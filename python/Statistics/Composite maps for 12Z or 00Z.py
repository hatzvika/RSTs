import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

import python.Plot_RSTs.plot_RST_constants as consts
from python.Plot_RSTs.Plot_RSTs import PlotRSTs
from python.Plot_RSTs.Calculate_RST import Calculate_RST

# This script creates the composite maps comprising all RST types of 00Z or 12Z
maps_for_12z = False  # False = 00Z

#############################################
# Which DB to create a composite map for
#############################################
req_DB = "NCEP"
# req_DB = "ERA"
# req_DB = "ERA_2_5"

lons = np.arange(20, 50.5, 0.5)
lats = np.arange(10, 50.5, 0.5)

current_year = 1979 # This is the starting year. Later it will be changed in the main loop

if maps_for_12z:
    z_hour = 12
else:
    z_hour = 0

rsts_cases_counter = 0
composite_slp_map = np.zeros([81, 61])
composite_geostrophic_map = np.zeros([81, 61])

# Main loop to collect all the single match map for the final composite map
for current_year in range(1979, 2017):
    print(current_year)

    # Get the PlotRST instance for the current year
    if req_DB == "NCEP":
        plotRSTs_instance = PlotRSTs('NCEP', current_year, z_hour=z_hour)
    elif req_DB == "ERA":
        plotRSTs_instance = PlotRSTs('ERA_Interim', current_year, z_hour=z_hour)
    else:  # ERA_2_5
        plotRSTs_instance = PlotRSTs('ERA Int 2.5', current_year, z_hour=z_hour)

    data_string_array = plotRSTs_instance.data_string_time

    for current_day in range (np.size(data_string_array,0)):
        # Calculate the maps for the current date
        _rst_class, slp_map, geostrophic_vorticity_map = plotRSTs_instance.calculate_maps_data(str(data_string_array[current_day]),
                                                                                               use_interpolation=True,
                                                                                               data_to_map="Geostrophic Vorticity",
                                                                                               show_dots=False,
                                                                                               only_longest_separate=True,
                                                                                               polyfit_rst=False)

        if _rst_class != consts.rst_orientation_no_rst:
            rsts_cases_counter = rsts_cases_counter + 1

            # Add the current date maps to the composite map
            composite_slp_map = composite_slp_map + slp_map
            composite_geostrophic_map = composite_geostrophic_map +geostrophic_vorticity_map

    print(rsts_cases_counter)

print(rsts_cases_counter)

# Divide the composite by the number of cases to get the average values
composite_slp_map = composite_slp_map / rsts_cases_counter
composite_geostrophic_map = composite_geostrophic_map / rsts_cases_counter

# Display the maps
# Create the map object
rst_map = Basemap(llcrnrlon=consts.map_lon1,
                  llcrnrlat=consts.map_lat1,
                  urcrnrlon=consts.map_lon2,
                  urcrnrlat=consts.map_lat2,
                  projection='merc',
                  resolution='i')
rst_map.drawcoastlines()
rst_map.drawparallels(np.arange(consts.map_lat1, consts.map_lat2, 2.5), labels=[1, 0, 0, 0], fontsize=8)
rst_map.drawmeridians(np.arange(consts.map_lon1, consts.map_lon2, 2.5), labels=[0, 0, 0, 1], fontsize=8)
# map_axis.set(cmap = plt.cm.get_cmap('Blues_r')) #colormap = 'coolwarm',

# Build map title
plot_title = str(z_hour) + "Z"
plt.title(plot_title)

# Calculate the meshes for the maps and plot SLP contours (always)
lon1_index = int(np.where(lons <= consts.map_lon1)[0][-1])
lon2_index = int(np.where(lons >= consts.map_lon2)[0][-1])
lat1_index = int(np.where(lats <= consts.map_lat1)[0][-1])
lat2_index = int(np.where(lats >= consts.map_lat2)[0][-1])
mesh_lons, mesh_lats = np.meshgrid(lons[lon1_index:lon2_index + 1], lats[lat1_index:lat2_index + 1])

x, y = rst_map(mesh_lons, mesh_lats)
min_slp = int(np.floor(composite_slp_map.min()))
max_slp = int(np.ceil(composite_slp_map.max()))
rst_map.contour(x, y, composite_slp_map[lat1_index:lat2_index + 1, lon1_index:lon2_index + 1], range(min_slp, max_slp, 200), linewidths=1.5,
                colors='k')

# Display the geostrophic vorticity map if needed
subset_map = composite_geostrophic_map[lat1_index:lat2_index + 1, lon1_index:lon2_index + 1]

rst_map.contour(x, y, subset_map, 10, linewidths=0.5, colors='k')
max_value = subset_map.max()
min_value = subset_map.min()
if min_value < 0 and max_value > 0:
    if max_value > abs(min_value):
        min_value = -max_value
    else:
        max_value = abs(min_value)
cs = rst_map.contourf(x, y, subset_map, 10, cmap=plt.cm.get_cmap('coolwarm'), vmin=min_value, vmax=max_value)

#Draw the average RST
# Find Red Sea Trough
calc_rst_obj = Calculate_RST(composite_slp_map, 0.5, consts.slp_check_distance, lats, lons) # 0.5 is the interpolated resolution

# Find the RSTs orientations and polyfit them + get the daily_rst_classification (unless rst conditions are not met
trough_coordinates_matrix, stam, stam1 = calc_rst_obj.get_trough_coords_matrix(only_long_separate_RSTs=True, polyfit_rst=True)

# Draw the RSTs, if any
for current_RST in range(0, int(np.size(trough_coordinates_matrix, 1) / 2)):
    # Get the current trough columns from the trough matrix
    trough_coords = trough_coordinates_matrix[:, 2 * current_RST:2 * current_RST + 2]
    # remove all zeros from current RST
    trough_coords = trough_coords[~(trough_coords == 0).all(1)]
    x_trough = trough_coords[:, 1]
    y_trough = trough_coords[:, 0]

    lat_map, lon_map = rst_map(x_trough, y_trough)
    rst_map.plot(lat_map, lon_map, marker=None, linewidth=6, color='black')
    rst_map.plot(lat_map, lon_map, marker=None, linewidth=4, color='yellow')

# Draw box3 and the 2 points
lat_array_region = [consts.rst_square3_lat1,
                    consts.rst_square3_lat1,
                    consts.rst_square3_lat2,
                    consts.rst_square3_lat2,
                    consts.rst_square3_lat1]
lon_array_region = [consts.rst_square3_lon1,
                    consts.rst_square3_lon2,
                    consts.rst_square3_lon2,
                    consts.rst_square3_lon1,
                    consts.rst_square3_lon1]
x_region, y_region = rst_map(lon_array_region, lat_array_region)
rst_map.plot(x_region, y_region, marker=None, linewidth=3, color='black')

# Draw the central red line
x_line, y_line = rst_map([consts.central_cross_line_lon, consts.central_cross_line_lon],
                         [consts.central_cross_line_lat1, consts.central_cross_line_lat2])
rst_map.plot(x_line, y_line, marker=None, linewidth=6, color='black')
rst_map.plot(x_line, y_line, marker=None, linewidth=3, color='red')

# Add Colorbar
plt.colorbar(cs)
plt.show()


