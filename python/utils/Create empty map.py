import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap
import python.Plot_RSTs.plot_RST_constants as consts


map_figure, map_axis = plt.subplots(figsize=(10, 10))

# Create the map object
rst_map = Basemap(llcrnrlon=30,
                  llcrnrlat=26,
                  urcrnrlon=40,
                  urcrnrlat=36,
                  projection='merc',
                  resolution='i',
                  ax=map_axis)
rst_map.drawcoastlines(linewidth=2)
rst_map.drawparallels(np.arange(consts.map_lat1, consts.map_lat2, 1), labels=[1, 0, 0, 0], fontsize=8, color='gray', dashes=[1,4])
rst_map.drawmeridians(np.arange(consts.map_lon1, consts.map_lon2, 1), labels=[0, 0, 0, 1], fontsize=8, color='gray', dashes=[1,4])

plt.show()


