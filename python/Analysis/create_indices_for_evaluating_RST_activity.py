import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# My imports
from python.utils.read_nc_files import read_nc_files
from python.utils.calculate_geostrophic_vorticity import calculate_geostrophic_vorticity

start_year = 1979
end_year = 1979  # 2017

data_directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Data/'

for current_year in range(start_year, end_year+1):
    # Read the data files for this year
    slp_filename = data_directory + 'SLP/NCEP/slp_' + str(current_year) + '_10-50N_20-50E.nc'
    geop_filename = data_directory + 'geopotential/NCEP/geopotential_' + str(current_year) + '_10-50N_20-50E_500.nc'
    shum_filename = data_directory + 'SHUM/NCEP/SHUM_' + str(current_year) + '_10-50N_20-50E_500_850_925.nc'
    temperature_filename = data_directory + 'temperature/NCEP/temperature_' + str(current_year) + '_10-50N_20-50E_500_850.nc'
    uwind_filename = data_directory + 'uwind/NCEP/uwind_' + str(current_year) + '_10-50N_20-50E_200_300_500_700.nc'
    vwind_filename = data_directory + 'vwind/NCEP/vwind_' + str(current_year) + '_10-50N_20-50E_200_300_500_700_850.nc'

    slp_data, data_lats, data_lons, data_time, data_string_time = read_nc_files(slp_filename)
    geop_data, geop_levels = read_nc_files(geop_filename)[0:2]
    shum_data, shum_levels = read_nc_files(shum_filename)[0:2]
    temperature_data, temperature_levels = read_nc_files(temperature_filename)[0:2]
    uwind_data, uwind_levels = read_nc_files(uwind_filename)[0:2]
    vwind_data, vwind_levels = read_nc_files(vwind_filename)[0:2]

    # The loop for calculating the right indices for each day
    for current_slice in range(np.size(slp_data, 0)):

        ##############################################################################################################
        # Calculate index 1 - max wind speed at 300hPa, along 35E between 20N-35N. Implication -Intensity of the STJ
        ##############################################################################################################
        index_1_level = 300  # hPa
        index_1_lon = 35 # 35E line
        index_1_lat1 = 20
        index_1_lat2 = 35

        uwind_level_index = list(uwind_levels).index(index_1_level)
        vwind_level_index = list(vwind_levels).index(index_1_level)

        # Create pandas dataframes for accessing the data easily
        uwind_df = pd.DataFrame(data=uwind_data[current_slice, uwind_level_index], index=data_lats, columns=data_lons)
        vwind_df = pd.DataFrame(data=vwind_data[current_slice, vwind_level_index], index=data_lats, columns=data_lons)
        req_uwind = uwind_df[index_1_lon][index_1_lat1:index_1_lat2]
        req_vwind = vwind_df[index_1_lon][index_1_lat1:index_1_lat2]

        # Calculation
        wind = np.sqrt(req_uwind**2 + req_vwind**2)
        index_1_value = wind.max()

        ##############################################################################################################
        # Calculate index 2 - max wind speed at 200hPa, along 35E between 20N-35N. Implication -Intensity of the STJ
        ##############################################################################################################
        index_2_level = 200  # hPa

        uwind_level_index = list(uwind_levels).index(index_2_level)
        vwind_level_index = list(vwind_levels).index(index_2_level)

        # Create pandas dataframes for accessing the data easily
        uwind_df = pd.DataFrame(data=uwind_data[current_slice, uwind_level_index], index=data_lats, columns=data_lons)
        vwind_df = pd.DataFrame(data=vwind_data[current_slice, vwind_level_index], index=data_lats, columns=data_lons)
        req_uwind = uwind_df[index_1_lon][index_1_lat1:index_1_lat2]
        req_vwind = vwind_df[index_1_lon][index_1_lat1:index_1_lat2]

        # Calculation
        wind = np.sqrt(req_uwind**2 + req_vwind**2)
        index_2_value = wind.max()

        ##############################################################################################################
        # Calculate indices 3,4 - max and mean G.vorticity in 29N-33.5N, 32E-38E. Implication -RST intensity.
        # Changed area to 27.5N-35N, 32.5E-37.5E to avoid the need for unnecessary interpolation.
        # The original definition is not on a 2.5X2.5 grid as well.
        ##############################################################################################################
        index_3_lon1 = 27.5
        index_3_lon2 = 35
        index_3_lat1 = 32.5
        index_3_lat2 = 37.5

        # Create pandas dataframes for accessing the data easily
        slp_df = pd.DataFrame(data=slp_data[current_slice], index=data_lats, columns=data_lons)

        # Calculation
        geostrophic_data = calculate_geostrophic_vorticity(np.array(slp_df), 2.5, data_lats, np.size(data_lats, 0), np.size(data_lons, 0))
        geostrophic_df = pd.DataFrame(data=geostrophic_data, index=data_lats, columns=data_lons)
        req_geostrophic = geostrophic_df[np.arange(index_3_lon1,index_3_lon2+2.5,2.5)][index_3_lat1:index_3_lat2]
        index_3_value = req_geostrophic.max().max()
        index_4_value = req_geostrophic.mean().mean()


        print()








        # # For testing
        # # Create the map object
        # fig = plt.figure(figsize=[16, 16 * 1080 / 1920])
        #
        # # Map borders
        # map_lat1 = 10
        # map_lat2 = 50
        # map_lon1 = 20
        # map_lon2 = 50
        # rst_map = Basemap(llcrnrlon=map_lon1,
        #                   llcrnrlat=map_lat1,
        #                   urcrnrlon=map_lon2,
        #                   urcrnrlat=map_lat2,
        #                   projection='merc',
        #                   resolution='i')
        # rst_map.drawcoastlines()
        # rst_map.drawparallels(np.arange(map_lat1, map_lat2, 5), linewidth=0.5, labels=[1, 0, 0, 0], fontsize=8, dashes=[1, 5])
        # rst_map.drawmeridians(np.arange(map_lon1, map_lon2, 5), linewidth=0.5, labels=[0, 0, 0, 1], fontsize=8, dashes=[1, 5])
        #
        # # Calculate the meshes for the maps and plot SLP contours (always)
        # lon1_index = int(np.where(data_lons <= map_lon1)[0][-1])
        # lon2_index = int(np.where(data_lons >= map_lon2)[0][-1])
        # lat1_index = int(np.where(data_lats <= map_lat1)[0][-1])
        # lat2_index = int(np.where(data_lats >= map_lat2)[0][-1])
        # mesh_lons, mesh_lats = np.meshgrid(data_lons[lon1_index:lon2_index + 1], data_lats[lat1_index:lat2_index + 1])
        #
        # x, y = rst_map(mesh_lons, mesh_lats)
        # cs = rst_map.contourf(x, y, slp_df.iloc[lat1_index:lat2_index + 1, lon1_index:lon2_index + 1], 15,
        #                       cmap='coolwarm')
        # rst_map.contour(x, y, slp_df.iloc[lat1_index:lat2_index + 1, lon1_index:lon2_index + 1], 15,
        #                 linewidths=1, colors='black')
        # plt.colorbar(cs)
        # plt.show()
        # wait = input("PRESS ENTER TO CONTINUE.")