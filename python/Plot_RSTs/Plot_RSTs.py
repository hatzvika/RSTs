import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from mpl_toolkits import basemap

# My imports
from python.Plot_RSTs.find_trough import find_trough
import python.Plot_RSTs.plot_RST_constants as consts
from python.utils.read_nc_files import read_nc_files
from python.utils.my_interp import my_interp


def main():
    use_interpolation = True
    show_vorticity = False
    show_geostrophic_vorticity = True
    show_dots = True
    show_rst_info = True
    save_maps = False
    display_maps = True

    # Read the data files
    slp_filename = consts.raw_data_prefix + "SLP/SLP_NCEP_20-50N_20-50E_full_1985.nc"
    slp_data, orig_data_lats, orig_data_lons, data_time, data_string_time = read_nc_files(slp_filename, 'slp', start_time=2, delta_time=4)
    if show_vorticity:
        uwind_filename = consts.raw_data_prefix + "/uwind/uwind_850hPa_NCEP_22.5-47.5N_22.5-47.5E_May_1985.nc"
        uwind_data = read_nc_files(uwind_filename, 'uwnd', start_time=2, delta_time=4)[0]
        vwind_filename = consts.raw_data_prefix + "/vwind/vwind_850hPa_NCEP_22.5-47.5N_22.5-47.5E_May_1985.nc"
        vwind_data = read_nc_files(vwind_filename, 'vwnd', start_time=2, delta_time=4)[0]

    total_days = slp_data.shape[0]
    data_resolution = orig_data_lats[1] - orig_data_lats[0]

    total_lat = orig_data_lats.shape[0]
    total_lon = orig_data_lons.shape[0]

    # Interpolation of the data
    if use_interpolation:
        # Find the interp lats and lons to create the temporary data holders.
        _, interp_data_lats, interp_data_lons = my_interp(slp_data[0, :, :],
                                                          orig_data_lats,
                                                          orig_data_lons,
                                                          consts.interp_resolution,
                                                          consts.interpolation_method)
        temp_slp_data = np.zeros((total_days, interp_data_lats.shape[0], interp_data_lons.shape[0]))

        for current_day in range(total_days):
            temp_slp_data[current_day, :, :] = my_interp(slp_data[current_day, :, :],
                                                         orig_data_lats,
                                                         orig_data_lons,
                                                         consts.interp_resolution,
                                                         consts.interpolation_method)[0]
        slp_data = temp_slp_data
        # Change the values of total lat and lon to the interpolated value of later
        total_lat = slp_data.shape[1]
        total_lon = slp_data.shape[2]

        if show_vorticity:
            vort_total_days = uwind_data.shape[0]
            temp_uwind_data = np.zeros((vort_total_days, interp_data_lats.shape[0], interp_data_lons.shape[0]))
            temp_vwind_data = np.zeros((vort_total_days, interp_data_lats.shape[0], interp_data_lons.shape[0]))
            for current_day in range(vort_total_days):
                temp_uwind_data[current_day, :, :] = my_interp(uwind_data[current_day, :, :],
                                                 orig_data_lats,
                                                 orig_data_lons,
                                                 consts.interp_resolution,
                                                 consts.interpolation_method)[0]
                temp_vwind_data[current_day, :, :] = my_interp(vwind_data[current_day, :, :],
                                                       orig_data_lats,
                                                       orig_data_lons,
                                                       consts.interp_resolution,
                                                       consts.interpolation_method)[0]
            uwind_data = temp_uwind_data
            vwind_data = temp_vwind_data

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
        if show_vorticity:
            uwind_map = np.squeeze(uwind_data[current_day, :, :])
            vwind_map = np.squeeze(vwind_data[current_day, :, :])

            vorticity_map = np.zeros((uwind_map.shape[0], uwind_map.shape[1]))
            for current_lat in range(1, uwind_map.shape[0]-1):
                for current_lon in range(1, uwind_map.shape[1]-1):
                    duwind = uwind_map[current_lat + 1, current_lon] - uwind_map[current_lat - 1, current_lon]
                    dvwind = vwind_map[current_lat, current_lon + 1] - vwind_map[current_lat, current_lon - 1]
                    if use_interpolation:
                        dy = 2 * consts.interp_resolution * 111000  # 111 Km. is the distance of 1 degree latitude. We look for the distance between 2 points.
                        dx = 2 * consts.interp_resolution * 111000 * math.cos(math.radians(interp_data_lats[current_lat]))
                    else:
                        dy = 2 * data_resolution * 111000  # 111 Km. is the distance of 1 degree latitude. We look for the distance between 2 points.
                        dx = 2 * data_resolution * 111000 * math.cos(math.radians(orig_data_lats[current_lat]))
                    vorticity_map[current_lat, current_lon] = (dvwind / dx) - (duwind / dy)

        # Calculate Geostrophic vorticity
        if show_geostrophic_vorticity:
            ugwind_map = np.zeros((total_lat, total_lon))
            vgwind_map = np.zeros((total_lat, total_lon))
            geostrophic_vorticity_map = np.zeros((total_lat, total_lon))
            rho = 1.2754
            omega = 7.27e-5
            for current_lat in range(1, total_lat - 1):
                for current_lon in range(1, total_lon - 1):
                    dpx = slp_data[current_day, current_lat, current_lon + 1] - slp_data[current_day,current_lat, current_lon - 1]
                    dpy = slp_data[current_day, current_lat + 1, current_lon] - slp_data[current_day, current_lat - 1, current_lon]
                    if use_interpolation:
                        dy = 2 * consts.interp_resolution * 111000 # 111 Km. is the distance of 1 degree latitude. We look for the distance between 2 points.
                        dx = 2 * consts.interp_resolution * 111000 * math.cos(math.radians(interp_data_lats[current_lat]))
                    else:
                        dy = 2 * data_resolution * 111000 # 111 Km. is the distance of 1 degree latitude. We look for the distance between 2 points.
                        dx = 2 * data_resolution * 111000 * math.cos(math.radians(orig_data_lats[current_lat]))
                    ugwind_map[current_lat, current_lon] = (((-1) / rho) * (dpy / dy)) / (2 * omega * math.sin(math.radians(current_lat)))
                    vgwind_map[current_lat, current_lon] = (((1) / rho) * (dpx / dx)) / (2 * omega * math.sin(math.radians(current_lat)))

            for current_lat in range(2, total_lat - 1):
                for current_lon in range(2, total_lon - 1):
                    duwind = ugwind_map[current_lat + 1, current_lon] - ugwind_map[current_lat - 1, current_lon]
                    dvwind = vgwind_map[current_lat, current_lon + 1] - vgwind_map[current_lat, current_lon - 1]
                    geostrophic_vorticity_map[current_lat, current_lon] = (dvwind / dx) - (duwind / dy)

        # Find Red Sea Trough
        func_interp_resolution = 0.5  # This is the interpolated resolution(degrees) for the find trough function.
        if not use_interpolation: # Not already inerpolated at the beginning. Needs the interpolation for the find_trough function
            total_lat = orig_data_lats.shape[0]
            total_lon = orig_data_lons.shape[0]

            [x_dense, y_dense] = np.meshgrid(np.arange(orig_data_lons[0], orig_data_lons[-1] + func_interp_resolution, func_interp_resolution),
                                             np.arange(orig_data_lats[0], orig_data_lats[-1] + func_interp_resolution, func_interp_resolution))
            temp_slp_data = basemap.interp(np.squeeze(slp_data[current_day, :, :]), orig_data_lons, orig_data_lats, x_dense,
                                                                  y_dense, order=consts.interpolation_method)
        else:
            temp_slp_data = np.squeeze(slp_data[current_day, :, :])
        lowest_lat = orig_data_lats[0]
        lowest_lon = orig_data_lons[0]
        multiplier = 1 / func_interp_resolution
        indexed_rst_lat1 = int((consts.rst_lat1 - lowest_lat) * multiplier)
        indexed_rst_lat2 = int((consts.rst_lat2 - lowest_lat) * multiplier)
        indexed_rst_lon1 = int((consts.rst_lon1 - lowest_lon) * multiplier)
        indexed_rst_lon2 = int((consts.rst_lon2 - lowest_lon) * multiplier)
        trough_matrix = temp_slp_data[indexed_rst_lat1:indexed_rst_lat2+1, indexed_rst_lon1: indexed_rst_lon2+1]
        trough_coordinates = find_trough(trough_matrix)

        # Calculate the mean SLP in the RST squares
        indexed_rst_square1_lat1 = math.ceil((consts.rst_square1_lat1 - lowest_lat) * multiplier)
        indexed_rst_square1_lat2 = math.floor((consts.rst_square1_lat2 - lowest_lat) * multiplier)
        indexed_rst_square1_lon1 = math.ceil((consts.rst_square1_lon1 - lowest_lat) * multiplier)
        indexed_rst_square1_lon2 = math.floor((consts.rst_square1_lon2 - lowest_lat) * multiplier)
        mean_slp_square1 = np.mean(np.mean(temp_slp_data[indexed_rst_square1_lat1:indexed_rst_square1_lat2+1, indexed_rst_square1_lon1:indexed_rst_square1_lon2+1])) / 100
        print("mean SLP at square 1: %f", mean_slp_square1)

        indexed_rst_square2_lat1 = math.ceil((consts.rst_square2_lat1 - lowest_lat) * multiplier)
        indexed_rst_square2_lat2 = math.floor((consts.rst_square2_lat2 - lowest_lat) * multiplier)
        indexed_rst_square2_lon1 = math.ceil((consts.rst_square2_lon1 - lowest_lat) * multiplier)
        indexed_rst_square2_lon2 = math.floor((consts.rst_square2_lon2 - lowest_lat) * multiplier)
        mean_slp_square2 = np.mean(np.mean(temp_slp_data[indexed_rst_square2_lat1:indexed_rst_square2_lat2+1, indexed_rst_square2_lon1:indexed_rst_square2_lon2+1])) / 100
        print("mean SLP at square 2: %f", mean_slp_square2)

        # Calculate the mean Geostrophic Vorticity in the 3rd RST square
        if show_geostrophic_vorticity:
            if use_interpolation:
                vort_multiplier = 1 / consts.interp_resolution
            else:
                vort_multiplier = 1 / data_resolution
            indexed_rst_square3_lat1 = math.ceil((consts.rst_square3_lat1 - lowest_lat) * vort_multiplier)
            indexed_rst_square3_lat2 = math.floor((consts.rst_square3_lat2 - lowest_lat) * vort_multiplier)
            indexed_rst_square3_lon1 = math.ceil((consts.rst_square3_lon1 - lowest_lat) * vort_multiplier)
            indexed_rst_square3_lon2 = math.floor((consts.rst_square3_lon2 - lowest_lat) * vort_multiplier)
            mean_geos_vort_square3 = np.mean(np.mean(geostrophic_vorticity_map[indexed_rst_square3_lat1:indexed_rst_square3_lat2+1, indexed_rst_square3_lon1:indexed_rst_square3_lon2+1])) / 100
            print("mean Geostrophic Vorticity at square 3: %f", mean_geos_vort_square3)

        # Check for the RST square condition
        if show_geostrophic_vorticity:
            if (mean_slp_square1 < mean_slp_square2) and (mean_geos_vort_square3 > 0):
                print('RST square conditions met')
            else:
                print('RST square conditions are not met')
            print('=====================================')

            if (mean_slp_square1 < mean_slp_square2) and (mean_geos_vort_square3 > 0) and any(trough_coordinates):
                is_rst_vector[current_day] = 1

        if display_maps:
            # Display the troughs and ridges maps
            aspect_ratio = total_lon/total_lat
            if aspect_ratio <= (16/9):
                size_y = 12
                size_x = size_y*aspect_ratio
            else:
                size_x = 20
                size_y = size_x/aspect_ratio
            fig = plt.figure(num=None, figsize=(size_x, size_y ), dpi=80, facecolor='w', edgecolor='k')
            map = Basemap(llcrnrlon=consts.map_lon1, llcrnrlat=consts.map_lat1, urcrnrlon=consts.map_lon2, urcrnrlat=consts.map_lat2, projection='merc', resolution='i')
            map.drawcoastlines()
            #map.fillcontinents(color='coral', lake_color='aqua')
            # draw parallels and meridians.
            map.drawparallels(np.arange(consts.map_lat1, consts.map_lat2, 2.5), labels=[1, 0, 0, 0], fontsize=8)
            map.drawmeridians(np.arange(consts.map_lon1, consts.map_lon2, 2.5), labels=[0, 0, 0, 1], fontsize=8)
            #map.drawmapboundary(fill_color='aqua')
            plt.title("Red Sea Troughs")

            if show_vorticity:
                if use_interpolation:
                    lon1_index = int(np.where(interp_data_lons == consts.map_lon1)[0])
                    lon2_index = int(np.where(interp_data_lons == consts.map_lon2)[0])
                    lat1_index = int(np.where(interp_data_lats == consts.map_lat1)[0])
                    lat2_index = int(np.where(interp_data_lats == consts.map_lat2)[0])
                    mesh_lons, mesh_lats = np.meshgrid(interp_data_lons[lon1_index:lon2_index + 1], interp_data_lats[lat1_index:lat2_index + 1])
                else:
                    lon1_index = int(np.where(orig_data_lons == consts.map_lon1)[0])
                    lon2_index = int(np.where(orig_data_lons == consts.map_lon2)[0])
                    lat1_index = int(np.where(orig_data_lats == consts.map_lat1)[0])
                    lat2_index = int(np.where(orig_data_lats == consts.map_lat2)[0])
                    mesh_lons, mesh_lats = np.meshgrid(orig_data_lons[lon1_index:lon2_index+1], orig_data_lats[lat1_index:lat2_index+1])

                subset_vorticity_map = vorticity_map[lat1_index:lat2_index+1, lon1_index:lon2_index+1]
                x, y = map(mesh_lons, mesh_lats)
                #clevs = np.arange(subset_geostrophic_vorticity_map.min(), subset_geostrophic_vorticity_map.max(), (subset_geostrophic_vorticity_map.max() - subset_geostrophic_vorticity_map.min()) / 11)
                #map.pcolormesh(x, y, subset_geostrophic_vorticity_map)
                map.contour(x, y, slp_data[current_day, lat1_index:lat2_index+1, lon1_index:lon2_index+1], 15, linewidths=1.5, colors='k')
                map.contour(x, y, subset_vorticity_map, 10, linewidths=0.5, colors='k')
                map.contourf(x, y, subset_vorticity_map, 10)
                map.colorbar()

            if show_geostrophic_vorticity:
                if use_interpolation:
                    lon1_index = int(np.where(interp_data_lons == consts.map_lon1)[0])
                    lon2_index = int(np.where(interp_data_lons == consts.map_lon2)[0])
                    lat1_index = int(np.where(interp_data_lats == consts.map_lat1)[0])
                    lat2_index = int(np.where(interp_data_lats == consts.map_lat2)[0])
                    mesh_lons, mesh_lats = np.meshgrid(interp_data_lons[lon1_index:lon2_index + 1], interp_data_lats[lat1_index:lat2_index + 1])
                else:
                    lon1_index = int(np.where(orig_data_lons == consts.map_lon1)[0])
                    lon2_index = int(np.where(orig_data_lons == consts.map_lon2)[0])
                    lat1_index = int(np.where(orig_data_lats == consts.map_lat1)[0])
                    lat2_index = int(np.where(orig_data_lats == consts.map_lat2)[0])
                    mesh_lons, mesh_lats = np.meshgrid(orig_data_lons[lon1_index:lon2_index + 1], orig_data_lats[lat1_index:lat2_index + 1])
                subset_geostrophic_vorticity_map = geostrophic_vorticity_map[lat1_index:lat2_index+1, lon1_index:lon2_index+1]
                x, y = map(mesh_lons, mesh_lats)
                #clevs = np.arange(subset_geostrophic_vorticity_map.min(), subset_geostrophic_vorticity_map.max(), (subset_geostrophic_vorticity_map.max() - subset_geostrophic_vorticity_map.min()) / 11)
                #map.pcolormesh(x, y, subset_geostrophic_vorticity_map)
                map.contour(x, y, slp_data[current_day, lat1_index:lat2_index+1, lon1_index:lon2_index+1], 15, linewidths=1.5, colors='k')
                map.contour(x, y, subset_geostrophic_vorticity_map, 10, linewidths=0.5, colors='k')
                map.contourf(x, y, subset_geostrophic_vorticity_map, 10)
                map.colorbar()

            # Draw the troughs and ridges dots
            if show_dots:
                if use_interpolation:
                    for current_lat in range(10,total_lat - 11):
                        for current_lon in range(10, total_lon - 11):
                            x_dot, y_dot = map(interp_data_lons[current_lon],  interp_data_lats[current_lat])
                            if troughs_map[current_lat, current_lon] == 1:
                                map.plot(x_dot, y_dot, 'D-', markersize=10, color='k', markerfacecolor='b')
                            if ridges_map[current_lat, current_lon] == 1:
                                map.plot(x_dot, y_dot, 'D-', markersize=10, color='k', markerfacecolor='r')
                else:
                    for current_lat in range(2, total_lat - 3):
                        for current_lon in range(2, total_lon - 3):
                            x_dot, y_dot = map(orig_data_lons[current_lon],  orig_data_lats[current_lat])
                            if troughs_map[current_lat, current_lon] == 1:
                                map.plot(x_dot, y_dot, 'D-', markersize=10, color='k', markerfacecolor='b')
                            if ridges_map[current_lat, current_lon] == 1:
                                map.plot(x_dot, y_dot, 'D-', markersize=10, color='k', markerfacecolor='r')
            # Add the date
            x_dot, y_dot = map(consts.map_lon1+1, consts.map_lat2-1)
            current_date = data_string_time[current_day]
            plt.text(x_dot, y_dot, current_date, fontsize=20, bbox=dict(facecolor="white", alpha=0.5))

            # Draw the RST, if such exists.
            if any(trough_coordinates):
                trough_length = trough_coordinates.shape[0]
                trough_deg_coordinates = np.zeros((trough_length, 2))
                for loop in range(trough_length):
                    trough_deg_coordinates[loop, 0] = consts.rst_lat1 + ((loop - 1) * func_interp_resolution)
                    trough_deg_coordinates[loop, 1] = consts.rst_lon1 + ((trough_coordinates[loop]) * func_interp_resolution)

                x_trough, y_trough = map(trough_deg_coordinates[:,1], trough_deg_coordinates[:,0])
                map.plot(x_trough, y_trough, marker=None, linewidth = 6, color='black')
                map.plot(x_trough, y_trough, marker=None, linewidth=4, color='red')

            if show_rst_info: # Draw box3 and the 2 points
                lat_array_region = [consts.rst_square3_lat1,
                                    consts.rst_square3_lat1,
                                    consts.rst_square3_lat2,
                                    consts.rst_square3_lat2,
                                    consts.rst_square3_lat1]
                lon_array_region = [consts.rst_square3_lon1,
                                    consts.rst_square3_lon2,
                                    consts.rst_square3_lon2,
                                    consts.rst_square3_lon1,
                                    consts.rst_square3_lon1]
                x_region, y_region = map(lon_array_region, lat_array_region)
                map.plot(x_region, y_region, marker=None, linewidth = 3, color='black')
                if use_interpolation:
                    x_mark, y_mark = map(35,30)
                    map.plot(x_mark, y_mark, 'D-', markersize=10, color='blue')
                    x_mark, y_mark = map(35,32.5)
                    map.plot(x_mark, y_mark, 'D-', markersize=10, color='blue')

                # Add the points value
                if show_geostrophic_vorticity:
                    if use_interpolation:
                        data_string = "1st point: " + str(geostrophic_vorticity_map[4, 6])\
                                      +"  2nd point: " + str(geostrophic_vorticity_map[3, 6])
                        x_dot, y_dot = map(consts.map_lon1 + 1, consts.map_lat2 - 2)
                        plt.text(x_dot, y_dot, data_string, fontsize=20, bbox=dict(facecolor="white", alpha=0.5))

                    # Add a note for met rst conditions
                    x_dot, y_dot = map(consts.map_lon1 + 1, consts.map_lat2 - 3)
                    if (mean_slp_square1 < mean_slp_square2) and (mean_geos_vort_square3 > 0):
                        plt.text(x_dot, y_dot, 'RST square conditions met', fontsize=20, bbox=dict(facecolor="white", alpha=0.5))
                    else:
                        plt.text(x_dot, y_dot, 'RST square conditions not met', fontsize=20, bbox=dict(facecolor="white", alpha=0.5))

            if save_maps:
                directory = ("C:/Users/hatzv/Documents/Geography/Research_help/Pinhas synoptic classification/New_classification_algorithm/output/")
                map_name_str = "Try_" + str(map_counter)
                filename = directory + map_name_str + ".png"
                plt.savefig(filename)

            plt.show()

    print()

if __name__ == "__main__":
    # execute only if run as a script
    main()