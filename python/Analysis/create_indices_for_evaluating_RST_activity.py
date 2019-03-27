import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import metpy.calc as mpcalc
from geopy.distance import great_circle
import xlsxwriter

# My imports
from python.utils.read_nc_files import read_nc_files
from python.utils.calculate_geostrophic_vorticity import calculate_geostrophic_vorticity

start_year = 1979
end_year = 2017

excel_headers = ['Date', 'Max wind speed 300', 'Max wind speed 200', 'Max geost vort SLP', 'Average geost vort SLP', 'Pressure drop SLP',
                 'Moisture flux Y integral 850-500', 'Moisture flux Y 700', 'Precipitable water 925-850', 'Vorticity advection 500',
                 'Vorticity advection 300', 'U/V 500', 'U/V 700', 'Vorticity 500', 'GPH anomaly 500', 'Wind Speed 500',
                 'temperature difference 850-500', 'Propagation speed of upper cyclonic center 500',
                 'Intensification rate of upper cyclonic center 500', 'Relative location of max. upper vorticity 500']
final_list = [excel_headers]

data_directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Data/'
geop_500_long_monthly_term_file = data_directory + 'geopotential/NCEP/geopotential_monthly_long_term_mean_10-50N_20-50E_500hPa_1981-2010.nc'
geop_500_long_monthly_term_data, geop_500_long_monthly_term_levels = read_nc_files(geop_500_long_monthly_term_file)[0:2]

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

    # The loop for calculating the right indices for each day (12Z)
    # The first day is omitted because we need the previous 24 hours value for some params (this is why we start at 6)
    for current_slice in range(6, np.size(slp_data, 0)+1, 4):
        print(data_string_time[current_slice])
        # Create pandas dataframes for accessing the data easily. SLP doesn't require a level, so it is good for all SLP based params.
        slp_df = pd.DataFrame(data=slp_data[current_slice], index=data_lats, columns=data_lons)
        # dx and dy (for vorticity) don't change between indices.
        dx, dy = mpcalc.lat_lon_grid_deltas(data_lons, data_lats)

        ##############################################################################################################
        # Calculate index 1 - max wind speed at 300hPa, along 35E between 20N-35N. Implication -Intensity of the STJ
        ##############################################################################################################
        index_1_level = 300  # hPa
        index_1_lat1 = 20
        index_1_lat2 = 35
        index_1_lon = 35  # 35E line

        uwind_level_index = list(uwind_levels).index(index_1_level)
        vwind_level_index = list(vwind_levels).index(index_1_level)

        # Create pandas dataframes for accessing the data easily
        uwind_df = pd.DataFrame(data=uwind_data[current_slice, uwind_level_index], index=data_lats, columns=data_lons)
        vwind_df = pd.DataFrame(data=vwind_data[current_slice, vwind_level_index], index=data_lats, columns=data_lons)
        req_uwind = uwind_df[np.arange(index_1_lon, index_1_lon+2.5, 2.5)][index_1_lat1:index_1_lat2]
        req_vwind = vwind_df[np.arange(index_1_lon, index_1_lon+2.5, 2.5)][index_1_lat1:index_1_lat2]

        # Calculation
        wind = np.sqrt(req_uwind**2 + req_vwind**2)
        index_1_value = wind.max().max()

        ##############################################################################################################
        # Calculate index 2 - max wind speed at 200hPa, along 35E between 20N-35N. Implication -Intensity of the STJ
        ##############################################################################################################
        index_2_level = 200  # hPa

        uwind_level_index = list(uwind_levels).index(index_2_level)
        vwind_level_index = list(vwind_levels).index(index_2_level)

        # Create pandas dataframes for accessing the data easily
        uwind_df = pd.DataFrame(data=uwind_data[current_slice, uwind_level_index], index=data_lats, columns=data_lons)
        vwind_df = pd.DataFrame(data=vwind_data[current_slice, vwind_level_index], index=data_lats, columns=data_lons)
        req_uwind = uwind_df[np.arange(index_1_lon, index_1_lon+2.5, 2.5)][index_1_lat1:index_1_lat2]
        req_vwind = vwind_df[np.arange(index_1_lon, index_1_lon+2.5, 2.5)][index_1_lat1:index_1_lat2]

        # Calculation
        wind = np.sqrt(req_uwind**2 + req_vwind**2)
        index_2_value = wind.max().max()

        ##############################################################################################################
        # Calculate indices 3,4 - max and mean G.vorticity in 29N-33.5N, 32E-38E. Implication - RST intensity.
        # Changed area to 27.5N-35N, 32.5E-37.5E to avoid the need for unnecessary interpolation.
        # The original definition is not on a 2.5X2.5 grid as well.
        ##############################################################################################################
        index_3_lat1 = 27.5
        index_3_lat2 = 35
        index_3_lon1 = 32.5
        index_3_lon2 = 37.5

        # Calculation
        geostrophic_data = calculate_geostrophic_vorticity(np.array(slp_df), 2.5, data_lats, np.size(data_lats, 0), np.size(data_lons, 0))
        geostrophic_df = pd.DataFrame(data=geostrophic_data, index=data_lats, columns=data_lons)
        req_geostrophic = geostrophic_df[np.arange(index_3_lon1, index_3_lon2+2.5, 2.5)][index_3_lat1:index_3_lat2]
        index_3_value = req_geostrophic.max().max()
        index_4_value = req_geostrophic.mean().mean()

        ##############################################################################################################
        # Calculate index 5 - SLP average pressure drop in 29N-33.5N, 32E-38E. Implication - Surface cyclogenesis.
        # Changed area to 27.5N-35N, 32.5E-37.5E to avoid the need for unnecessary interpolation.
        # The original definition is not on a 2.5X2.5 grid as well.
        ##############################################################################################################
        index_5_lat1 = 27.5
        index_5_lat2 = 35
        index_5_lon1 = 32.5
        index_5_lon2 = 37.5

        # Create pandas dataframes for accessing the data easily
        previous_slp_df = pd.DataFrame(data=slp_data[current_slice-4], index=data_lats, columns=data_lons)

        # Create pandas dataframes for accessing the data easily
        req_current_slp = slp_df[np.arange(index_5_lon1, index_5_lon2+2.5, 2.5)][index_5_lat1:index_5_lat2]
        req_previous_slp = previous_slp_df[np.arange(index_5_lon1, index_5_lon2+2.5, 2.5)][index_5_lat1:index_5_lat2]

        # Calculation
        average_current = req_current_slp.mean().mean()
        average_previous = req_previous_slp.mean().mean()
        index_5_value = average_current - average_previous

        ##############################################################################################################
        # Calculate indices 6, 7 - Moisture flux in Y direction. Integral of shum*v between 850-500hPa and
        # shum*v 700hPa respectively, averaged over 26-30N,33-37E. Implication - Tropical moisture supply + alternative.
        # Changed area to 25N-30N, 32.5E-37.5E to avoid the need for unnecessary interpolation.
        ##############################################################################################################
        index_6_level1 = 850  # hPa
        index_6_level2 = 500  # hPa
        index_7_level = 700
        index_6_lat1 = 25
        index_6_lat2 = 30
        index_6_lon1 = 32.5
        index_6_lon2 = 37.5

        shum_level_indices = range(list(shum_levels).index(index_6_level1), list(shum_levels).index(index_6_level2) + 1)
        shum_level_index = list(shum_levels).index(index_7_level)

        index_6_value = 0
        for shum_level in shum_level_indices:
            # Create pandas dataframes for accessing the data easily
            shum_df = pd.DataFrame(data=shum_data[current_slice, shum_level], index=data_lats, columns=data_lons)
            vwind_level_index = list(vwind_levels).index(shum_levels[shum_level])
            vwind_df = pd.DataFrame(data=vwind_data[current_slice, vwind_level_index], index=data_lats, columns=data_lons)

            req_shum = shum_df[np.arange(index_6_lon1, index_6_lon2+2.5, 2.5)][index_6_lat1:index_6_lat2]
            req_vwind = vwind_df[np.arange(index_6_lon1, index_6_lon2+2.5, 2.5)][index_6_lat1:index_6_lat2]

            # Calculation
            index_6_value += (req_shum*req_vwind).mean().mean()
            if vwind_levels[vwind_level_index] == index_7_level:
                index_7_value = (req_shum*req_vwind).mean().mean()

        ##############################################################################################################
        # Calculate index 8 - Precipitable water. Integral of shum between 925-500hPa averaged over 29-32N,33-37E.
        # Implication - Moisture existence.Changed area to 30N-32.5N, 32.5E-37.5E to avoid the need for unnecessary interpolation.
        ##############################################################################################################
        index_8_level1 = 925  # hPa
        index_8_level2 = 500  # hPa
        index_8_lat1 = 30
        index_8_lat2 = 32.5
        index_8_lon1 = 32.5
        index_8_lon2 = 37.5

        shum_level_indices = range(list(shum_levels).index(index_8_level1), list(shum_levels).index(index_8_level2) + 1)

        index_8_value = 0
        for shum_level in shum_level_indices:
            # Create pandas dataframes for accessing the data easily
            shum_df = pd.DataFrame(data=shum_data[current_slice, shum_level], index=data_lats, columns=data_lons)

            req_shum = shum_df[np.arange(index_8_lon1, index_8_lon2+2.5, 2.5)][index_8_lat1:index_8_lat2]

            # Calculation
            index_8_value += req_shum.mean().mean()

        ##############################################################################################################
        # Calculate indices 9,10 - Vorticity advection at 500 and 300hPa respectively averaged over 29-32N,33-37E.
        # Implication - Dynamic support. Changed area to 30N-32.5N, 32.5E-37.5E to avoid the need for unnecessary interpolation.
        ##############################################################################################################
        index_9_level = 500  # hPa
        index_9_lat1 = 30
        index_9_lat2 = 32.5
        index_9_lon1 = 32.5
        index_9_lon2 = 37.5

        uwind_level_index = list(uwind_levels).index(index_9_level)
        vwind_level_index = list(vwind_levels).index(index_9_level)

        # Create pandas dataframes for accessing the data easily
        uwind_df = pd.DataFrame(data=uwind_data[current_slice, uwind_level_index], index=data_lats, columns=data_lons)
        vwind_df = pd.DataFrame(data=vwind_data[current_slice, vwind_level_index], index=data_lats, columns=data_lons)

        # Calculate vorticity advection
        avor = mpcalc.vorticity(np.array(uwind_df), np.array(vwind_df), dx, dy, dim_order='yx')
        vort_adv = mpcalc.advection(avor, [np.array(uwind_df), np.array(vwind_df)], (dx, dy), dim_order='yx') * 1e9
        vort_adv_df = pd.DataFrame(data=np.array(vort_adv), index=data_lats, columns=data_lons)

        req_vort_adv = vort_adv_df[np.arange(index_9_lon1, index_9_lon2+2.5, 2.5)][index_9_lat1:index_9_lat2]

        # Calculation
        index_9_value = req_vort_adv.mean().mean()

        index_10_level = 300  # hPa

        uwind_level_index = list(uwind_levels).index(index_10_level)
        vwind_level_index = list(vwind_levels).index(index_10_level)

        # Create pandas dataframes for accessing the data easily
        uwind_df = pd.DataFrame(data=uwind_data[current_slice, uwind_level_index], index=data_lats, columns=data_lons)
        vwind_df = pd.DataFrame(data=vwind_data[current_slice, vwind_level_index], index=data_lats, columns=data_lons)

        # Calculate vorticity advection
        avor = mpcalc.vorticity(np.array(uwind_df), np.array(vwind_df), dx, dy, dim_order='yx')
        vort_adv = mpcalc.advection(avor, [np.array(uwind_df), np.array(vwind_df)], (dx, dy), dim_order='yx') * 1e9
        vort_adv_df = pd.DataFrame(data=np.array(vort_adv), index=data_lats, columns=data_lons)

        req_vort_adv = vort_adv_df[np.arange(index_9_lon1, index_9_lon2+2.5, 2.5)][index_9_lat1:index_9_lat2]

        # Calculation
        index_10_value = req_vort_adv.mean().mean()

        ##############################################################################################################
        # Calculate indices 11,12 - vwind/uwind at 500 and 700hPa respectively, averaged 5x5 around 30N,35E.
        # Implication - Northward wind deflection from zonality.
        ##############################################################################################################
        index_11_level = 500  # hPa
        index_11_lat1 = 27.5
        index_11_lat2 = 32.5
        index_11_lon1 = 32.5
        index_11_lon2 = 37.5

        vwind_level_index = list(vwind_levels).index(index_11_level)
        uwind_level_index = list(uwind_levels).index(index_11_level)

        # Create pandas dataframes for accessing the data easily
        vwind_df = pd.DataFrame(data=vwind_data[current_slice, vwind_level_index], index=data_lats, columns=data_lons)
        uwind_df = pd.DataFrame(data=uwind_data[current_slice, uwind_level_index], index=data_lats, columns=data_lons).replace(0, 0.001)
        req_vwind = vwind_df[np.arange(index_11_lon1, index_11_lon2+2.5, 2.5)][index_11_lat1:index_11_lat2]
        req_uwind = uwind_df[np.arange(index_11_lon1, index_11_lon2+2.5, 2.5)][index_11_lat1:index_11_lat2]

        # Calculation
        index_11_value = (req_vwind / req_uwind).mean().mean()

        index_12_level = 700  # hPa

        vwind_level_index = list(vwind_levels).index(index_12_level)
        uwind_level_index = list(uwind_levels).index(index_12_level)

        # Create pandas dataframes for accessing the data easily
        vwind_df = pd.DataFrame(data=vwind_data[current_slice, vwind_level_index], index=data_lats, columns=data_lons)
        uwind_df = pd.DataFrame(data=uwind_data[current_slice, uwind_level_index], index=data_lats, columns=data_lons).replace(0, 0.001)
        req_vwind = vwind_df[np.arange(index_11_lon1, index_11_lon2+2.5, 2.5)][index_11_lat1:index_11_lat2]
        req_uwind = uwind_df[np.arange(index_11_lon1, index_11_lon2+2.5, 2.5)][index_11_lat1:index_11_lat2]

        # Calculation
        index_12_value = (req_vwind / req_uwind).mean().mean()

        ##############################################################################################################
        # Calculate index 13 - Vorticity at 500hPa, averaged 5x5 around 30N,35E. Implication - Upper-level cyclonicity.
        ##############################################################################################################
        index_13_level = 500  # hPa
        index_13_lat1 = 27.5
        index_13_lat2 = 32.5
        index_13_lon1 = 32.5
        index_13_lon2 = 37.5

        uwind_level_index = list(uwind_levels).index(index_13_level)
        vwind_level_index = list(vwind_levels).index(index_13_level)

        # Create pandas dataframes for accessing the data easily
        uwind_df = pd.DataFrame(data=uwind_data[current_slice, uwind_level_index], index=data_lats, columns=data_lons)
        vwind_df = pd.DataFrame(data=vwind_data[current_slice, vwind_level_index], index=data_lats, columns=data_lons)

        # Calculate vorticity
        avor = mpcalc.vorticity(np.array(uwind_df), np.array(vwind_df), dx, dy, dim_order='yx')
        vort_df = pd.DataFrame(data=np.array(avor), index=data_lats, columns=data_lons)
        req_vort = vort_df[np.arange(index_13_lon1, index_13_lon2+2.5, 2.5)][index_13_lat1:index_13_lat2]

        # Calculation
        index_13_value = req_vort.mean().mean()

        ##############################################################################################################
        # Calculate index 14 - Upper-level Geopotential Height anomaly (with respect to the monthly avg. 1980-2010)
        # at 500hPa, averaged 5x5 around 22.5N,27.5E. Implication - Amplitude of upper trough over most significant location.
        ##############################################################################################################
        index_14_level = 500  # hPa
        index_14_lat1 = 20
        index_14_lat2 = 25
        index_14_lon1 = 25
        index_14_lon2 = 30

        geop_level_index = list(geop_levels).index(index_14_level)
        geop_long_term_level_index = list(geop_500_long_monthly_term_levels).index(index_14_level)

        # Create pandas dataframes for accessing the data easily
        geop_df = pd.DataFrame(data=geop_data[current_slice, geop_level_index], index=data_lats, columns=data_lons)
        req_geop = geop_df[np.arange(index_14_lon1, index_14_lon2+2.5, 2.5)][index_14_lat1:index_14_lat2]
        current_month = int(str(data_string_time[current_slice])[5:7])-1
        geop_long_term_df = pd.DataFrame(data=geop_500_long_monthly_term_data[current_month, geop_long_term_level_index],
                                         index=data_lats, columns=data_lons)
        req_geop_long_term = geop_long_term_df[np.arange(index_14_lon1, index_14_lon2+2.5, 2.5)][index_14_lat1:index_14_lat2]

        # Calculation
        index_14_value = (req_geop - req_geop_long_term).mean().mean()

        ##############################################################################################################
        # Calculate index 15 - upper level wind speed wind at 500hPa at 30N,35E. Implication - Combination of factors.
        ##############################################################################################################
        index_15_level = 500  # hPa
        index_15_lat = 27.5
        index_15_lon = 32.5

        uwind_level_index = list(uwind_levels).index(index_15_level)
        vwind_level_index = list(vwind_levels).index(index_15_level)

        # Create pandas dataframes for accessing the data easily
        uwind_df = pd.DataFrame(data=uwind_data[current_slice, uwind_level_index], index=data_lats, columns=data_lons)
        vwind_df = pd.DataFrame(data=vwind_data[current_slice, vwind_level_index], index=data_lats, columns=data_lons)
        req_uwind = uwind_df[index_15_lon][index_15_lat]
        req_vwind = vwind_df[index_15_lon][index_15_lat]

        # Calculation
        index_15_value = np.sqrt(req_uwind**2 + req_vwind**2)

        ##############################################################################################################
        # Calculate index 16 - Vertical temperature difference, 850-500hPa, averaged 5x5 around 30N,35E.
        # Implication - Static instability, Represents CAPE.
        ##############################################################################################################
        index_16_level_1 = 850  # hPa
        index_16_level_2 = 500  # hPa
        index_16_lat1 = 27.5
        index_16_lat2 = 32.5
        index_16_lon1 = 32.5
        index_16_lon2 = 37.5

        temperature_level_index_1 = list(temperature_levels).index(index_16_level_1)
        temperature_level_index_2 = list(temperature_levels).index(index_16_level_2)

        # Create pandas dataframes for accessing the data easily
        temperature_df_1 = pd.DataFrame(data=temperature_data[current_slice, temperature_level_index_1], index=data_lats, columns=data_lons)
        temperature_df_2 = pd.DataFrame(data=temperature_data[current_slice, temperature_level_index_2], index=data_lats, columns=data_lons)
        req_temperature_1 = temperature_df_1[np.arange(index_16_lon1, index_16_lon2+2.5, 2.5)][index_16_lat1:index_16_lat2]
        req_temperature_2 = temperature_df_2[np.arange(index_16_lon1, index_16_lon2+2.5, 2.5)][index_16_lat1:index_16_lat2]

        # Calculation
        index_16_value = (req_temperature_1 - req_temperature_2).mean().mean()

        ##############################################################################################################
        # Calculate index 17 - Propagation speed of upper cyclonic center at 500hPa, over 23-37N, 25-38E.
        # Implication - Reducing effect of speed.
        # Calculate index 18 - Intensification rate of upper cyclonic center at 500hPa, over 23-37N, 25-38E.
        # Implication - Enhancing effect of intensification.
        # Calculate index 19 - Relative location of maximum upper vorticity at 500hPa, over 23-37N, 25-38E.
        # Implication - Optimal location is expected.
        # Changed area to 22.5N-37.5N, 25E-37.5E to avoid the need for unnecessary interpolation.
        ##############################################################################################################
        index_17_level = 500  # hPa
        index_17_lat1 = 22.5
        index_17_lat2 = 37.5
        index_17_lon1 = 25
        index_17_lon2 = 37.5

        uwind_level_index = list(uwind_levels).index(index_17_level)
        vwind_level_index = list(vwind_levels).index(index_17_level)

        # Create pandas dataframes for accessing the data easily
        uwind_df = pd.DataFrame(data=uwind_data[current_slice, uwind_level_index], index=data_lats, columns=data_lons)
        vwind_df = pd.DataFrame(data=vwind_data[current_slice, vwind_level_index], index=data_lats, columns=data_lons)
        uwind_previous_df = pd.DataFrame(data=uwind_data[current_slice-4, uwind_level_index], index=data_lats, columns=data_lons)
        vwind_previous_df = pd.DataFrame(data=vwind_data[current_slice-4, vwind_level_index], index=data_lats, columns=data_lons)

        # Calculate vorticity
        avor = mpcalc.vorticity(np.array(uwind_df), np.array(vwind_df), dx, dy, dim_order='yx')
        vort_df = pd.DataFrame(data=np.array(avor), index=data_lats, columns=data_lons)
        req_vort = vort_df[np.arange(index_17_lon1, index_17_lon2+2.5, 2.5)][index_17_lat1:index_17_lat2]
        max_vort = np.max(np.max(req_vort))
        geoloc_max_vort = req_vort[req_vort == max_vort].stack().index.tolist()[0]

        avor_prev = mpcalc.vorticity(np.array(uwind_previous_df), np.array(vwind_previous_df), dx, dy, dim_order='yx')
        vort_prev_df = pd.DataFrame(data=np.array(avor_prev), index=data_lats, columns=data_lons)
        req_vort_prev = vort_prev_df[np.arange(index_17_lon1, index_17_lon2+2.5, 2.5)][index_17_lat1:index_17_lat2]
        max_vort_prev = np.max(np.max(req_vort_prev))
        geoloc_max_vort_prev = req_vort_prev[req_vort_prev == max_vort_prev].stack().index.tolist()[0]

        # Calculation
        index_17_value = great_circle(geoloc_max_vort, geoloc_max_vort_prev).kilometers / 24
        index_18_value = (max_vort - max_vort_prev) / 24

        # In order to get a relative location with one number, I start counting from top-left, down to bottom left, continuing to top of
        # second column from left and to bottom of second column, etc., until I get to the bottom of the rightmost column.
        # To do that, I need the actual numerals of the index and column names (lat, lon).
        geoloc_lat_index = req_vort.index.get_loc(geoloc_max_vort[0])
        geoloc_lon_index = req_vort.columns.get_loc(geoloc_max_vort[1])
        num_of_lats = req_vort.shape[0]  # number of rows
        index_19_value = geoloc_lat_index + (num_of_lats * geoloc_lon_index)

        final_list.append([str(data_string_time[current_slice]), index_1_value, index_2_value, index_3_value, index_4_value, index_5_value,
                           index_6_value, index_7_value, index_8_value, index_9_value, index_10_value, index_11_value, index_12_value,
                           index_13_value, index_14_value, index_15_value, index_16_value, index_17_value, index_18_value, index_19_value, ])

        # print()

# Create an new Excel file and add a worksheet.
workbook = xlsxwriter.Workbook('Indices_for_RST_evaluation.xlsx') #, {'nan_inf_to_errors': True})
worksheet = workbook.add_worksheet()

total_cols = len(final_list[1])
for row in range(len(final_list)):
    for col in range(total_cols):
        worksheet.write(row, col, final_list[row][col])

workbook.close()

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
        # cs = rst_map.contourf(x, y, vorticity_df.iloc[lat1_index:lat2_index + 1, lon1_index:lon2_index + 1], 15,
        #                       cmap='coolwarm')
        # rst_map.contour(x, y, geop_df.iloc[lat1_index:lat2_index + 1, lon1_index:lon2_index + 1], 15,
        #                 linewidths=1, colors='black')
        # # plt.quiver(x, y, uwind_df, vwind_df, pivot='middle')
        # plt.colorbar(cs)
        # plt.show()
