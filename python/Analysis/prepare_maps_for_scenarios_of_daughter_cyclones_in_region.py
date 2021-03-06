import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import datetime as dt
from math import floor

import python.Plot_RSTs.plot_RST_constants as Consts
from python.utils.read_nc_files import read_nc_files
from python.Tracks.TracksDB import TracksDB

save_maps = True

# Map borders
map_lat1 = 20
map_lat2 = 50
map_lon1 = 20
map_lon2 = 45

# Read the dates, sorted by bigeest lat difference from parent
df = pd.read_excel('C:/Users/hatzv/Documents/Geography/RSTs/python/Results/RST_lows.xlsx', 'Sheet1')
subdf = df.sort_values(by=['Lat Difference'], ascending=False)

# (find problem with 20)
gen = (temp for j in (range(0, 20), range(21, 76), range(77, 94), range(95,103)) for temp in j)
# gen = (temp for j in (range(77, 94), range(95,103)) for temp in j)
slide_counter = 0
for i in gen:
    slide_counter += 1
    if slide_counter in [8, 18, 31, 33, 34, 35, 39, 43, 44, 45, 50, 51, 52,
                         53, 54, 55, 56, 57, 59, 62, 64, 65, 70, 71, 72,
                         75, 78, 82, 85, 88, 90, 93, 94, 95, 96, 97, 98, 100]:

    #if slide_counter in [9, 27, 31, 43, 48, 54, 56, 74, 78, 80, 82, 89, 92, 94, 98]:
        # set the requested day
        req_date = subdf.iloc[i]['Date']
        req_year = req_date[0:4]
        req_month = req_date[5:7]
        req_day = req_date[8:10]
        req_hour = req_date[11:13]
        print(req_year, req_month, req_day, req_hour)

        # Load the correct TracksDB file. The file is from Sep_year to May_year+1, so each req_year can have 2 TracksDB files.
        if int(req_month) >= 9:
            tr_db = TracksDB(int(req_year))
        else:
            tr_db = TracksDB(int(req_year) - 1)

        # Create the track for dispalying on the map and find the gradient statistics
        req_track = subdf.iloc[i]['Track Number']
        curr_track = tr_db.get_track(req_track)
        track_lats = []
        track_lons = []
        start_gradient = tr_db.get_low_radius(curr_track[0])
        max_gradient = start_gradient
        max_gradient_48 = start_gradient
        for low in range(len(curr_track)):
            low_num = curr_track[low]
            if low_num > 0:
                track_lats.append(tr_db.get_low_lat_degrees(low_num))
                track_lons.append(tr_db.get_low_lon_degrees(low_num))
                gradient = tr_db.get_low_radius(low_num)
                if gradient > max_gradient:
                    max_gradient = gradient
                if (gradient > max_gradient_48) and (low <= 7):
                    max_gradient_48 = gradient
            else:
                # This is for plotting the right place after a -1000 occurs
                track_lats.append(tr_db.get_low_lat_degrees(curr_track[low-1]))
                track_lons.append(tr_db.get_low_lon_degrees(curr_track[low-1]))

        time_offset = -1
        while time_offset < len(curr_track):

            # Find the slp map of the requested day
            slp_filename = Consts.raw_data_prefix + "SLP/ERA_Int/SLP_ERA_Int_10-50N_20-50E_full_" + req_year + ".nc"
            slp_data, slp_lats, slp_lons, _, slp_data_string_time = read_nc_files(slp_filename)

            index_day = list(slp_data_string_time).index(dt.datetime(int(req_year), int(req_month), int(req_day), int(req_hour))) + time_offset
            slp_map = slp_data[index_day, :, :]

            # Find the 500hPa geopotential map of the requested day
            geop_filename = Consts.raw_data_prefix + "geopotential/NCEP/geopotential_" + req_year + "_10-50N_20-50E_500.nc"
            geop_data, geop_levels, geop_lats, geop_lons, _, geop_data_string_time = read_nc_files(geop_filename)

            geop_map = geop_data[index_day, :, :]

            # Create the map object
            fig = plt.figure(figsize=[16, 16*1080/1920])

            # Plot the main title with all the information
            lat_diff = str(subdf.iloc[i]['Lat Difference'])
            track_length_hours = str((len(curr_track)-1)*6) + ' Hrs'
            fig.suptitle(req_date + ", offset: " + str(time_offset*6) + ' Hrs.\nLat Diff: ' + lat_diff +
                         ', Track Length: ' + track_length_hours + ', Start Radius: ' + str(start_gradient) +\
                         ', Max Radius: ' + str(max_gradient) + ', Max Radius in 48 Hrs: ' + str(max_gradient_48), fontsize=20)


            ax = fig.add_subplot(121)
            ax.set_title("SLP")
            rst_map = Basemap(llcrnrlon=map_lon1,
                              llcrnrlat=map_lat1,
                              urcrnrlon=map_lon2,
                              urcrnrlat=map_lat2,
                              projection='merc',
                              resolution='i')
            rst_map.drawcoastlines()
            rst_map.drawparallels(np.arange(map_lat1, map_lat2, 5), linewidth=0.5, labels=[1, 0, 0, 0], fontsize=8, dashes=[1, 5])
            rst_map.drawmeridians(np.arange(map_lon1, map_lon2, 5), linewidth=0.5, labels=[0, 0, 0, 1], fontsize=8, dashes=[1, 5])

            # Calculate the meshes for the maps and plot SLP contours (always)
            lon1_index = int(np.where(slp_lons <= map_lon1)[0][-1])
            lon2_index = int(np.where(slp_lons >= map_lon2)[0][-1])
            lat1_index = int(np.where(slp_lats <= map_lat1)[0][-1])
            lat2_index = int(np.where(slp_lats >= map_lat2)[0][-1])
            mesh_lons, mesh_lats = np.meshgrid(slp_lons[lon1_index:lon2_index + 1], slp_lats[lat1_index:lat2_index + 1])

            x, y = rst_map(mesh_lons, mesh_lats)
            min_slp = int(np.floor(slp_map.min()) / 100)
            max_slp = int(np.ceil(slp_map.max()) / 100)
            cs = rst_map.contourf(x, y, slp_map[lat1_index:lat2_index + 1, lon1_index:lon2_index + 1] / 100, range(min_slp, max_slp+2, 1),
                                  cmap='coolwarm')
            rst_map.contour(x, y, slp_map[lat1_index:lat2_index + 1, lon1_index:lon2_index + 1] / 100, range(min_slp, max_slp+2, 1),
                            linewidths=1, colors='black')
            plt.colorbar(cs)

            # Plot the track on the SLP map
            x_track, y_track = rst_map(track_lons, track_lats)
            rst_map.plot(x_track, y_track, marker=None, linewidth=5, color='black')
            rst_map.plot(x_track, y_track, marker=None, linewidth=4, color='white')

            # Plot the current place of the low with a big point. White for normal low and red for skipped time slice (-1000)
            if time_offset > -1:
                if curr_track[time_offset] == -1000:
                    rst_map.plot(x_track[time_offset-1], y_track[time_offset-1], linestyle='none', marker="o", markersize=13, c="red",
                                 markeredgecolor="black", markeredgewidth=1)
                else:
                    rst_map.plot(x_track[time_offset], y_track[time_offset], linestyle='none', marker="o", markersize=13, c="white",
                                 markeredgecolor="black", markeredgewidth=1)
            else:
                rst_map.plot(x_track[0], y_track[0], linestyle='none', marker="o", markersize=13, c="white",
                             markeredgecolor="black", markeredgewidth=1)

            ax = fig.add_subplot(122)
            ax.set_title("500hPa GPH")
            rst_map = Basemap(llcrnrlon=map_lon1,
                              llcrnrlat=map_lat1,
                              urcrnrlon=map_lon2,
                              urcrnrlat=map_lat2,
                              projection='merc',
                              resolution='i')
            rst_map.drawcoastlines()
            rst_map.drawparallels(np.arange(map_lat1, map_lat2, 5), linewidth=0.5, labels=[1, 0, 0, 0], fontsize=8, dashes=[1, 5])
            rst_map.drawmeridians(np.arange(map_lon1, map_lon2, 5), linewidth=0.5, labels=[0, 0, 0, 1], fontsize=8, dashes=[1, 5])

            # Calculate the meshes for the maps and plot GPH contours (always)
            lon1_index = int(np.where(geop_lons <= map_lon1)[0][-1])
            lon2_index = int(np.where(geop_lons >= map_lon2)[0][-1])
            lat1_index = int(np.where(geop_lats <= map_lat1)[0][-1])
            lat2_index = int(np.where(geop_lats >= map_lat2)[0][-1])
            mesh_lons, mesh_lats = np.meshgrid(geop_lons[lon1_index:lon2_index + 1], geop_lats[lat1_index:lat2_index + 1])

            x, y = rst_map(mesh_lons, mesh_lats)
            min_geop = int(np.floor(geop_map.min()))
            max_geop = int(np.ceil(geop_map.max()))
            cs = rst_map.contourf(x, y, geop_map[lat1_index:lat2_index + 1, lon1_index:lon2_index + 1],
                                  range(min_geop, max_geop + 20, 20),
                                  cmap='coolwarm')
            rst_map.contour(x, y, geop_map[lat1_index:lat2_index + 1, lon1_index:lon2_index + 1],
                            range(min_geop, max_geop + 20, 20),
                            linewidths=1, colors='black')
            plt.colorbar(cs)

            # Plot the track on the GPH map
            x_track, y_track = rst_map(track_lons, track_lats)
            rst_map.plot(x_track, y_track, marker=None, linewidth=5, color='black')
            rst_map.plot(x_track, y_track, marker=None, linewidth=4, color='white')

            # Plot the current place of the low with a big point. White for normal low and red for skipped time slice (-1000)
            if time_offset > -1:
                if curr_track[time_offset] == -1000:
                    rst_map.plot(x_track[time_offset-1], y_track[time_offset-1], linestyle='none', marker="o", markersize=13, c="red",
                                 markeredgecolor="black", markeredgewidth=1)
                else:
                    rst_map.plot(x_track[time_offset], y_track[time_offset], linestyle='none', marker="o", markersize=13, c="white",
                                 markeredgecolor="black", markeredgewidth=1)
            else:
                rst_map.plot(x_track[0], y_track[0], linestyle='none', marker="o", markersize=13, c="white",
                             markeredgecolor="black", markeredgewidth=1)

            # plt.tight_layout()
            if save_maps:
                directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Results/Maps for daughter lows scenarios/'
                map_name = req_date[0:13]
                filename = directory + str(i) + "_" + map_name + "_map_number_" + str(floor(time_offset/2)+1) + ".png"
                plt.savefig(filename)
            else:
                plt.show()
            plt.close()

            time_offset += 2
