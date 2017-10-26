import numpy as np

# This function receives a matrix of SLP values with a resolution of 0.5
# degrees, and returns a trough starting from the bottom and going up.


def find_trough(slp_matrix):
    slp_check_distance = 3 # grid points. 3 * 0.5 = 1.5 deg.
    next_point_search_distance = 5 # grid points. 5 * 0.5 = 2.5 deg.
    total_lat = slp_matrix.shape[0]
    total_lon = slp_matrix.shape[1]
    trough_coords = np.zeros(total_lat) # [x1, y1; x2, y2; etc.]

    # Find the first point of the trough
    maximum_diff = 0
    for current_lon in range(slp_check_distance, total_lon - slp_check_distance):
        current_slp = slp_matrix[0, current_lon]
        compared_slp_1 = slp_matrix[0, current_lon - slp_check_distance]
        compared_slp_2 = slp_matrix[0, current_lon + slp_check_distance]
        if (current_slp < compared_slp_1) and (current_slp < compared_slp_2):
            current_maxima = compared_slp_1 + compared_slp_2 - (2 * current_slp)
            if current_maxima > maximum_diff:
                trough_coords[0] = current_lon
                maximum_diff = current_maxima

    # Find the following points, if a starting point was found.
    if trough_coords[0] > 0:
        for current_lat in range(1, total_lat-1):
            maximum_diff = 0
            for current_lon in range(int(max(trough_coords[current_lat - 1] - next_point_search_distance, slp_check_distance+1)),
                                     int(min(trough_coords[current_lat - 1] + next_point_search_distance, total_lon - slp_check_distance))):
                current_slp = slp_matrix[current_lat, current_lon]
                compared_slp_1 = slp_matrix[current_lat, current_lon - slp_check_distance]
                compared_slp_2 = slp_matrix[current_lat, current_lon + slp_check_distance]
                if (current_slp < compared_slp_1) and (current_slp < compared_slp_2):
                    current_maxima = compared_slp_1 + compared_slp_2 - (2 * current_slp)
                    if current_maxima > maximum_diff:
                        trough_coords[current_lat] = current_lon
                        maximum_diff = current_maxima

                if current_lat < total_lat: # Check diagonaly.
                    compared_slp_1 = slp_matrix[current_lat + 1, current_lon - slp_check_distance]
                    compared_slp_2 = slp_matrix[current_lat - 1, current_lon + slp_check_distance]
                    if (current_slp < compared_slp_1) and (current_slp < compared_slp_2):
                        current_maxima = compared_slp_1 + compared_slp_2 - (2 * current_slp)
                        if current_maxima > maximum_diff:
                            trough_coords[current_lat] = current_lon
                            maximum_diff = current_maxima

                compared_slp_1 = slp_matrix[current_lat - 1, current_lon - slp_check_distance]
                compared_slp_2 = slp_matrix[current_lat + 1, current_lon + slp_check_distance]
                if (current_slp < compared_slp_1) and (current_slp < compared_slp_2):
                    current_maxima = compared_slp_1 + compared_slp_2 - (2 * current_slp)
                    if current_maxima > maximum_diff:
                        trough_coords[current_lat] = current_lon
                        maximum_diff = current_maxima

            if maximum_diff == 0:
                break

    if not all(trough_coords):
        trough_coords = trough_coords[trough_coords > 0]

    return trough_coords
