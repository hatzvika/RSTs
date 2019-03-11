import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import datetime as dt

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
df = pd.read_excel('C:/Users/hatzv/Documents/Geography/RSTs/python/Results/RST_lows_after_RST.xlsx', 'Sheet1')
subdf = df.sort_values(by=['Max Radius 48'], ascending=False)

# (find problem with 20)
# gen = (temp for j in (range(0, 20), range(21, 76), range(77, 94), range(95,103)) for temp in j)
# gen = (temp for j in (range(77, 94), range(95,103)) for temp in j)
for i in range(100): #gen:
    # set the requested day
    req_date = subdf.iloc[i]['Date']
    req_year = req_date[0:4]
    req_month = req_date[5:7]
    req_day = req_date[8:10]
    req_hour = req_date[11:13]
    print(req_year, req_month, req_day, req_hour)

    # Find the slp map of the requested day
    slp_filename = Consts.raw_data_prefix + "SLP/ERA_Int/SLP_ERA_Int_10-50N_20-50E_full_" + req_year + ".nc"
    slp_data, slp_lats, slp_lons, _, slp_data_string_time = read_nc_files(slp_filename)

    if (req_month == '12') and (req_day == '31') and (req_hour == '18'):
        index_day = list(slp_data_string_time).index(dt.datetime(int(req_year), 12, 31, 12))
    else:
        index_day = list(slp_data_string_time).index(dt.datetime(int(req_year), int(req_month), int(req_day), int(req_hour)))
    slp_map = slp_data[index_day, :, :]

    # Find the 500hPa geopotential map of the requested day
    geop_filename = Consts.raw_data_prefix + "geopotential/NCEP/geopotential_" + req_year + "_10-50N_20-50E_500.nc"
    geop_data, geop_levels, geop_lats, geop_lons, _, geop_data_string_time = read_nc_files(geop_filename)

    geop_map = np.squeeze(geop_data[index_day, :, :])

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

    # Create the map object
    fig = plt.figure(figsize=[16, 16*1080/1920])

    # Plot the main title with all the information
    track_length_hours = str((len(curr_track)-1)*6) + ' Hrs'
    fig.suptitle(req_date + '\nTrack Length: ' + track_length_hours + ', Start Radius: ' + str(start_gradient) +\
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
    rst_map.plot(x_track[0], y_track[0], linestyle='none', marker="o", markersize=13, c="white", markeredgecolor="black",
           markeredgewidth=1)

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
    max_gradient = int(np.ceil(geop_map.max()))
    cs = rst_map.contourf(x, y, geop_map[lat1_index:lat2_index + 1, lon1_index:lon2_index + 1], range(min_geop, max_gradient + 20, 20),
                          cmap='coolwarm')
    rst_map.contour(x, y, geop_map[lat1_index:lat2_index + 1, lon1_index:lon2_index + 1], range(min_geop, max_gradient + 20, 20),
                    linewidths=1, colors='black')
    plt.colorbar(cs)

    # Plot the track on the GPH map
    x_track, y_track = rst_map(track_lons, track_lats)
    rst_map.plot(x_track, y_track, marker=None, linewidth=5, color='black')
    rst_map.plot(x_track, y_track, marker=None, linewidth=4, color='white')
    rst_map.plot(x_track[0], y_track[0], linestyle='none', marker="o", markersize=13, c="white", markeredgecolor="black",
           markeredgewidth=1)

    # plt.tight_layout()
    if save_maps:
        directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Results/Maps for daughter lows/'
        map_name = req_date[0:13]
        filename = directory + str(i) + "_" + map_name + ".png"
        plt.savefig(filename)
    else:
        plt.show()
    plt.close()
