# This program creates a db with the 100 values for each day.
# The values are for SLP, air-temp, uwind and vwind at 850hPa and for 25 grid points in the area 27.5N-37.5N, 30E-40E.
# The values are saved in pkl, both as original values and normalized values

import pandas as pd
import numpy as np
from scipy.stats import zscore
import pickle

# My imports
from python.utils.read_nc_files import read_nc_files


hour = 12 # xxZ of each day
start_year = 1991
end_year = 2008

data_directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Data/Rain Data/NCEP/'

# Read the data files for this year
slp_filename = data_directory + 'SLP/SLP_1991-2008.nc'
temperature_filename = data_directory + 'temperature/temperature_1991-2008_850hPa.nc'
uwind_filename = data_directory + 'uwind/uwind_1991-2008_850hPa.nc'
vwind_filename = data_directory + 'vwind/vwind_1991-2008_850hPa.nc'

start_time = int(hour/6)
temperature_data, levels, data_lats, data_lons, data_time, data_string_time = read_nc_files(temperature_filename, start_time=start_time, delta_time=4)
uwind_data, _, _, _, _, _ = read_nc_files(uwind_filename, start_time=start_time, delta_time=4)
vwind_data, _, _, _, _, _ = read_nc_files(vwind_filename, start_time=start_time, delta_time=4)
slp_data, _, _, _, _ = read_nc_files(slp_filename, start_time=start_time, delta_time=4)

ncep_orig_values_list = np.zeros([len(data_string_time), 100])
counter = 0
for current_date in data_string_time:
    ncep_orig_values_list[counter][0:25] = slp_data[counter].reshape((1, 25))
    ncep_orig_values_list[counter][25:50] = temperature_data[counter][0].reshape((1, 25))
    ncep_orig_values_list[counter][50:75] = uwind_data[counter][0].reshape((1, 25))
    ncep_orig_values_list[counter][75:100] = vwind_data[counter][0].reshape((1, 25))
    counter += 1

# Create pandas dataframes for accessing the data easily
ncep_orig_vals_df = pd.DataFrame(data=ncep_orig_values_list, index=data_string_time, columns=range(100))
ncep_zscore_vals_df = ncep_orig_vals_df.apply(zscore)


output_directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Data/Rain Data/pkls/'
output_filename = 'ncep_orig_vals_df_1991-2008.pkl'
with open(output_directory + output_filename, 'wb') as output:
    pickle.dump(ncep_orig_vals_df, output, pickle.HIGHEST_PROTOCOL)

output_filename = 'ncep_zscore_vals_df_1991-2008.pkl'
with open(output_directory + output_filename, 'wb') as output:
    pickle.dump(ncep_zscore_vals_df, output, pickle.HIGHEST_PROTOCOL)