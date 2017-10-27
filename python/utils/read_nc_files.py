# This function reads an NetCDF file and return the data, lats, lons, time and string time
# The input start_time is for the first time index to read and the delta_time skips that many
# time indices between each field read.
# Because it is easier to work with ascending lat values, sometimes it is easier to flip them.

from netCDF4 import Dataset, num2date
import numpy as np


def read_nc_files(filename, var_name, start_time=0, delta_time=1, flip_lats=True):
    file_nc = Dataset(filename)

    # flipping the data and lats because nc files come with descending lats
    if flip_lats:
        file_data = np.flip(np.squeeze(file_nc.variables[var_name][start_time:-1:delta_time, :, :]), 1)
        file_lats = np.flip(file_nc.variables['lat'][:], 0)
    else:
        file_data = np.squeeze(file_nc.variables[var_name][start_time:-1:delta_time, :, :])
        file_lats = file_nc.variables['lat'][:]

    file_lons = file_nc.variables['lon'][:]
    file_indexed_time = file_nc.variables['time'][start_time:-1:delta_time]
    file_string_time = num2date(file_indexed_time[:], file_nc.variables['time'].units)

    return file_data, file_lats, file_lons, file_indexed_time, file_string_time
