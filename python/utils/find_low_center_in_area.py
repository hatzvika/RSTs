import numpy as np


# find a low center and its depth in a given area
# NOTICE: The slp_data MUST BE LARGER than the searched area by AT LEAST the amount of both the supplied radii.
def find_low_center_in_area(slp_data,
                            lats,
                            lons,
                            resolution,
                            area_lat_low,
                            area_lat_high,
                            area_lon_low,
                            area_lon_high,
                            test_center_radius_km,
                            depth_radius_km):
    deg_lat_in_km = 110

    low_center_lat = None
    low_center_lon = None
    low_center_depth = 0
    lowest_value_in_one_direction = 0

    # Calculate the lat points of each radius (This doesn't change with latitude,
    # unlike the lon points which need to be calculated for each lat)
    test_center_radius_lat_grid_points = int(np.round((test_center_radius_km / deg_lat_in_km) / resolution))
    depth_radius_lat_grid_points = int(np.round((depth_radius_km / deg_lat_in_km) / resolution))

    # Find the indices of the area limits
    area_lat_low_index = int((area_lat_low - lats[0]) / resolution)
    area_lat_high_index = int((area_lat_high - lats[0]) / resolution)
    area_lon_low_index = int((area_lon_low - lons[0]) / resolution)
    area_lon_high_index = int((area_lon_high - lons[0]) / resolution)

    # Loop inside the searched area to find the low centers and pick the deeper one.
    for current_lat in range(area_lat_low_index, area_lat_high_index+1):
        distance_lat_modifier = np.cos(np.deg2rad(lats[current_lat]))
        test_center_radius_lon_grid_points = int(np.round((test_center_radius_km / deg_lat_in_km * distance_lat_modifier) / resolution))
        depth_radius_lon_grid_points = int(np.round((depth_radius_km / (deg_lat_in_km * distance_lat_modifier)) / resolution))
        for current_lon in range(area_lon_low_index, area_lon_high_index+1):
            center_point_slp = slp_data[current_lat, current_lon]
            north_point_slp = slp_data[current_lat + test_center_radius_lat_grid_points, current_lon]
            south_point_slp = slp_data[current_lat - test_center_radius_lat_grid_points, current_lon]
            east_point_slp = slp_data[current_lat, current_lon + test_center_radius_lon_grid_points]
            west_point_slp = slp_data[current_lat, current_lon - test_center_radius_lon_grid_points]

            # If the tested point has a lower slp than the four points around it, then it is a low center
            if (center_point_slp < north_point_slp) and (center_point_slp < south_point_slp) and (center_point_slp < east_point_slp) and (center_point_slp < west_point_slp):
                north_depth_point_slp = slp_data[current_lat + depth_radius_lat_grid_points, current_lon]
                south_depth_point_slp = slp_data[current_lat - depth_radius_lat_grid_points, current_lon]
                east_depth_point_slp = slp_data[current_lat, current_lon + depth_radius_lon_grid_points]
                west_depth_point_slp = slp_data[current_lat, current_lon - depth_radius_lon_grid_points]
                current_low_depth = (north_depth_point_slp + south_depth_point_slp + east_depth_point_slp + west_depth_point_slp) / 4 - center_point_slp
                if current_low_depth > low_center_depth:
                    low_center_depth = current_low_depth
                    low_center_lat = lats[current_lat]
                    low_center_lon = lons[current_lon]

                    northwest_depth_point_slp = slp_data[current_lat + depth_radius_lat_grid_points, current_lon - depth_radius_lon_grid_points]
                    northeast_depth_point_slp = slp_data[current_lat + depth_radius_lat_grid_points, current_lon + depth_radius_lon_grid_points]
                    southwest_depth_point_slp = slp_data[current_lat - depth_radius_lat_grid_points, current_lon - depth_radius_lon_grid_points]
                    southeast_depth_point_slp = slp_data[current_lat - depth_radius_lat_grid_points, current_lon + depth_radius_lon_grid_points]
                    lowest_value_in_one_direction = min(north_depth_point_slp, south_depth_point_slp,
                                                        east_depth_point_slp, west_depth_point_slp,
                                                        northwest_depth_point_slp, northeast_depth_point_slp,
                                                        southwest_depth_point_slp, southeast_depth_point_slp) - center_point_slp

    return low_center_lat, low_center_lon, low_center_depth, lowest_value_in_one_direction
