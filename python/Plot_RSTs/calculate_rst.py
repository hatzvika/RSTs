import numpy as np

import python.Plot_RSTs.plot_RST_constants as consts
from python.utils.my_interp import my_interp


# This function returns the RST lat/lon array (if any)
# after interpolating the SLP data if needed.
# Currently, there are two algorithms for finding the RST:
# the first is by looking at points in a distance of 1.5 degress
# and the second tests each of the 5 neighboring points and goes
# for the higher found value. Use the "method" agument to activate each option.
def calculate_rst(slp_data, resolution, lats, lons):
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
    trough_coords_matrix = np.zeros((total_lat*3, consts.max_number_of_RST*2)) # *3 because the second method allows goind sideways as well.

    # slp_check_distance = 3  # grid points. 3 * 0.5 = 1.5 deg.
    slp_check_distance = 1  # grid points. 3 * 0.5 = 1.5 deg.
    next_point_search_distance = 5  # grid points. 5 * 0.5 = 2.5 deg.

    # Find the first point of the trough by comparing slp values to the ones at
    # a distance of +/- slp_check_distance.
    last_found_slp = 0
    for start_lat in range(indexed_rst_lat1, indexed_rst_lat1 + consts.num_of_RST_start_lats):
        for current_lon_index in range(max(slp_check_distance, indexed_rst_lon1),
                                       min(total_lon - slp_check_distance, indexed_rst_lon2 + 1)):
            current_slp = slp_data[start_lat, current_lon_index]
            compared_slp_1 = slp_data[start_lat, current_lon_index - slp_check_distance]
            compared_slp_2 = slp_data[start_lat, current_lon_index + slp_check_distance]
            if (current_slp < compared_slp_1) and (current_slp < compared_slp_2):
                # This point has lower SLP value than its neighbors on the left and right
                # First check if it is part of another trough which started in a lower latitude
                current_lon_degrees = lons[current_lon_index]
                is_new_trough = True
                if start_lat > indexed_rst_lat1:
                    for tested_RST in range(troughs_counter):
                        if current_lon_degrees == trough_coords_matrix[start_lat - indexed_rst_lat1, 2*tested_RST+1]:
                            is_new_trough = False
                            break

                if is_new_trough:
                    # Mark the start of the RST
                    trough_coords_matrix[0, 2 * troughs_counter:2 * troughs_counter + 2] = lats[start_lat], current_lon_degrees
                    last_found_point_lon = current_lon_index

                    # Continue finding the rest of the RST that was just found
                    # Find the following points, if a starting point was found.
                    for current_lat_index in range(start_lat + 1, indexed_rst_lat2 + 1):
                        maximum_diff = 0
                        next_last_slp = 0
                        for current_lon_index in range(int(max(last_found_point_lon - next_point_search_distance, slp_check_distance)),
                                                       int(min(last_found_point_lon + next_point_search_distance, indexed_rst_lon2 + 1))):
                            current_slp = slp_data[current_lat_index, current_lon_index]
                            compared_slp_1 = slp_data[current_lat_index, current_lon_index - slp_check_distance]
                            compared_slp_2 = slp_data[current_lat_index, current_lon_index + slp_check_distance]
                            if (current_slp < compared_slp_1) and (current_slp < compared_slp_2) and (current_slp > last_found_slp):
                                current_maxima = compared_slp_1 + compared_slp_2 - (2 * current_slp)
                                if current_maxima > maximum_diff:
                                    trough_coords_matrix[current_lat_index - indexed_rst_lat1, 2*troughs_counter:2*troughs_counter+2] = lats[current_lat_index], lons[current_lon_index]
                                    last_found_point_lon = current_lon_index
                                    maximum_diff = current_maxima
                                    next_last_slp = current_slp

                            if current_lat_index < total_lat:  # Check diagonaly.
                                compared_slp_1 = slp_data[current_lat_index + 1, current_lon_index - slp_check_distance]
                                compared_slp_2 = slp_data[current_lat_index - 1, current_lon_index + slp_check_distance]
                                if (current_slp < compared_slp_1) and (current_slp < compared_slp_2) and (current_slp > last_found_slp):
                                    current_maxima = compared_slp_1 + compared_slp_2 - (2 * current_slp)
                                    if current_maxima > maximum_diff:
                                        trough_coords_matrix[current_lat_index - indexed_rst_lat1, 2*troughs_counter:2*troughs_counter + 2] = lats[current_lat_index], lons[current_lon_index]
                                        last_found_point_lon = current_lon_index
                                        maximum_diff = current_maxima
                                        next_last_slp = current_slp

                                compared_slp_1 = slp_data[current_lat_index - 1, current_lon_index - slp_check_distance]
                                compared_slp_2 = slp_data[current_lat_index + 1, current_lon_index + slp_check_distance]
                                if (current_slp < compared_slp_1) and (current_slp < compared_slp_2) and (current_slp > last_found_slp):
                                    current_maxima = compared_slp_1 + compared_slp_2 - (2 * current_slp)
                                    if current_maxima > maximum_diff:
                                        trough_coords_matrix[current_lat_index - indexed_rst_lat1, 2*troughs_counter:2*troughs_counter + 2] = lats[current_lat_index], lons[current_lon_index]
                                        last_found_point_lon = current_lon_index
                                        maximum_diff = current_maxima
                                        next_last_slp = current_slp

                        last_found_slp = next_last_slp
                        if maximum_diff == 0:
                            break

                    troughs_counter = troughs_counter + 1

    return trough_coords_matrix
