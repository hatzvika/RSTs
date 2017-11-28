import numpy as np

import python.Plot_RSTs.plot_RST_constants as consts
from python.utils.my_interp import my_interp


# This function returns the RST lat/lon array (if any)
# after interpolating the SLP data if needed.
# The method is looking at points in a distance of 1.5 degress
# trying to find if the middle point is the local minima

class Calculate_RST:
    def __init__(self, slp_data, resolution, slp_check_distance, lats, lons):
        # These lines of code are used by both methods
        if consts.rst_resolution != resolution:
            # The data and the rst resolutions are different. Needs the interpolation for the find_trough function
            self.slp_data, self.lats, self.lons = my_interp(slp_data, lats, lons, consts.rst_resolution, consts.interpolation_method)
        else:
            self.slp_data = slp_data
            self.lats = lats
            self.lons = lons

        lowest_lat = lats[0]
        lowest_lon = lons[0]
        multiplier = 1 / consts.rst_resolution
        self.indexed_rst_lat1 = int((consts.rst_lat1 - lowest_lat) * multiplier)
        self.indexed_rst_lat2 = int((consts.rst_lat2 - lowest_lat) * multiplier)
        self.indexed_rst_lon1 = int((consts.rst_lon1 - lowest_lon) * multiplier)
        self.indexed_rst_lon2 = int((consts.rst_lon2 - lowest_lon) * multiplier)
        self.total_lat = slp_data.shape[0]
        self.total_lon = slp_data.shape[1]

        # The following test matrix holds the 4 pairs of locations with which the algorithm tests for local minima.
        # Each row holds the values of [lat_diff1, lon_diff1, lat_diff2, lon_diff2] which are added to the lat and lot of the tested point.
        # It looks like that :    3
        #                       4   2
        #                      1  *  1
        #                       2   4
        #                         3
        # The * marks the tested location for slp minima and the numbers are the matrix rows
        slp_check_distance_diagonal = int(np.round(slp_check_distance / np.sqrt(2)))
        self.test_matrix = [[0, slp_check_distance, 0, -slp_check_distance],
                            [slp_check_distance_diagonal, slp_check_distance_diagonal, -slp_check_distance_diagonal, -slp_check_distance_diagonal],
                            [slp_check_distance, 0, -slp_check_distance, 0],
                            [-slp_check_distance_diagonal, slp_check_distance_diagonal, slp_check_distance_diagonal, -slp_check_distance_diagonal]]
        self.slp_check_distance = slp_check_distance

        # similiarly to self.test_matrix, self.neighbors_matrix is mapping the
        # next available grid points indices in relation to the last point found in the trough so far
        self.neighbors_matrix = [[0, -1],   # Left
                                 [1, -1],   # Upper left
                                 [1, 0],    # Upper
                                 [1,1],     # Upper right
                                 [0,1]]     # Right

        # There can be multiple troughs found.
        # Each takes 2 columns in the trough matrix.
        # each trough has [[x1, y1], [x2, y2], ..., [xn,yn]]
        self.troughs_counter = 0
        self.trough_coords_matrix = np.zeros((self.total_lat*3, consts.max_number_of_RST*2)) # *3 because the algorithm allows goind sideways as well.
        self._find_all_rsts()

    def get_trough_coords_matrix(self, longest_only=False):
        if longest_only:
            longest = 0
            longest_matrix = []
            for current_RST in range(self.troughs_counter):
                # Get the current trough columns from the trough matrix
                trough_coords = self.trough_coords_matrix[:, 2*current_RST:2*current_RST+2]
                # remove all zeros from current RST
                trough_coords = trough_coords[~(trough_coords == 0).all(1)]
                if np.size(trough_coords, 0) > longest:
                    longest = np.size(trough_coords, 0)
                    longest_matrix = trough_coords
            self.trough_coords_matrix = longest_matrix

        return self.trough_coords_matrix

    def _find_all_rsts(self):
        # Find the first point of the trough by comparing slp values to the ones at
        # a distance of +/- self.test_matrix.
        for current_lat_index in range(self.indexed_rst_lat1, self.indexed_rst_lat1 + consts.num_of_RST_start_lats):
            for current_lon_index in range(max(self.slp_check_distance, self.indexed_rst_lon1),
                                           min(self.total_lon - self.slp_check_distance, self.indexed_rst_lon2 + 1)):
                current_slp = self.slp_data[current_lat_index, current_lon_index]
                for current_compare in range(np.size(self.test_matrix, 0)):
                    compared_slp_1 = self.slp_data[current_lat_index + self.test_matrix[current_compare][0],
                                                   current_lon_index + self.test_matrix[current_compare][1]]
                    compared_slp_2 = self.slp_data[current_lat_index + self.test_matrix[current_compare][2],
                                                   current_lon_index + self.test_matrix[current_compare][3]]
                    if (current_slp < compared_slp_1) and (current_slp < compared_slp_2):
                        # This point has lower SLP value than its neighbors as decided by the test_matrix
                        # First check if it is part of another trough which started in a lower latitude
                        current_lon_degrees = self.lons[current_lon_index]
                        current_lat_degrees = self.lats[current_lat_index]
                        is_new_trough = True
                        for tested_RST in range(self.troughs_counter):
                            for current_point in range(np.size(self.trough_coords_matrix, 0)):
                                if (current_lon_degrees == self.trough_coords_matrix[current_point, 2*tested_RST+1]) and \
                                        (current_lat_degrees == self.trough_coords_matrix[current_point, 2 * tested_RST]):
                                    is_new_trough = False
                                    break
                        if is_new_trough:
                            # Mark the start of the RST
                            self.trough_coords_matrix[0, 2 * self.troughs_counter:2 * self.troughs_counter + 2] = self.lats[current_lat_index], current_lon_degrees
                            self._calaculate_trough_for_a_starting_point(current_lat_index, current_lon_index)
                            self.troughs_counter = self.troughs_counter + 1

    def _calaculate_trough_for_a_starting_point(self, current_lat_index, current_lon_index):
        # points_in_trough_counter starts as one because there is already one point in the trough
        points_in_trough_counter = 1

        next_neighbor_lat = None
        next_neighbor_lon = None
        trough_end = False
        while not trough_end:
            trough_end = True

            # For ensuring the slp value is rising and avoiding going through saddles
            last_found_slp = self.slp_data[current_lat_index, current_lon_index]

            # We look for the neighbor with the maximal difference from its neighbors
            maximum_diff = 0

            for current_neighbor in range(np.size(self.neighbors_matrix, 0)):
                current_neighbor_lat = current_lat_index + self.neighbors_matrix[current_neighbor][0]
                current_neighbor_lon = current_lon_index + self.neighbors_matrix[current_neighbor][1]
                current_neighbor_slp = self.slp_data[current_neighbor_lat, current_neighbor_lon]
                # Check if slp value is indeed rising
                if current_neighbor_slp > last_found_slp:
                    for current_compare in range(np.size(self.test_matrix, 0)):
                        compared_slp_1 = self.slp_data[current_neighbor_lat + self.test_matrix[current_compare][0],
                                                       current_neighbor_lon + self.test_matrix[current_compare][1]]
                        compared_slp_2 = self.slp_data[current_neighbor_lat + self.test_matrix[current_compare][2],
                                                       current_neighbor_lon + self.test_matrix[current_compare][3]]
                        current_maxima = compared_slp_1 + compared_slp_2 - (2 * current_neighbor_slp)
                        if (current_neighbor_slp < compared_slp_1) and (current_neighbor_slp < compared_slp_2) and (current_maxima > maximum_diff):
                            trough_end = False
                            maximum_diff = current_maxima
                            self.trough_coords_matrix[points_in_trough_counter, 2 * self.troughs_counter:2 * self.troughs_counter + 2] = \
                                self.lats[current_neighbor_lat],self.lons[current_neighbor_lon]
                            next_neighbor_lat = current_neighbor_lat
                            next_neighbor_lon = current_neighbor_lon
            current_lat_index = next_neighbor_lat
            current_lon_index = next_neighbor_lon
            points_in_trough_counter = points_in_trough_counter +1

            # Check if we reached the edges of our search area or map
            # if (current_lat_index is not None):
            #     if (current_lat_index == max(self.slp_check_distance, self.indexed_rst_lat1)) or \
            #             (current_lat_index == min(self.total_lat - self.slp_check_distance, self.indexed_rst_lat2 + 1)) or \
            #             (current_lon_index == max(self.slp_check_distance, self.indexed_rst_lon1)) or \
            #             (current_lon_index == min(self.total_lon - self.slp_check_distance, self.indexed_rst_lon2 + 1)):
            #         trough_end = True
