import numpy as np

import python.Plot_RSTs.plot_RST_constants as consts
from python.utils.my_interp import my_interp


# This function returns the RST lat/lon array (if any)
# after interpolating the SLP data if needed.
# Currently, there are two algorithms for finding the RST:
# the first is by looking at points in a distance of 1.5 degress
# and the second tests each of the 5 neighboring points and goes
# for the higher found value. Use the "method" agument to activate each option.
def calculate_rst(slp_data, resolution, lats, lons, method=1):
    # These lines of code are used by both methods
    if consts.rst_resolution != resolution:
        # The data and the rst resolutions are different. Needs the interpolation for the find_trough function
        slp_data, lats, lons = my_interp(slp_data, lats, lons, consts.rst_resolution, consts.interpolation_method)
    lowest_lat = lats[0]
    lowest_lon = lons[0]
    multiplier = 1 / consts.rst_resolution
    indexed_rst_lat1 = int((consts.rst_lat1 - lowest_lat) * multiplier)
    indexed_rst_lat2 = int((consts.rst_lat2 - lowest_lat) * multiplier)
    indexed_rst_lon1 = int((consts.rst_lon1 - lowest_lon) * multiplier)
    indexed_rst_lon2 = int((consts.rst_lon2 - lowest_lon) * multiplier)
    total_lat = slp_data.shape[0]
    total_lon = slp_data.shape[1]

    # There can be multiple troughs found.
    # Each takes 2 columns in the trough matrix.
    # each trough has [x1, y1; x2, y2; etc.]
    troughs_counter = 0
    trough_coords_matrix = np.zeros((total_lat, consts.max_number_of_RST*2))

    if method == 1:
        slp_check_distance = 3  # grid points. 3 * 0.5 = 1.5 deg.
        next_point_search_distance = 5  # grid points. 5 * 0.5 = 2.5 deg.

        # Find the first point of the trough by comparing slp values to the ones at
        # a distance of +/- slp_check_distance.
        maximum_diff = 0
        last_found_point_lon = 0
        for current_lon in range(max(slp_check_distance, indexed_rst_lon1),
                                 min(total_lon - slp_check_distance, indexed_rst_lon2 + 1)):
            current_slp = slp_data[indexed_rst_lat1, current_lon]
            compared_slp_1 = slp_data[indexed_rst_lat1, current_lon - slp_check_distance]
            compared_slp_2 = slp_data[indexed_rst_lat1, current_lon + slp_check_distance]
            if (current_slp < compared_slp_1) and (current_slp < compared_slp_2):
                current_maxima = compared_slp_1 + compared_slp_2 - (2 * current_slp)
                if current_maxima > maximum_diff:
                    # Notice that currently only one trough is found in this method., so troughs_counter is always 0
                    trough_coords_matrix[0, troughs_counter:troughs_counter+2] = lats[indexed_rst_lat1], lons[current_lon]
                    last_found_point_lon = current_lon
                    maximum_diff = current_maxima

        # Find the following points, if a starting point was found.
        if trough_coords_matrix[0, 0] > 0:
            for current_lat in range(indexed_rst_lat1 + 1, indexed_rst_lat2 + 1):
                maximum_diff = 0
                for current_lon in range(int(max(last_found_point_lon - next_point_search_distance, slp_check_distance)),
                                         int(min(last_found_point_lon + next_point_search_distance, indexed_rst_lon2 + 1))):
                    current_slp = slp_data[current_lat, current_lon]
                    compared_slp_1 = slp_data[current_lat, current_lon - slp_check_distance]
                    compared_slp_2 = slp_data[current_lat, current_lon + slp_check_distance]
                    if (current_slp < compared_slp_1) and (current_slp < compared_slp_2):
                        current_maxima = compared_slp_1 + compared_slp_2 - (2 * current_slp)
                        if current_maxima > maximum_diff:
                            trough_coords_matrix[current_lat - indexed_rst_lat1, troughs_counter:troughs_counter+2] = lats[current_lat], lons[current_lon]
                            last_found_point_lon = current_lon
                            maximum_diff = current_maxima

                    if current_lat < total_lat:  # Check diagonaly.
                        compared_slp_1 = slp_data[current_lat + 1, current_lon - slp_check_distance]
                        compared_slp_2 = slp_data[current_lat - 1, current_lon + slp_check_distance]
                        if (current_slp < compared_slp_1) and (current_slp < compared_slp_2):
                            current_maxima = compared_slp_1 + compared_slp_2 - (2 * current_slp)
                            if current_maxima > maximum_diff:
                                trough_coords_matrix[current_lat - indexed_rst_lat1, troughs_counter:troughs_counter + 2] = lats[current_lat], lons[current_lon]
                                last_found_point_lon = current_lon
                                maximum_diff = current_maxima

                        compared_slp_1 = slp_data[current_lat - 1, current_lon - slp_check_distance]
                        compared_slp_2 = slp_data[current_lat + 1, current_lon + slp_check_distance]
                        if (current_slp < compared_slp_1) and (current_slp < compared_slp_2):
                            current_maxima = compared_slp_1 + compared_slp_2 - (2 * current_slp)
                            if current_maxima > maximum_diff:
                                trough_coords_matrix[current_lat - indexed_rst_lat1, troughs_counter:troughs_counter + 2] = lats[current_lat], lons[current_lon]
                                last_found_point_lon = current_lon
                                maximum_diff = current_maxima

                if maximum_diff == 0:
                    break

        return trough_coords_matrix
    elif method == 2:

        return trough_coords_matrix

