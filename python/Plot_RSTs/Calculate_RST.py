import numpy as np

import python.Plot_RSTs.plot_RST_constants as consts
from python.utils.my_interp import my_interp
from python.utils.find_low_center_in_area import find_low_center_in_area
from python.utils.calculate_distance_between_two_points_on_earth import calculate_distance_between_two_points_on_earth

# This function returns the RST lat/lon array (if any) of the given day
# after interpolating the SLP data if needed.
# The method is looking at points in a distance of 1.5 degress
# trying to find if the middle point is the local minima


# IMPORTANT: the geostrophic_vorticity_map and slp_data MUST have the same resolution and size!
class Calculate_RST:
    def __init__(self, slp_data, geostrophic_vorticity_map, resolution, slp_check_distance, lats, lons):
        # These lines of code are used by both methods
        if consts.rst_resolution != resolution:
            # The data and the rst resolutions are different. Needs the interpolation for the find_trough function
            self.slp_data, self.lats, self.lons = my_interp(slp_data, lats, lons, consts.rst_resolution, consts.interpolation_method)
            self.geostrophic_vorticity_map, _, _ = my_interp(geostrophic_vorticity_map, lats, lons, consts.rst_resolution, consts.interpolation_method)
        else:
            self.slp_data = slp_data
            self.geostrophic_vorticity_map = geostrophic_vorticity_map
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
                                 # [0, -2],  # Far left
                                 # [1, -2],  #
                                 # [2, -2],  # Far upper left
                                 # [2, -1],  #
                                 # [2, 0],  # Far upper
                                 # [2, 1],  #
                                 # [2, 2],  # Far upper right
                                 # [1, 2],  #
                                 # [0, 2]]  # Far right

        # There can be multiple troughs found.
        # Each takes 2 columns in the trough matrix.
        # each trough has [[x1, y1], [x2, y2], ..., [xn,yn]]
        self.troughs_counter = 0
        self.trough_coords_matrix = np.zeros((self.total_lat*3, consts.max_number_of_RST*2)) # *3 because the algorithm allows goind sideways as well.

        # This will be the final decision about the rst classification of the day (unless rst conditions are not met)
        self.daily_rst_classification = consts.rst_orientation_no_rst

        self._find_all_rsts()

    def get_trough_coords_matrix(self, only_long_separate_RSTs=False, polyfit_rst=True):
        rst_orientation_str = ""
        if only_long_separate_RSTs:
            # Get all RSTs which are longer than a threshold. If none found, get the longest possible.
            longest = 0
            longest_matrix = []
            long_RSTs_counter = 0
            long_RSTs_matrix = np.zeros((self.total_lat*3, consts.max_number_of_RST*2))
            for current_RST in range(self.troughs_counter):
                # Get the current trough columns from the trough matrix
                trough_coords = self.trough_coords_matrix[:, 2*current_RST:2*current_RST+2]
                # remove all zeros from current RST
                trough_coords = trough_coords[~(trough_coords == 0).all(1)]
                trough_length = np.size(trough_coords, 0)
                if trough_length > longest:
                    longest = trough_length
                    longest_matrix = trough_coords
                if trough_length >= consts.RST_length_threshold:
                    long_RSTs_matrix[0:trough_length, long_RSTs_counter*2:long_RSTs_counter*2+2] = trough_coords
                    long_RSTs_counter = long_RSTs_counter + 1
            if long_RSTs_counter == 0:
                self.trough_coords_matrix = longest_matrix
            else:
                self.trough_coords_matrix = long_RSTs_matrix[:, 0:long_RSTs_counter*2]
                self._leave_only_separate_troughs()

        rst_orientation_str = self._polyfit_rsts_and_find_orientations(polyfit_rst)

        return self.trough_coords_matrix, rst_orientation_str, self.daily_rst_classification

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
                if (current_neighbor_lat < self.total_lat) and (current_neighbor_lat >= 0) and (current_neighbor_lon < self.total_lon) and (current_neighbor_lon >= 0):
                    current_neighbor_slp = self.slp_data[current_neighbor_lat, current_neighbor_lon]
                    # Check if slp value is indeed rising
                    if current_neighbor_slp > last_found_slp:
                        for current_compare in range(np.size(self.test_matrix, 0)):
                            compared_slp_1_lat = current_neighbor_lat + self.test_matrix[current_compare][0]
                            compared_slp_1_lon = current_neighbor_lon + self.test_matrix[current_compare][1]
                            compared_slp_2_lat = current_neighbor_lat + self.test_matrix[current_compare][2]
                            compared_slp_2_lon = current_neighbor_lon + self.test_matrix[current_compare][3]

                            if (compared_slp_1_lat < self.total_lat) and (compared_slp_1_lat >= 0) \
                                and (compared_slp_1_lon < self.total_lon) and (compared_slp_1_lon >= 0) \
                                and (compared_slp_2_lat < self.total_lat) and (compared_slp_2_lat >= 0) \
                                and (compared_slp_2_lon < self.total_lon) and (compared_slp_2_lon >= 0):

                                compared_slp_1 = self.slp_data[compared_slp_1_lat, compared_slp_1_lon]
                                compared_slp_2 = self.slp_data[compared_slp_2_lat, compared_slp_2_lon]
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

    def _leave_only_separate_troughs(self):
        # This function removes converging troughs, leaving only the longest troughs.
        current_valid_troughs_counter = 0
        while (2 * current_valid_troughs_counter) < np.size(self.trough_coords_matrix, 1):
            # Get tested trough
            tested_trough = self.trough_coords_matrix[:, current_valid_troughs_counter*2:current_valid_troughs_counter*2+2]
            # remove all zeros from tested trough
            tested_trough = tested_trough[~(tested_trough == 0).all(1)]
            other_trough_index = current_valid_troughs_counter + 1

            # Initialize the additive longitude values arrays
            # This array concatenates every overlapping RST, and is sorted in the end to find the low and high values in each latitude.
            # It is done this way because it is fast and because there could be multiple values for each latitude in a single RST.
            additive_current_valid_trough = tested_trough

            while (2 * other_trough_index) < np.size(self.trough_coords_matrix, 1):
                other_trough = self.trough_coords_matrix[:, other_trough_index*2:other_trough_index*2+2]
                # remove all zeros from other trough
                other_trough = other_trough[~(other_trough == 0).all(1)]

                # Compare tested and other troughs
                is_different = True
                tested_trough_length = np.size(tested_trough,0)
                other_trough_length = np.size(other_trough,0)
                for tested_point_index in range(tested_trough_length):
                    tested_point_lat = tested_trough[tested_point_index, 0]
                    tested_point_lon = tested_trough[tested_point_index, 1]
                    for other_point_index in range (other_trough_length):
                        other_point_lat = other_trough[other_point_index, 0]
                        other_point_lon = other_trough[other_point_index, 1]
                        if (tested_point_lat == other_point_lat) and (tested_point_lon == other_point_lon):
                            is_different = False
                            break
                    if not is_different:
                        break

                if not is_different:
                    # Add the current other_trough to the additive_current_valid_trough
                    additive_current_valid_trough = np.concatenate((additive_current_valid_trough, other_trough), axis=0)

                    if other_trough_length > tested_trough_length:
                        tested_trough = other_trough

                        self.trough_coords_matrix[:, current_valid_troughs_counter * 2:current_valid_troughs_counter * 2 + 2] = \
                            self.trough_coords_matrix[:, other_trough_index * 2:other_trough_index * 2 + 2]
                    # elif other_trough_length == tested_trough_length:
                    #     multiplier = 1 / consts.rst_resolution
                    #     tested_starting_lat_index = int(tested_trough[0,0] * multiplier)
                    #     tested_starting_lon_index = int(tested_trough[0,1] * multiplier)
                    #     other_starting_lat_index = int(other_trough[0,0] * multiplier)
                    #     other_starting_lon_index = int(other_trough[0,1] * multiplier)
                    #     tested_starting_slp = self.slp_data[tested_starting_lat_index, tested_starting_lon_index]
                    #     other_starting_slp = self.slp_data[other_starting_lat_index, other_starting_lon_index]
                    #     if other_starting_slp < tested_starting_slp:
                    #         self.trough_coords_matrix[current_valid_troughs_counter * 2, current_valid_troughs_counter * 2 + 1] = \
                    #             self.trough_coords_matrix[other_trough_index * 2, other_trough_index * 2 + 1]

                    self.trough_coords_matrix = np.delete(self.trough_coords_matrix, other_trough_index * 2 + 1, 1)
                    self.trough_coords_matrix = np.delete(self.trough_coords_matrix, other_trough_index * 2, 1)
                else:
                    other_trough_index = other_trough_index + 1

            # Put the average of same latitudes in the concatenated additive_current_valid_trough back in the trough_coords_matrix
            # First sort the results by lat and lon
            additive_current_valid_trough = additive_current_valid_trough[additive_current_valid_trough[:, 1].argsort()]
            additive_current_valid_trough = additive_current_valid_trough[additive_current_valid_trough[:, 0].argsort(kind='mergesort')]

            # Now find the min and max for each lat
            last_lat = additive_current_valid_trough[0, 0]
            lowest_lons = np.zeros((np.size(self.trough_coords_matrix, 0), 2))
            lowest_lons[0, :] = additive_current_valid_trough[0]
            highest_lons = np.zeros((np.size(self.trough_coords_matrix, 0), 2))
            points_counter = 0
            for current_lat_index in range(np.size(additive_current_valid_trough,0)):
                current_lat = additive_current_valid_trough[current_lat_index, 0]
                if (current_lat > last_lat) and (current_lat_index != 0): # Going to next lat. Record the lowest lon.
                    highest_lons[points_counter, :] = additive_current_valid_trough[current_lat_index-1, :]
                    points_counter = points_counter + 1
                    lowest_lons[points_counter, :] = additive_current_valid_trough[current_lat_index, :]
                    last_lat = current_lat
            highest_lons[points_counter, :] = additive_current_valid_trough[-1, :]

            # Average the min and max for each lat and create the average_trough
            average_trough = np.zeros((np.size(self.trough_coords_matrix, 0), 2))
            average_trough[:,0] = lowest_lons[:,0]
            average_trough[:,1] = (lowest_lons[:,1] + highest_lons[:,1])/2

            # Insert the average_trough back in the trough_coords_matrix
            self.trough_coords_matrix[:, current_valid_troughs_counter * 2:current_valid_troughs_counter * 2 + 2] = average_trough

            current_valid_troughs_counter = current_valid_troughs_counter + 1

    def _polyfit_rsts_and_find_orientations(self, polyfit_rst):
        self.daily_rst_classification = consts.rst_orientation_no_rst
        daily_class_trough_num = None
        rst_orientation_str = ""
        if len(self.trough_coords_matrix) != 0:
            num_of_rsts = int(np.size(self.trough_coords_matrix, 1) / 2)
        else:
            num_of_rsts = 0
        temp_coordinates_matrix = np.zeros((1000, 2*num_of_rsts))

        for current_RST in range(0, num_of_rsts):
            # Get the current trough columns from the trough matrix
            trough_coords = self.trough_coords_matrix[:, 2 * current_RST:2 * current_RST + 2]
            # remove all zeros from current RST
            trough_coords = trough_coords[~(trough_coords == 0).all(1)]
            x_trough = trough_coords[:, 1]
            y_trough = trough_coords[:, 0]

            # Find the orientation of the RST
            current_rst_orientation_str = self._Check_RST_orientation(x_trough, y_trough)

            # Check if it is a better choice for this day's classification result (only when it is not "No_RST")
            if current_rst_orientation_str != consts.rst_orientation_no_rst:
                change_rst_orintation = False
                if self.daily_rst_classification == consts.rst_orientation_no_rst:
                    # This is the first rst which has an orientation
                    change_rst_orintation = True
                else: # Start comparing the current daily RST and the competing trough
                    current_daily_trough = self.trough_coords_matrix[:,2*daily_class_trough_num:2*daily_class_trough_num+2]
                    current_daily_trough = current_daily_trough[~(current_daily_trough == 0).all(1)]
                    current_daily_GV_score = self._calculate_GV_score(current_daily_trough)
                    trough_coords_score = self._calculate_GV_score(trough_coords)
                    if (trough_coords_score > current_daily_GV_score):
                        change_rst_orintation = True

                if change_rst_orintation:
                    self.daily_rst_classification = current_rst_orientation_str
                    daily_class_trough_num = current_RST

                # First check in the East
                low_center_lat, low_center_lon, low_center_depth, depth_in_one_dir = find_low_center_in_area(self.slp_data, self.lats,
                                                                                                             self.lons,
                                                                                                             consts.interp_resolution, 30,
                                                                                                             35, 35, 42.5,
                                                                                                             110, 300)
                print(low_center_depth, depth_in_one_dir)
                if low_center_lat is not None:
                    if low_center_depth > 160 and depth_in_one_dir > 75:
                        self.daily_rst_classification = consts.rst_orientation_no_rst

                # Then check in the West
                low_center_lat, low_center_lon, low_center_depth, depth_in_one_dir = find_low_center_in_area(self.slp_data, self.lats,
                                                                                                             self.lons,
                                                                                                             consts.interp_resolution, 25,
                                                                                                             32.5, 25,
                                                                                                             35, 110, 300)
                print(low_center_depth, depth_in_one_dir)
                if low_center_lat is not None:
                    if low_center_depth > 160 and depth_in_one_dir > 75:
                        self.daily_rst_classification = consts.rst_orientation_no_rst

                # # Before the geostrpohic vorticity change:
                # if (self.daily_rst_classification != consts.rst_orientation_no_rst) and (self.daily_rst_classification != current_rst_orientation_str) and (current_rst_orientation_str != consts.rst_orientation_no_rst):
                #     print("Different classifications for this date")
                # if (self.daily_rst_classification == consts.rst_orientation_no_rst) or (np.max(y_trough) >= np.max(self.trough_coords_matrix[:,2*daily_class_trough_num])):
                #     # This is the first rst which has an orientation or a later rst has an orientation and is has a higher lat value
                #     self.daily_rst_classification = current_rst_orientation_str
                #     daily_class_trough_num = current_RST

            rst_orientation_str = rst_orientation_str + current_rst_orientation_str + ", "

            # Smooth the RST for display purposes
            if polyfit_rst:
                try:
                    z = np.polyfit(y_trough, x_trough, 3)  # I invert the x and y because of the trough shape from south to north
                    p = np.poly1d(z)
                    latp = np.linspace(y_trough[0], y_trough[-1], 100)
                    x_trough = p(latp)
                    y_trough = latp
                except:
                    print("can't polyfit")


            # Return the polyfitted trough to the trough coords matrix
            temp_coordinates_matrix[0:np.size(y_trough,0), 2 * current_RST] = y_trough
            temp_coordinates_matrix[0:np.size(x_trough,0), 2 * current_RST + 1] = x_trough

        self.trough_coords_matrix = temp_coordinates_matrix

        if rst_orientation_str != "":
            rst_orientation_str = rst_orientation_str[:-2]

        return rst_orientation_str

    def _Check_RST_orientation(self, x_trough, y_trough):
        east = False
        west = False
        for current_index in range(np.size(x_trough, 0)):
            current_lat = y_trough[current_index]
            current_lon = x_trough[current_index]
            if current_lat >= consts.central_cross_line_lat1 and current_lat <= consts.rst_square3_lat2:
                if current_lon >= consts.rst_square3_lon1 and current_lon <= consts.central_cross_line_lon:
                    west = True
                if current_lon >= consts.central_cross_line_lon and current_lon <= consts.rst_square3_lon2:
                    east = True
        #if (west or east) and (y_trough[0] > 30):
        #    return consts.rst_orientation_testing
        if west and east:
            return consts.rst_orientation_central
        elif east:
            return consts.rst_orientation_east
        elif west:
            return consts.rst_orientation_west
        else:
            return consts.rst_orientation_no_rst

    # This function calculates the total geostrophic vorticity across the trough.
    # This way length and depth are both taken into account.
    def _calculate_GV_score(self, scored_trough):
        total_GV = 0
        multiplier = 1/consts.interp_resolution
        for current_point in range(np.size(scored_trough, 0)):
            current_lat = scored_trough[current_point, 0]
            indexed_lat = int((current_lat - self.lats[0]) * multiplier)

            current_lon = scored_trough[current_point, 1]
            current_lon_rounded_to_nearest_grid_point = round(current_lon * multiplier) / multiplier
            indexed_rounded_lon = int((current_lon_rounded_to_nearest_grid_point - self.lons[0]) * multiplier)

            current_GV_value = self.geostrophic_vorticity_map[indexed_lat, indexed_rounded_lon]
            total_GV = total_GV + current_GV_value

        return total_GV


