# This program creates a db with the 100 values for each day.
# The values are for SLP, air-temp, uwind and vwind at 850hPa and for 25 grid points in the area 27.5N-37.5N, 30E-40E.
# The values are saved in pkl, both as original values and normalized values

import pandas as pd
import numpy as np
from scipy.stats import zscore
import pickle

# My imports
from python.utils.read_nc_files import read_nc_files


hour = 12  # xxZ of each day

data_directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Data/Rain Data/NCEP/'

# Read the data files for this year
slp_filename = data_directory + 'SLP/SLP_1991-2008.nc'
temperature_filename = data_directory + 'temperature/temperature_1991-2008_850hPa.nc'
uwind_filename = data_directory + 'uwind/uwind_1991-2008_850hPa.nc'
vwind_filename = data_directory + 'vwind/vwind_1991-2008_850hPa.nc'

start_time = int(hour/6)
temperature_data, _, _, _, _, data_string_time = read_nc_files(temperature_filename, start_time=start_time, delta_time=4)
uwind_data, _, _, _, _, _ = read_nc_files(uwind_filename, start_time=start_time, delta_time=4)
vwind_data, _, _, _, _, _ = read_nc_files(vwind_filename, start_time=start_time, delta_time=4)
slp_data, _, _, _, _ = read_nc_files(slp_filename, start_time=start_time, delta_time=4)

# Change the data_string_time from Datetime object to a string so I can remove Feb 29s (because they are not in the rain station data.
index_time = list(pd.to_datetime(data_string_time).strftime('%Y%m%d'))
temp_index_time = index_time[:]

ncep_orig_values_array = np.zeros([len(index_time), 100])
counter = 0
counter_num_of_feb_29 = 0
for current_date in temp_index_time:
    if current_date.endswith('0229'):
        index_time.remove(current_date)
        counter_num_of_feb_29 += 1
    else:
        ncep_orig_values_array[counter][0:25] = slp_data[counter + counter_num_of_feb_29].reshape((1, 25))
        ncep_orig_values_array[counter][25:50] = temperature_data[counter + counter_num_of_feb_29][0].reshape((1, 25))
        ncep_orig_values_array[counter][50:75] = uwind_data[counter + counter_num_of_feb_29][0].reshape((1, 25))
        ncep_orig_values_array[counter][75:100] = vwind_data[counter + counter_num_of_feb_29][0].reshape((1, 25))
        counter += 1

ncep_orig_values_array = ncep_orig_values_array[:counter]
# Create pandas dataframes for accessing the data easily
ncep_orig_vals_df = pd.DataFrame(data=ncep_orig_values_array,
                                 index=index_time,
                                 columns=range(100))
ncep_zscore_vals_df = ncep_orig_vals_df.apply(zscore)


output_directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Data/Rain Data/pkls/'
output_filename = 'ncep_orig_vals_df_1991-2008.pkl'
with open(output_directory + output_filename, 'wb') as output:
    pickle.dump(ncep_orig_vals_df, output, pickle.HIGHEST_PROTOCOL)

output_filename = 'ncep_zscore_vals_df_1991-2008.pkl'
with open(output_directory + output_filename, 'wb') as output:
    pickle.dump(ncep_zscore_vals_df, output, pickle.HIGHEST_PROTOCOL)
