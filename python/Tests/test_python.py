import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

files_path = 'D:/DB/Era_Interim'
req_year = '2016'
req_month = '12'
req_day = '19'
req_hour = '00'
# levels(hPa): 0=100 1=150 2=200 3=250 4=300 5=350 6=400 7=450 8=500 9=550
#              10=600 11=650 12=700 13=750 14=800 15=850 16=900 17=950 18=1000
levels = range(100,1001, 50)
current_level = 15

# Create a histogram for the low resolution data
# Read the file
directory_pre = files_path + '/' + req_year + '/' + req_year + '-' + req_month + '/' + req_day + '/' \
                + req_year + '-' + req_month + '-' + req_day + '_' + req_hour + 'Z_'
directory_post = '_isobaric.nc'

LWC_low_res_nc = Dataset(directory_pre + 'LWC' + directory_post)
LWC_low_res_data = LWC_low_res_nc.variables['lwc'][:]
LWC_low_res_level_data = np.squeeze(LWC_low_res_data[0, current_level, :, :])
LWC_low_res_1D_array = np.sort(LWC_low_res_level_data.flatten())
print(LWC_low_res_1D_array.max())
print(LWC_low_res_1D_array.mean())
print(LWC_low_res_1D_array.std())

fig = plt.figure()
ax = fig.add_subplot(221)

numBins = 50
ax.hist(LWC_low_res_1D_array[-30:-1], numBins, color='green', alpha=0.8)

lats_low = LWC_low_res_nc.variables['latitude'][:]
lons_low = LWC_low_res_nc.variables['longitude'][:]
latbounds = [ lats_low[0], lats_low[-1]]
lonbounds = [ lons_low[0], lons_low[-1]]

# Draw low res map
ax = fig.add_subplot(223)
my_map = Basemap(projection='mill',
                 lat_0=lats_low.min(),
                 lon_0=lons_low.min(),
                 lat_1=lats_low.max(),
                 lon_1=lons_low.max(),
                 llcrnrlat=lats_low.min(), urcrnrlat=lats_low.max(),
                 llcrnrlon=lons_low.min(), urcrnrlon=lons_low.max(),
                 ax=ax
                 )
lon, lat = np.meshgrid(lons_low, lats_low)
xi, yi = my_map(lon, lat)
vmin = LWC_low_res_level_data.min()
vmax = LWC_low_res_level_data.max()
cs = my_map.pcolor(xi, yi, np.squeeze(LWC_low_res_level_data), vmin=vmin, vmax=vmax)

# Add Grid Lines and Geography
# hPa level
my_map.drawparallels(np.arange(lats_low.min(), lats_low.max(), 10.), labels=[1, 0, 0, 0], fontsize=8)
my_map.drawmeridians(np.arange(lons_low.min(), lons_low.max(), 10.), labels=[0, 0, 0, 1], fontsize=8)
# Add Coastlines, States, and Country Boundaries
# my_map.fillcontinents()
my_map.drawcoastlines()
my_map.drawstates()
my_map.drawcountries()

cbar = fig.colorbar(cs, orientation='horizontal')
cbar.set_label('g/m3')

# Create a histogram for the high resolution data
# Read the file
CLWC_high_res_nc = Dataset('C:/Users/hatzv/Documents/Geography/Research_help/Icing/meteo.icing/python/ERA-Interim_specific_LWC_Dec-2016.nc')
SHUM_high_res_nc = Dataset('C:/Users/hatzv/Documents/Geography/Research_help/Icing/meteo.icing/python/ERA-Interim_specific_humidity_Dec-2016.nc')
TEMP_high_res_nc = Dataset('C:/Users/hatzv/Documents/Geography/Research_help/Icing/meteo.icing/python/ERA-Interim_Temperature_Dec-2016.nc')
lats_high = CLWC_high_res_nc.variables['latitude'][:]
lons_high = CLWC_high_res_nc.variables['longitude'][:]

# latitude lower and upper index
latli = np.argmin(np.abs(lats_high - latbounds[0]))
latui = np.argmin(np.abs(lats_high - latbounds[1]))

# longitude lower and upper index
lonli = np.argmin(np.abs(lons_high - lonbounds[0]))
lonui = np.argmin(np.abs(lons_high - lonbounds[1]))

time = (int(req_day)-1)*4 + (int(req_hour)/6)
CLWC_high_res_level_data = np.squeeze(CLWC_high_res_nc.variables['clwc'][time, current_level, latli:latui , lonli:lonui])
SHUM_high_res_level_data = np.squeeze(SHUM_high_res_nc.variables['q'][time, current_level, latli:latui , lonli:lonui])
TEMP_high_res_level_data = np.squeeze(TEMP_high_res_nc.variables['t'][time, current_level, latli:latui , lonli:lonui])

pressure = levels[current_level] * 100  # Hectopascal to Pascal
Rd = 287  # J K-1 Kg-1
epsilon = 0.622  # Rd/Rv approximately in Earth's atmosphere

omega_grid = SHUM_high_res_level_data / (1 - SHUM_high_res_level_data)
virtual_t_grid = TEMP_high_res_level_data * (epsilon + omega_grid) / (epsilon * (1 + omega_grid))
air_density_grid = pressure / (Rd * virtual_t_grid)
LWC_high_res_level_data = CLWC_high_res_level_data * air_density_grid * 1000  # *1000 o get to g/m3 instead of Kg/m3

LWC_high_res_1D_array = np.sort(LWC_high_res_level_data.flatten())

print(LWC_high_res_1D_array.max())
print(LWC_high_res_1D_array.mean())
print(LWC_high_res_1D_array.std())

#fig = plt.figure()
bx = fig.add_subplot(222)

numBins = 50
bx.hist(LWC_high_res_1D_array[-1000:-1], numBins, color='green', alpha=0.8)

# Draw low res map
ax = fig.add_subplot(224)
my_map = Basemap(projection='mill',
                 lat_0=lats_high.min(),
                 lon_0=lons_high.min(),
                 lat_1=lats_high.max(),
                 lon_1=lons_high.max(),
                 llcrnrlat=lats_high.min(), urcrnrlat=lats_high.max(),
                 llcrnrlon=lons_high.min(), urcrnrlon=lons_high.max(),
                 ax=ax
                 )
lon, lat = np.meshgrid(lons_high, lats_high)
xi, yi = my_map(lon, lat)
vmin = LWC_high_res_level_data.min()
vmax = LWC_high_res_level_data.max()
cs = my_map.pcolor(xi, yi, np.squeeze(LWC_high_res_level_data), vmin=vmin, vmax=vmax)

# Add Grid Lines and Geography
# hPa level
my_map.drawparallels(np.arange(lats_high.min(), lats_high.max(), 10.), labels=[1, 0, 0, 0], fontsize=8)
my_map.drawmeridians(np.arange(lons_high.min(), lons_high.max(), 10.), labels=[0, 0, 0, 1], fontsize=8)
# Add Coastlines, States, and Country Boundaries
# my_map.fillcontinents()
my_map.drawcoastlines()
my_map.drawstates()
my_map.drawcountries()

cbar = fig.colorbar(cs, orientation='horizontal')
cbar.set_label('g/m3')


plt.show()
