# This function reads an NetCDF file and return the data, lats, lons, time and string time
# The input start_time is for the first time index to read and the delta_time skips that many
# time indices between each field read.
# Because it is easier to work with ascending lat values, sometimes it is easier to flip them.

from netCDF4 import Dataset, num2date
import numpy as np


def read_nc_files(filename, start_time=0, delta_time=1, flip_lats=True):
    level_str, lon_str, lat_str, time_str, data_str = [], [], [], [], []

    file_nc = Dataset(filename)
    variable_list = list(file_nc.variables.keys())
    for current_var in range(len(variable_list)):
        variable_name = variable_list[current_var]
        if variable_name.startswith('lon'):
            lon_str = variable_name
        elif variable_name.startswith('lat'):
            lat_str = variable_name
        elif variable_name.startswith('time'):
            time_str = variable_name
        elif variable_name.startswith('level'):
            level_str = variable_name
        elif variable_name.startswith('climatology_bounds') or variable_name.startswith('valid_yr_count'):
            # Encountered this in the long term monthely mean files.
            pass
        else:
            data_str = variable_name

    if (lon_str == []) or (lat_str == []) or (time_str == []) or (data_str == []):
        print('Something is wrong whle opening ' + filename)

    # flipping the data and lats because nc files come with descending lats
    if flip_lats:
        dims = file_nc.variables[data_str].dimensions
        lat_dim_idx = list(dims).index(lat_str)
        file_data = np.flip(file_nc.variables[data_str][start_time::delta_time], lat_dim_idx)
        file_lats = np.flip(file_nc.variables[lat_str][:], 0)
    else:
        file_data = file_nc.variables[data_str][start_time::delta_time]
        file_lats = file_nc.variables[lat_str][:]

    file_lons = file_nc.variables[lon_str][:]
    file_indexed_time = file_nc.variables[time_str][start_time::delta_time]
    file_string_time = num2date(file_indexed_time[:], file_nc.variables[time_str].units)
    if level_str:
        file_level = file_nc.variables[level_str][:]
        return file_data, file_level, file_lats, file_lons, file_indexed_time, file_string_time
    else:
        return file_data, file_lats, file_lons, file_indexed_time, file_string_time
