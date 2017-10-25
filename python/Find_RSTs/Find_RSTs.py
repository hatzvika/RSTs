import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from netCDF4 import Dataset, num2date
from mpl_toolkits import basemap


def main():
    use_interpolation = 1
    show_vorticity = 0
    show_geostrophic_vorticity = 1
    show_dots = 0
    show_rst_info = 1
    # For the interpolation - order	0 for nearest-neighbor interpolation, 1 for bilinear interpolation, 3 for cublic spline (default 1). order=3 requires scipy.ndimage.
    interpolation_method = 3
    save_maps = 1
    display_maps = 1

    lat1 = 25
    lat2 = 45
    lon1 = 25
    lon2 = 45
    rst_lat1 = 27.5
    rst_lat2 = 32.5
    rst_lon1 = 32.5
    rst_lon2 = 42.5
    rst_square1_lat1 = 27
    rst_square1_lat2 = 31
    rst_square1_lon1 = 33
    rst_square1_lon2 = 37
    rst_square2_lat1 = 31
    rst_square2_lat2 = 35
    rst_square2_lon1 = 33
    rst_square2_lon2 = 37
    rst_square3_lat1 = 29
    rst_square3_lat2 = 33
    rst_square3_lon1 = 34
    rst_square3_lon2 = 36

    # processed_data_prefix = 'C:\Users\Tzvika\Documents\Geography\Dry_Spells\Processed_data\';
    raw_data_prefix = "C:/Users/hatzv/Documents/Geography/Research_help/Pinhas synoptic classification/New_classification_algorithm/Raw_data/"

    slp_filename = raw_data_prefix + "SLP/SLP_NCEP_20-50N_20-50E_full_1985.nc"
    slp_nc = Dataset(slp_filename)
    slp_data = np.flip(np.squeeze(slp_nc.variables['slp'][2:-1:4, :, :]), 1) # Take only the 12Z data
    slp_lats = np.flip(slp_nc.variables['lat'][:], 0)  # flipping because nc files come with descending lats
    slp_lons = slp_nc.variables['lon'][:]
    slp_time = slp_nc.variables['time']
    total_days = slp_data.shape[0]
    data_resolution = slp_lats[1] - slp_lats[0]

    if show_vorticity == 1:
        uwind_filename = raw_data_prefix + "/uwind/uwind_850hPa_NCEP_22.5-47.5N_22.5-47.5E_May_1985.nc"
        uwind_nc = Dataset(uwind_filename)
        uwind_data = np.flip(np.squeeze(uwind_nc.variables['uwnd'][2:-1:4, :, :]), 1) # Take only the 12Z data
        vwind_filename = raw_data_prefix + "/vwind/vwind_850hPa_NCEP_22.5-47.5N_22.5-47.5E_May_1985.nc"
        vwind_nc = Dataset(vwind_filename)
        vwind_data = np.flip(np.squeeze(vwind_nc.variables['vwnd'][2:-1:4, :, :]), 1) # Take only the 12Z data

    # Interpolation of the data
    total_lat = slp_lats.shape[0]
    total_lon = slp_lons.shape[0]

    interp_resolution = 0.5  # This is the interpolated resolution(degrees) we aim for
    if use_interpolation == 1:
        [x_dense, y_dense] = np.meshgrid(np.arange(slp_lons[0], slp_lons[-1]+interp_resolution, interp_resolution),
                                         np.arange(slp_lats[0], slp_lats[-1]+interp_resolution, interp_resolution))
        temp_slp_data = np.zeros((total_days, x_dense.shape[0], y_dense.shape[0]))

        for current_day in range(total_days):
            temp_slp_data[current_day, :, :] = basemap.interp(np.squeeze(slp_data[current_day,:,:]),
                                                              slp_lons,
                                                              slp_lats,
                                                              x_dense,
                                                              y_dense,
                                                              order=interpolation_method)

        slp_data = temp_slp_data
        # Update total_lat and total and slp_lats, slp_lons
        total_lat = slp_data.shape[1]
        total_lon = slp_data.shape[2]
        slp_lats = np.arange(slp_lats[0], slp_lats[-1]+interp_resolution, interp_resolution)
        slp_lons = np.arange(slp_lons[0], slp_lons[-1]+interp_resolution, interp_resolution)

    map_counter = 0
    is_rst_vector = np.zeros(total_days)
    # for current_day in range(62,93):
    for current_day in range(total_days):
        troughs_map = np.zeros((total_lat, total_lon))
        ridges_map = np.zeros((total_lat, total_lon))
        map_counter = map_counter + 1

        for current_lat in range(total_lat - 1):
            for current_lon in range(total_lon - 1):
                current_slp_value = slp_data[current_day, current_lat, current_lon]

                # Check for troughs and ridges on the lat axis
                if (current_lat > 1) and (current_lat < total_lat):
                    slp_value_1 = slp_data[current_day, current_lat - 1, current_lon]
                    slp_value_2 = slp_data[current_day, current_lat + 1, current_lon]
                    if (current_slp_value < slp_value_1) and (current_slp_value < slp_value_2):
                        troughs_map[current_lat, current_lon] = 1
                    elif (current_slp_value > slp_value_1) and (current_slp_value > slp_value_2):
                            ridges_map[current_lat, current_lon] = 1

                # Check for troughs and ridges on the lon axis
                if (current_lon > 1) and (current_lon < total_lon):
                    slp_value_1 = slp_data[current_day, current_lat, current_lon - 1]
                    slp_value_2 = slp_data[current_day, current_lat, current_lon + 1]
                    if (current_slp_value < slp_value_1) and (current_slp_value < slp_value_2):
                        troughs_map[current_lat, current_lon] = 1
                    elif (current_slp_value > slp_value_1) and (current_slp_value > slp_value_2):
                            ridges_map[current_lat, current_lon] = 1

                # Check for troughs and ridges on the diagonals
                if (current_lon > 1) and (current_lon < total_lon) and (current_lat > 1) and (current_lat < total_lat):
                    slp_value_1 = slp_data[current_day, current_lat - 1, current_lon - 1]
                    slp_value_2 = slp_data[current_day, current_lat + 1, current_lon + 1]
                    slp_value_3 = slp_data[current_day, current_lat + 1, current_lon - 1]
                    slp_value_4 = slp_data[current_day, current_lat - 1, current_lon + 1]
                    if ((current_slp_value < slp_value_1) and (current_slp_value < slp_value_2)) or ((current_slp_value < slp_value_3) and (current_slp_value < slp_value_4)):
                        troughs_map[current_lat, current_lon] = 1
                    elif ((current_slp_value > slp_value_1) and (current_slp_value > slp_value_2)) or ((current_slp_value > slp_value_3) and (current_slp_value > slp_value_4)):
                            ridges_map[current_lat, current_lon] = 1

        # Calculate Vorticity
        if show_vorticity == 1:
            uwind_map = np.squeeze(uwind_data[current_day, :, :])
            vwind_map = np.squeeze(vwind_data[current_day, :, :])

            vorticity_map = np.zeros(uwind_map.shape[0], uwind_map.shape[1])
            for current_lat in range(1, uwind_map.shape[0]):
                for current_lon in range(1, uwind_map.shape[1]):
                    duwind = uwind_map[current_lat + 1, current_lon] - uwind_map[current_lat - 1, current_lon]
                    dvwind = vwind_map[current_lat, current_lon + 1] - vwind_map[current_lat, current_lon - 1]
                    dy = 2 * data_resolution * 111000 # 111 Km. is the distance of 1 degree latitude. We look for the distance between 2 points.
                    dx = 2 * data_resolution * 111000 * math.cos(math.radians(slp_lats[current_lat]))
                    vorticity_map[current_lat, current_lon] = (dvwind / dx) - (duwind / dy)

        # Calculate Geostrophic vorticity
        if show_geostrophic_vorticity == 1:
            ugwind_map = np.zeros((total_lat, total_lon))
            vgwind_map = np.zeros((total_lat, total_lon))
            geostrophic_vorticity_map = np.zeros((total_lat, total_lon))
            rho = 1.2754
            omega = 7.27e-5
            for current_lat in range(1, total_lat - 1):
                for current_lon in range(1, total_lon - 1):
                    dpx = slp_data[current_day, current_lat, current_lon + 1] - slp_data[current_day,current_lat, current_lon - 1]
                    dpy = slp_data[current_day, current_lat + 1, current_lon] - slp_data[current_day, current_lat - 1, current_lon]
                    if use_interpolation == 1:
                        dy = 2 * interp_resolution * 111000 # 111 Km. is the distance of 1 degree latitude. We look for the distance between 2 points.
                        dx = 2 * interp_resolution * 111000 * math.cos(math.radians(slp_lats[current_lat]))
                    else:
                        dy = 2 * data_resolution * 111000 # 111 Km. is the distance of 1 degree latitude. We look for the distance between 2 points.
                        dx = 2 * data_resolution * 111000 * math.cos(math.radians(slp_lats[current_lat]))
                    ugwind_map[current_lat, current_lon] = (((-1) / rho) * (dpy / dy)) / (2 * omega * math.sin(math.radians(current_lat)))
                    vgwind_map[current_lat, current_lon] = (((1) / rho) * (dpx / dx)) / (2 * omega * math.sin(math.radians(current_lat)))

            for current_lat in range(2, total_lat - 1):
                for current_lon in range(2, total_lon - 1):
                    duwind = ugwind_map[current_lat + 1, current_lon] - ugwind_map[current_lat - 1, current_lon]
                    dvwind = vgwind_map[current_lat, current_lon + 1] - vgwind_map[current_lat, current_lon - 1]
                    geostrophic_vorticity_map[current_lat, current_lon] = (dvwind / dx) - (duwind / dy)

        # Find Red Sea Trough
        func_interp_resolution = 0.5  # This is the interpolated resolution(degrees) for the find trough function.
        if use_interpolation == 0: # Not already inerpolated at the beginning. Needs the interpolation for the find_trough function
            total_lat = slp_lats.shape[0]
            total_lon = slp_lons.shape[0]

            interp_ratio = func_interp_resolution / data_resolution
            [x_dense, y_dense] = np.meshgrid(np.arange(slp_lons[0], slp_lons[-1] + interp_resolution, interp_resolution),
                                             np.arange(slp_lats[0], slp_lats[-1] + interp_resolution, interp_resolution))
            temp_slp_data = basemap.interp(np.squeeze(slp_data[current_day, :, :]), slp_lons, slp_lats, x_dense,
                                                                  y_dense, order=interpolation_method)
        else:
            temp_slp_data = np.squeeze(slp_data[current_day, :, :])
        lowest_lat = slp_lats[0]
        lowest_lon = slp_lons[0]
        multiplier = 1 / func_interp_resolution
        indexed_rst_lat1 = int((rst_lat1 - lowest_lat) * multiplier)
        indexed_rst_lat2 = int((rst_lat2 - lowest_lat) * multiplier)
        indexed_rst_lon1 = int((rst_lon1 - lowest_lon) * multiplier)
        indexed_rst_lon2 = int((rst_lon2 - lowest_lon) * multiplier)
        trough_matrix = temp_slp_data[indexed_rst_lat1:indexed_rst_lat2+1, indexed_rst_lon1: indexed_rst_lon2+1]
        trough_coordinates = find_trough(trough_matrix)

        # Calculate the mean SLP in the RST squares
        indexed_rst_square1_lat1 = math.ceil((rst_square1_lat1 - lowest_lat) * multiplier)
        indexed_rst_square1_lat2 = math.floor((rst_square1_lat2 - lowest_lat) * multiplier)
        indexed_rst_square1_lon1 = math.ceil((rst_square1_lon1 - lowest_lat) * multiplier)
        indexed_rst_square1_lon2 = math.floor((rst_square1_lon2 - lowest_lat) * multiplier)
        mean_slp_square1 = np.mean(np.mean(temp_slp_data[indexed_rst_square1_lat1:indexed_rst_square1_lat2+1, indexed_rst_square1_lon1:indexed_rst_square1_lon2+1])) / 100
        print("mean SLP at square 1: %f", mean_slp_square1)

        indexed_rst_square2_lat1 = math.ceil((rst_square2_lat1 - lowest_lat) * multiplier)
        indexed_rst_square2_lat2 = math.floor((rst_square2_lat2 - lowest_lat) * multiplier)
        indexed_rst_square2_lon1 = math.ceil((rst_square2_lon1 - lowest_lat) * multiplier)
        indexed_rst_square2_lon2 = math.floor((rst_square2_lon2 - lowest_lat) * multiplier)
        mean_slp_square2 = np.mean(np.mean(temp_slp_data[indexed_rst_square2_lat1:indexed_rst_square2_lat2+1, indexed_rst_square2_lon1:indexed_rst_square2_lon2+1])) / 100
        print("mean SLP at square 2: %f", mean_slp_square2)

        # Calculate the mean Geostrophic Vorticity in the 3rd RST square
        if show_geostrophic_vorticity == 1:
            if use_interpolation == 1:
                vort_multiplier = 1 / interp_resolution
            else:
                vort_multiplier = 1 / data_resolution
            indexed_rst_square3_lat1 = math.ceil((rst_square3_lat1 - lowest_lat) * vort_multiplier)
            indexed_rst_square3_lat2 = math.floor((rst_square3_lat2 - lowest_lat) * vort_multiplier)
            indexed_rst_square3_lon1 = math.ceil((rst_square3_lon1 - lowest_lat) * vort_multiplier)
            indexed_rst_square3_lon2 = math.floor((rst_square3_lon2 - lowest_lat) * vort_multiplier)
            mean_geos_vort_square3 = np.mean(np.mean(geostrophic_vorticity_map[indexed_rst_square3_lat1:indexed_rst_square3_lat2+1, indexed_rst_square3_lon1:indexed_rst_square3_lon2+1])) / 100
            print("mean Geostrophic Vorticity at square 3: %f", mean_geos_vort_square3)

        # Check for the RST square condition
        if show_geostrophic_vorticity == 1:
            if (mean_slp_square1 < mean_slp_square2) and (mean_geos_vort_square3 > 0):
                print('RST square conditions met')
            else:
                print('RST square conditions are not met')
            print('=====================================')

        if (mean_slp_square1 < mean_slp_square2) and (mean_geos_vort_square3 > 0) and any(trough_coordinates):
            is_rst_vector[current_day] = 1

        if display_maps == 1:
            # Display the troughs and ridges maps
            aspect_ratio = total_lon/total_lat
            if aspect_ratio <= (16/9):
                size_y = 12
                size_x = size_y*aspect_ratio
            else:
                size_x = 20
                size_y = size_x/aspect_ratio
            fig = plt.figure(num=None, figsize=(size_x, size_y ), dpi=80, facecolor='w', edgecolor='k')
            map = Basemap(llcrnrlon=lon1, llcrnrlat=lat1, urcrnrlon=lon2, urcrnrlat=lat2, projection='merc', resolution='i')
            map.drawcoastlines()
            #map.fillcontinents(color='coral', lake_color='aqua')
            # draw parallels and meridians.
            map.drawparallels(np.arange(lat1, lat2, 2.5), labels=[1, 0, 0, 0], fontsize=8)
            map.drawmeridians(np.arange(lon1, lon2, 2.5), labels=[0, 0, 0, 1], fontsize=8)
            #map.drawmapboundary(fill_color='aqua')
            plt.title("Red Sea Troughs")

            if show_vorticity == 1:
                map.pcolor(slp_lons, slp_lats, vorticity_map)
                map.colorbar()

            if show_geostrophic_vorticity == 1:
                lon1_index = int(np.where(slp_lons == lon1)[0])
                lon2_index = int(np.where(slp_lons == lon2)[0])
                lat1_index = int(np.where(slp_lats == lat1)[0])
                lat2_index = int(np.where(slp_lats == lat2)[0])
                subset_geostrophic_vorticity_map = geostrophic_vorticity_map[lat1_index:lat2_index+1, lon1_index:lon2_index+1]
                mesh_lons, mesh_lats = np.meshgrid(slp_lons[lon1_index:lon2_index+1], slp_lats[lat1_index:lat2_index+1])
                x, y = map(mesh_lons, mesh_lats)
                #clevs = np.arange(subset_geostrophic_vorticity_map.min(), subset_geostrophic_vorticity_map.max(), (subset_geostrophic_vorticity_map.max() - subset_geostrophic_vorticity_map.min()) / 11)
                #map.pcolormesh(x, y, subset_geostrophic_vorticity_map)
                map.contour(x, y, slp_data[current_day, lat1_index:lat2_index+1, lon1_index:lon2_index+1], 15, linewidths=1.5, colors='k')
                map.contour(x, y, subset_geostrophic_vorticity_map, 10, linewidths=0.5, colors='k')
                map.contourf(x, y, subset_geostrophic_vorticity_map, 10)
                map.colorbar()

            # Draw the troughs and ridges dots
            if show_dots == 1:
                if use_interpolation == 1:
                    for current_lat in range(10,total_lat - 11):
                        for current_lon in range(10, total_lon - 11):
                            x_dot, y_dot = map(slp_lons[current_lon],  slp_lats[current_lat])
                            if troughs_map[current_lat, current_lon] == 1:
                                map.plot(x_dot, y_dot, 'D-', markersize=10, dotwidth=2, color='k', markerfacecolor='b')
                            if ridges_map[current_lat, current_lon] == 1:
                                map.plot(x_dot, y_dot, 'D-', markersize=10, dotwidth=2, color='k', markerfacecolor='r')
                else:
                    for current_lat in range(2, total_lat - 3):
                        for current_lon in range(2, total_lon - 3):
                            x_dot, y_dot = map(slp_lons[current_lon],  slp_lats[current_lat])
                            if troughs_map[current_lat, current_lon] == 1:
                                map.plot(x_dot, y_dot, 'D-', markersize=10, dotwidth=2, color='k', markerfacecolor='b')
                            if ridges_map[current_lat, current_lon] == 1:
                                map.plot(x_dot, y_dot, 'D-', markersize=10, dotwidth=2, color='k', markerfacecolor='r')
            # Add the date
            x_dot, y_dot = map(lon1+1, lat2-1)
            current_date = num2date(slp_time[0], slp_time.units)
            plt.text(x_dot, y_dot, current_date, fontsize=20, bbox=dict(facecolor="white", alpha=0.5))

            # Draw the RST, if such exists.
            if any(trough_coordinates):
                trough_length = trough_coordinates.shape[0]
                trough_deg_coordinates = np.zeros((trough_length, 2))
                for loop in range(trough_length):
                    trough_deg_coordinates[loop, 0] = rst_lat1 + ((loop) * interp_resolution)
                    trough_deg_coordinates[loop, 1] = rst_lon1 + ((trough_coordinates[loop]) * interp_resolution)

                x_trough, y_trough = map(trough_deg_coordinates[:,1], trough_deg_coordinates[:,0])
                map.plot(x_trough, y_trough, marker=None, linewidth = 6, color='black')
                map.plot(x_trough, y_trough, marker=None, linewidth=4, color='red')

            if show_rst_info == 1: # Draw box3 and the 2 points
                lat_array_region = [rst_square3_lat1,
                                    rst_square3_lat1,
                                    rst_square3_lat2,
                                    rst_square3_lat2,
                                    rst_square3_lat1]
                lon_array_region = [rst_square3_lon1,
                                    rst_square3_lon2,
                                    rst_square3_lon2,
                                    rst_square3_lon1,
                                    rst_square3_lon1]
                x_region, y_region = map(lon_array_region, lat_array_region)
                map.plot(x_region, y_region, marker=None, linewidth = 3, color='black')
                if use_interpolation == 0:
                    x_mark, y_mark = map(35,30)
                    map.plot(x_mark, y_mark, 'D-', markersize=10, color='blue')
                    x_mark, y_mark = map(35,32.5)
                    map.plot(x_mark, y_mark, 'D-', markersize=10, color='blue')

                # Add the points value
                if use_interpolation == 0:
                    data_string = "1st point: " + str(geostrophic_vorticity_map[4, 6])\
                                  +"  2nd point: " + str(geostrophic_vorticity_map[3, 6])
                    x_dot, y_dot = map(lon1 + 1, lat2 - 2)
                    plt.text(x_dot, y_dot, data_string, fontsize=20, bbox=dict(facecolor="white", alpha=0.5))

                # Add a note for met rst conditions
                x_dot, y_dot = map(lon1 + 1, lat2 - 3)
                if (mean_slp_square1 < mean_slp_square2) and (mean_geos_vort_square3 > 0):
                    plt.text(x_dot, y_dot, 'RST square conditions met', fontsize=20, bbox=dict(facecolor="white", alpha=0.5))
                else:
                    plt.text(x_dot, y_dot, 'RST square conditions not met', fontsize=20, bbox=dict(facecolor="white", alpha=0.5))

            if save_maps == 1:
                directory = ("C:/Users/hatzv/Documents/Geography/Research_help/Pinhas synoptic classification/New_classification_algorithm/output/")
                map_name_str = "Try_" + str(map_counter)
                filename = directory + map_name_str + ".png"
                plt.savefig(filename)

            plt.show()

    print()


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

if __name__ == "__main__":
    # execute only if run as a script
    main()