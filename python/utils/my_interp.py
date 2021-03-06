from mpl_toolkits import basemap
import numpy as np


def my_interp(orig_data, lats, lons, interp_resolution, interp_method=3):
    [lon_dense, lat_dense] = np.meshgrid(np.arange(lons[0], lons[-1] + interp_resolution, interp_resolution),
                                         np.arange(lats[0], lats[-1] + interp_resolution, interp_resolution))

    interp_data = basemap.interp(np.squeeze(orig_data),
                                 lons,
                                 lats,
                                 lon_dense,
                                 lat_dense,
                                 order=interp_method)
    interp_lats = np.squeeze(lat_dense[:, 1])
    interp_lons = np.squeeze(lon_dense[1, :])

    return interp_data, interp_lats, interp_lons
