import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# My imports
import python.Plot_RSTs.plot_RST_constants as consts
from python.utils.read_nc_files import read_nc_files
from python.utils.my_interp import my_interp
from python.Plot_RSTs.Calculate_RST import Calculate_RST

class PlotRSTs ():
    def __init__(self, model_data='NCEP', data_year=1984):
        self.model_data = model_data

        # Read the data files
        (self.orig_slp_data,
         self.orig_uwind_data,
         self.orig_vwind_data,
         self.orig_data_lats,
         self.orig_data_lons,
         self.data_time,
         self.data_string_time) = self._read_files(model_data, data_year)

        # Interpolate the data. All the data is interpolated and the
        # decision on which data to use is left outside the class
        (self.interp_slp_data,
         self.interp_data_lats,
         self.interp_data_lons) = self._interpolate_data(self.orig_slp_data)

        # is_interpolated is a flag used for determining if the current maps are
        # interpolated maps. This flag is set when calculate_maps_data is called
        # and it is used when creating the map display. The same goes for current_day
        self.is_interpolated = None
        self.current_day = None

        # Fields to be calculated and later shown on a map
        self.troughs_map, self.ridges_map = None, None
        self.vorticity_map = None
        self.geostrophic_vorticity_map = None
        self.trough_coordinates_matrix = None

        # The squares mean value for the RST condition met check
        self.mean_slp_square1 = None
        self.mean_slp_square2 = None
        self.mean_geos_vort_square3 = None

    # Read the data files
    def _read_files(self, model_data, data_year):
        if model_data == 'NCEP':
            slp_filename = consts.raw_data_prefix + "SLP/NCEP/SLP_NCEP_10-50N_20-50E_full_" + str(data_year) + ".nc"
            uwind_filename = consts.raw_data_prefix + "uwind/NCEP/uwind_NCEP_850hPa_10-50N_20-50E_full_" + str(data_year) + ".nc"
            vwind_filename = consts.raw_data_prefix + "vwind/NCEP/vwind_NCEP_850hPa_10-50N_20-50E_full_" + str(data_year) + ".nc"
        elif model_data == 'ERA_Interim':
            slp_filename = consts.raw_data_prefix + "SLP/ERA_Int/SLP_ERA_Int_10-50N_20-50E_full_" + str(data_year) + ".nc"
            uwind_filename = consts.raw_data_prefix + "uwind/ERA_Int/uwind_ERA_Int_850hPa_10-50N_20-50E_full_" + str(data_year) + ".nc"
            vwind_filename = consts.raw_data_prefix + "vwind/ERA_Int/vwind_ERA_Int_850hPa_10-50N_20-50E_full_" + str(data_year) + ".nc"
        elif model_data == 'ERA Int 2.5':
            slp_filename = consts.raw_data_prefix + "SLP/ERA_Int_2.5/SLP_ERA_Int_2.5_10-50N_20-50E_full_" + str(data_year) + ".nc"
            uwind_filename = consts.raw_data_prefix + "uwind/ERA_Int_2.5/uwind_ERA_Int_2.5_850hPa_10-50N_20-50E_full_" + str(data_year) + ".nc"
            vwind_filename = consts.raw_data_prefix + "vwind/ERA_Int_2.5/vwind_ERA_Int_2.5_850hPa_10-50N_20-50E_full_" + str(data_year) + ".nc"

        else:
            print("Wrong model_data name")
            return

        slp_data, orig_data_lats, orig_data_lons, data_time, data_string_time = read_nc_files(slp_filename, start_time=2, delta_time=4)
        uwind_data = read_nc_files(uwind_filename, start_time=2, delta_time=4)[0]
        vwind_data = read_nc_files(vwind_filename, start_time=2, delta_time=4)[0]

        return slp_data, uwind_data, vwind_data, orig_data_lats, orig_data_lons, data_time, data_string_time

    # Interpolation of the data
    def _interpolate_data(self, data_to_interpolate):
        # Find the interp lats and lons to create the temporary data holders.
        _, interp_data_lats, interp_data_lons = my_interp(data_to_interpolate[0, :, :],
                                                          self.orig_data_lats,
                                                          self.orig_data_lons,
                                                          consts.interp_resolution,
                                                          consts.interpolation_method)
        total_days = data_to_interpolate.shape[0]

        # Create interpolated files
        interp_data = np.zeros((total_days, interp_data_lats.shape[0], interp_data_lons.shape[0]))

        for current_day in range(total_days):
            interp_data[current_day, :, :] = my_interp(data_to_interpolate[current_day, :, :],
                                                           self.orig_data_lats,
                                                           self.orig_data_lons,
                                                           consts.interp_resolution,
                                                           consts.interpolation_method)[0]

        return interp_data, interp_data_lats, interp_data_lons

    def calculate_maps_data(self, current_day, use_interpolation, data_to_map, show_dots):
        self.is_interpolated = use_interpolation

        # Two ways to ask for a current day: by an integer counter from the file start or by a "DD-MM-YYYY" string
        if type(current_day) is int:
            self.current_day = current_day
        else:
            for loop_day in range(self.data_string_time.shape[0]):
                if str(self.data_string_time[loop_day]) == current_day:
                    self.current_day = loop_day
                    break

        # Decide data type flags according to data_to_map
        if data_to_map == 'Geostrophic Vorticity':
            show_geostrophic_vorticity = True
            show_vorticity = False
        elif data_to_map == 'Vorticity':
            show_geostrophic_vorticity = False
            show_vorticity = True
        else:
            print("Wrong data_to_map string")
            return


        # The Vorticity and Geostrophic vorticity need the original data for calculations
        # and only then will they be interpolated.
        slp_data = self.orig_slp_data[self.current_day, :, :].squeeze()
        uwind_data = self.orig_uwind_data[self.current_day, :, :].squeeze()
        vwind_data = self.orig_vwind_data[self.current_day, :, :].squeeze()
        total_lat = self.orig_data_lats.shape[0]
        total_lon = self.orig_data_lons.shape[0]
        lats = self.orig_data_lats
        lons = self.orig_data_lons
        resolution = lats[1] - lats[0]

        # Calculate Vorticity
        if show_vorticity:
            self.vorticity_map = self._calcualte_vorticity_maps(uwind_data, vwind_data, resolution, lats, total_lat, total_lon)
        else:
            self.vorticity_map = None

        # Calculate Geostrophic Vorticity
        if show_geostrophic_vorticity:
            # First calculate the map on the original dataset na donly then interpolate it
            self.geostrophic_vorticity_map = self._calcualte_geostrophic_vorticity_maps(slp_data, resolution, lats, total_lat, total_lon)
        else:
            self.geostrophic_vorticity_map = None

        # For the rest of the calculations (other then vorticity calculations, see above)
        # the data is interpolated if necessary.
        if self.is_interpolated:
            slp_data = self.interp_slp_data[self.current_day, :, :].squeeze()
            total_lat = self.interp_data_lats.shape[0]
            total_lon = self.interp_data_lons.shape[0]
            lats = self.interp_data_lats
            lons = self.interp_data_lons  # Calculate original data resolution for later use
            resolution = lats[1] - lats[0]

        orig_data_resolution = self.orig_data_lats[1] - self.orig_data_lats[0]

        # The following maps are needed for displaying the ridges and troughs using blue and red dots
        if show_dots:
            self.troughs_map, self.ridges_map = self._calculate_troughs_and_ridges_dots(slp_data, total_lat, total_lon)
        else:
            self.troughs_map, self.ridges_map = None, None

        # Find Red Sea Trough
        calc_rst_obj = Calculate_RST(slp_data, resolution, consts.slp_check_distance, lats, lons)
        self.trough_coordinates_matrix = calc_rst_obj.get_trough_coords_matrix(longest_only=consts.longest_only)

        # Calculate RST conditions in 3 boxes
        is_rst_condition_met = self._calculate_rst_conditions_in_boxes(slp_data, self.geostrophic_vorticity_map, lats, lons, resolution,
                                                                       show_geostrophic_vorticity, self.trough_coordinates_matrix)


        return is_rst_condition_met

    def _calculate_troughs_and_ridges_dots(self, slp_data, total_lat, total_lon):
        troughs_map = np.zeros((total_lat, total_lon))
        ridges_map = np.zeros((total_lat, total_lon))

        for current_lat in range(total_lat - 1):
            for current_lon in range(total_lon - 1):
                current_slp_value = slp_data[current_lat, current_lon]

                # Check for troughs and ridges on the lat axis
                if (current_lat > 1) and (current_lat < total_lat):
                    slp_value_1 = slp_data[current_lat - 1, current_lon]
                    slp_value_2 = slp_data[current_lat + 1, current_lon]
                    if (current_slp_value < slp_value_1) and (current_slp_value < slp_value_2):
                        troughs_map[current_lat, current_lon] = 1
                    elif (current_slp_value > slp_value_1) and (current_slp_value > slp_value_2):
                            ridges_map[current_lat, current_lon] = 1

                # Check for troughs and ridges on the lon axis
                if (current_lon > 1) and (current_lon < total_lon):
                    slp_value_1 = slp_data[current_lat, current_lon - 1]
                    slp_value_2 = slp_data[current_lat, current_lon + 1]
                    if (current_slp_value < slp_value_1) and (current_slp_value < slp_value_2):
                        troughs_map[current_lat, current_lon] = 1
                    elif (current_slp_value > slp_value_1) and (current_slp_value > slp_value_2):
                            ridges_map[current_lat, current_lon] = 1

                # Check for troughs and ridges on the diagonals
                if (current_lon > 1) and (current_lon < total_lon) and (current_lat > 1) and (current_lat < total_lat):
                    slp_value_1 = slp_data[current_lat - 1, current_lon - 1]
                    slp_value_2 = slp_data[current_lat + 1, current_lon + 1]
                    slp_value_3 = slp_data[current_lat + 1, current_lon - 1]
                    slp_value_4 = slp_data[current_lat - 1, current_lon + 1]
                    if ((current_slp_value < slp_value_1) and (current_slp_value < slp_value_2)) or ((current_slp_value < slp_value_3) and (current_slp_value < slp_value_4)):
                        troughs_map[current_lat, current_lon] = 1
                    elif ((current_slp_value > slp_value_1) and (current_slp_value > slp_value_2)) or ((current_slp_value > slp_value_3) and (current_slp_value > slp_value_4)):
                            ridges_map[current_lat, current_lon] = 1

        return troughs_map, ridges_map

    def _calcualte_vorticity_maps(self, uwind_data, vwind_data, resolution, lats, total_lat, total_lon):
        vorticity_map = np.zeros((total_lat, total_lon))
        for current_lat in range(1, uwind_data.shape[0] - 1):
            for current_lon in range(1, uwind_data.shape[1] - 1):
                duwind = uwind_data[current_lat + 1, current_lon] - uwind_data[current_lat - 1, current_lon]
                dvwind = vwind_data[current_lat, current_lon + 1] - vwind_data[current_lat, current_lon - 1]
                dy = 2 * resolution * 111000  # 111 Km. is the distance of 1 degree latitude. We look for the distance between 2 points.
                dx = dy * math.cos(math.radians(lats[current_lat]))
                vorticity_map[current_lat, current_lon] = (dvwind / dx) - (duwind / dy)

        if self.is_interpolated:
            vorticity_map = my_interp(vorticity_map,
                                      self.orig_data_lats,
                                      self.orig_data_lons,
                                      consts.interp_resolution,
                                      consts.interpolation_method)[0]

        return vorticity_map

    # Calculate Geostrophic vorticity
    def _calcualte_geostrophic_vorticity_maps(self, slp_data, resolution, lats, total_lat, total_lon):
        ugwind_map = np.zeros((total_lat, total_lon))
        vgwind_map = np.zeros((total_lat, total_lon))
        geostrophic_vorticity_map = np.zeros((total_lat, total_lon))
        rho = 1.2754
        omega = 7.27e-5
        dy = 2 * resolution * 111000  # 111 Km. is the distance of 1 degree latitude. We look for the distance between 2 points.
        for current_lat in range(1, total_lat - 1):
            for current_lon in range(1, total_lon - 1):
                dpx = slp_data[current_lat, current_lon + 1] - slp_data[current_lat, current_lon - 1]
                dpy = slp_data[current_lat + 1, current_lon] - slp_data[current_lat - 1, current_lon]
                dx = dy * math.cos(math.radians(lats[current_lat]))
                ugwind_map[current_lat, current_lon] = (((-1) / rho) * (dpy / dy)) / (2 * omega * math.sin(math.radians(current_lat)))
                vgwind_map[current_lat, current_lon] = (((1) / rho) * (dpx / dx)) / (2 * omega * math.sin(math.radians(current_lat)))

        for current_lat in range(2, total_lat - 1):
            for current_lon in range(2, total_lon - 1):
                duwind = ugwind_map[current_lat + 1, current_lon] - ugwind_map[current_lat - 1, current_lon]
                dvwind = vgwind_map[current_lat, current_lon + 1] - vgwind_map[current_lat, current_lon - 1]
                geostrophic_vorticity_map[current_lat, current_lon] = (dvwind / dx) - (duwind / dy)

        if self.is_interpolated:
            geostrophic_vorticity_map = my_interp(geostrophic_vorticity_map,
                                                  self.orig_data_lats,
                                                  self.orig_data_lons,
                                                  consts.interp_resolution,
                                                  consts.interpolation_method)[0]

        return geostrophic_vorticity_map

    # Calculate the mean SLP in the RST squares
    def _calculate_rst_conditions_in_boxes(self, slp_data, geostrophic_vorticity_map, lats, lons, resolution,
                                           show_geostrophic_vorticity, trough_coordinates):
        lowest_lat = lats[0]
        lowest_lon = lons[0]
        multiplier = 1 / resolution

        indexed_rst_square1_lat1 = math.ceil((consts.rst_square1_lat1 - lowest_lat) * multiplier)
        indexed_rst_square1_lat2 = math.floor((consts.rst_square1_lat2 - lowest_lat) * multiplier)
        indexed_rst_square1_lon1 = math.ceil((consts.rst_square1_lon1 - lowest_lon) * multiplier)
        indexed_rst_square1_lon2 = math.floor((consts.rst_square1_lon2 - lowest_lon) * multiplier)
        self.mean_slp_square1 = np.mean(np.mean(slp_data[indexed_rst_square1_lat1:indexed_rst_square1_lat2+1,
                                           indexed_rst_square1_lon1:indexed_rst_square1_lon2+1])) / 100
        print("mean SLP at square 1: %f", self.mean_slp_square1)

        indexed_rst_square2_lat1 = math.ceil((consts.rst_square2_lat1 - lowest_lat) * multiplier)
        indexed_rst_square2_lat2 = math.floor((consts.rst_square2_lat2 - lowest_lat) * multiplier)
        indexed_rst_square2_lon1 = math.ceil((consts.rst_square2_lon1 - lowest_lon) * multiplier)
        indexed_rst_square2_lon2 = math.floor((consts.rst_square2_lon2 - lowest_lon) * multiplier)
        self.mean_slp_square2 = np.mean(np.mean(slp_data[indexed_rst_square2_lat1:indexed_rst_square2_lat2+1,
                                           indexed_rst_square2_lon1:indexed_rst_square2_lon2+1])) / 100
        print("mean SLP at square 2: %f", self.mean_slp_square2)

        # Calculate the mean Geostrophic Vorticity in the 3rd RST square
        if show_geostrophic_vorticity:
            indexed_rst_square3_lat1 = math.ceil((consts.rst_square3_lat1 - lowest_lat) * multiplier)
            indexed_rst_square3_lat2 = math.floor((consts.rst_square3_lat2 - lowest_lat) * multiplier)
            indexed_rst_square3_lon1 = math.ceil((consts.rst_square3_lon1 - lowest_lon) * multiplier)
            indexed_rst_square3_lon2 = math.floor((consts.rst_square3_lon2 - lowest_lon) * multiplier)
            self.mean_geos_vort_square3 = np.mean(np.mean(geostrophic_vorticity_map[indexed_rst_square3_lat1:indexed_rst_square3_lat2+1, indexed_rst_square3_lon1:indexed_rst_square3_lon2+1])) / 100
            print("mean Geostrophic Vorticity at square 3: %f", self.mean_geos_vort_square3)

        # Check for the RST square condition
        if show_geostrophic_vorticity:
            if (self.mean_slp_square1 < self.mean_slp_square2) and (self.mean_geos_vort_square3 > 0):
                print('RST square conditions met')
            else:
                print('RST square conditions are not met')
            print('=====================================')

            if (self.mean_slp_square1 < self.mean_slp_square2) and (self.mean_geos_vort_square3 > 0) and (self.trough_coordinates_matrix.any()):
                is_rst_condition_met = True
            else:
                is_rst_condition_met = False
        else:
            is_rst_condition_met = None

        return is_rst_condition_met

    # This function will create the map according to the flags sent in the previous calculate_maps_data method call
    def create_map(self, map_axis, show_rst_info, req_colormap, polyfit_rst):
        if self.is_interpolated is None:
            print("Use the calculate_maps_data method before calling create_map")
            return

        # Prepare the right data depending on interpolation
        if self.is_interpolated:
            slp_data = self.interp_slp_data[self.current_day, :, :].squeeze()
            total_lat = self.interp_data_lats.shape[0]
            total_lon = self.interp_data_lons.shape[0]
            lats = self.interp_data_lats
            lons = self.interp_data_lons
        else:
            slp_data = self.orig_slp_data[self.current_day, :, :].squeeze()
            total_lat = self.orig_data_lats.shape[0]
            total_lon = self.orig_data_lons.shape[0]
            lats = self.orig_data_lats
            lons = self.orig_data_lons

        # Create the map object
        rst_map = Basemap(llcrnrlon=consts.map_lon1,
                          llcrnrlat=consts.map_lat1,
                          urcrnrlon=consts.map_lon2,
                          urcrnrlat=consts.map_lat2,
                          projection='merc',
                          resolution='i',
                          ax=map_axis)
        rst_map.drawcoastlines()
        rst_map.drawparallels(np.arange(consts.map_lat1, consts.map_lat2, 2.5), labels=[1, 0, 0, 0], fontsize=8)
        rst_map.drawmeridians(np.arange(consts.map_lon1, consts.map_lon2, 2.5), labels=[0, 0, 0, 1], fontsize=8)
        #map_axis.set(cmap = plt.cm.get_cmap('Blues_r')) #colormap = 'coolwarm',

        # Build map title
        resolution_str = str(self.orig_data_lats[1] - self.orig_data_lats[0])
        if self.is_interpolated:
            is_interpolated_str = 'Interpolated'
        else:
            is_interpolated_str = 'Not Interpolated'
        plot_title = self.model_data + ', Resolution ' + resolution_str + ', ' + is_interpolated_str
        plt.title(plot_title)

        # Calculate the meshes for the maps and plot SLP contours (always)
        lon1_index = int(np.where(lons <= consts.map_lon1)[0][-1])
        lon2_index = int(np.where(lons >= consts.map_lon2)[0][-1])
        lat1_index = int(np.where(lats <= consts.map_lat1)[0][-1])
        lat2_index = int(np.where(lats >= consts.map_lat2)[0][-1])
        mesh_lons, mesh_lats = np.meshgrid(lons[lon1_index:lon2_index + 1], lats[lat1_index:lat2_index + 1])

        x, y = rst_map(mesh_lons, mesh_lats)
        min_slp = int(np.floor(slp_data.min()))
        max_slp = int(np.ceil(slp_data.max()))
        rst_map.contour(x, y, slp_data[lat1_index:lat2_index + 1, lon1_index:lon2_index + 1], range(min_slp, max_slp, 200), linewidths=1.5, colors='k')

        # Prepare the selected subsetmap
        subset_map = None
        if self.vorticity_map is not None:
            subset_map = self.vorticity_map[lat1_index:lat2_index + 1, lon1_index:lon2_index + 1]

        # Display the geostrophic vorticity map if needed
        if self.geostrophic_vorticity_map is not None:
            subset_map = self.geostrophic_vorticity_map[lat1_index:lat2_index+1, lon1_index:lon2_index+1]

        # Display the selected map
        if subset_map is not None:
            rst_map.contour(x, y, subset_map, 10, linewidths=0.5, colors='k')
            max_value = subset_map.max()
            min_value = subset_map.min()
            if min_value < 0 and max_value > 0:
                if max_value > abs(min_value):
                    min_value = -max_value
                else:
                    max_value = abs(min_value)
            cs = rst_map.contourf(x, y, subset_map, 10, cmap=plt.cm.get_cmap(req_colormap), vmin=min_value, vmax=max_value)

            # Add Colorbar
            plt.colorbar(cs)

        # Draw the RSTs, if any
        for current_RST in range(0, int(np.size(self.trough_coordinates_matrix, 1)/2)):
            # Get the current trough columns from the trough matrix
            trough_coords = self.trough_coordinates_matrix[:, 2*current_RST:2*current_RST+2]
            # remove all zeros from current RST
            trough_coords = trough_coords[~(trough_coords == 0).all(1)]
            x_trough, y_trough = rst_map(trough_coords[:, 1], trough_coords[:, 0])

            if polyfit_rst:
                z = np.polyfit(y_trough, x_trough, 3) # I invert trhe x and y because of the trough shape from south to north
                p = np.poly1d(z)
                latp = np.linspace(y_trough[0], y_trough[-1], 100)
                rst_map.plot(p(latp), latp, marker=None, linewidth = 6, color='black')
                rst_map.plot(p(latp), latp, marker=None, linewidth=4, color='yellow')
            else:
                rst_map.plot(x_trough, y_trough, marker=None, linewidth = 6, color='black')
                rst_map.plot(x_trough, y_trough, marker=None, linewidth=4, color='yellow')

        # Draw the troughs and ridges dots
        if self.troughs_map is not None:
            for current_lat in range(lat1_index, lat2_index):
                for current_lon in range(lon1_index, lon2_index):
                    x_dot, y_dot = rst_map(lons[current_lon],  lats[current_lat])
                    if self.troughs_map[current_lat, current_lon] == 1:
                        rst_map.plot(x_dot,
                                     y_dot,
                                     marker='o',
                                     fillstyle='full',
                                     color='blue',
                                     markeredgecolor='black',
                                     markersize=5)
                    if self.ridges_map[current_lat, current_lon] == 1:
                        rst_map.plot(x_dot,
                                     y_dot,
                                     marker='o',
                                     fillstyle='full',
                                     color='red',
                                     markeredgecolor='black',
                                     markersize=5)

        if show_rst_info: # Draw box3 and the 2 points
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
            rst_map.plot(x_region, y_region, marker=None, linewidth = 3, color='black')
            if self.is_interpolated:
                x_mark, y_mark = rst_map(35,30)
                rst_map.plot(x_mark,
                             y_mark,
                             marker='o',
                             fillstyle = 'full',
                             color='white',
                             markeredgecolor='black',
                             markersize=10)

                x_mark, y_mark = rst_map(35,32.5)
                rst_map.plot(x_mark,
                             y_mark,
                             marker='o',
                             fillstyle = 'full',
                             color='white',
                             markeredgecolor='black',
                             markersize=10)

            # Add the points value
            if (self.geostrophic_vorticity_map is not None) and (self.is_interpolated):
                # data_string = "1st point: " + str(('%.2E' % self.geostrophic_vorticity_map[4, 6]))\
                #               +"  2nd point: " + str(('%.2E' % self.geostrophic_vorticity_map[3, 6]))
                # x_dot, y_dot = rst_map(consts.map_lon1 + 1, consts.map_lat2 - 2)
                # plt.text(x_dot, y_dot, data_string, fontsize=consts.map_text_fontsize, bbox=dict(facecolor="white", alpha=0.5))

                # Add a note for met rst conditions
                x_dot, y_dot = rst_map(consts.map_lon1 + 1, consts.map_lat2 - 2)
                if (self.mean_slp_square1 < self.mean_slp_square2) and (self.mean_geos_vort_square3 > 0):
                    # plt.text(x_dot, y_dot, 'RST square conditions met', fontsize=consts.map_text_fontsize, bbox=dict(facecolor="white", alpha=0.5))
                    plt.text(x_dot, y_dot, 'Conditions met', fontsize=consts.map_text_fontsize, color = 'green', weight = 'bold',
                             bbox=dict(facecolor="white", alpha=0.8))
                else:
                    # plt.text(x_dot, y_dot, 'RST square conditions not met', fontsize=consts.map_text_fontsize, bbox=dict(facecolor="white", alpha=0.5))
                    plt.text(x_dot, y_dot, 'Conditions not met', fontsize=consts.map_text_fontsize, color = 'red', weight = 'bold',
                             bbox=dict(facecolor="white", alpha=0.8))

        # Add the date
        x_dot, y_dot = rst_map(consts.map_lon1+1, consts.map_lat2-1)
        current_date = self.data_string_time[self.current_day]
        plt.text(x_dot, y_dot, current_date, fontsize=consts.map_text_fontsize, weight = 'bold', bbox=dict(facecolor="white", alpha=0.8))



        return rst_map

    # return the prev day string date and next day string date for the Next/Prev days buttons in the GUI
    def get_next_and_prev_days(self, current_date):
        this_day = 0
        for loop_day in range(self.data_string_time.shape[0]):
            if str(self.data_string_time[loop_day]) == current_date:
                this_day = loop_day
                break

        if this_day == 0:
            return [], self.data_string_time[this_day + 1]
        elif this_day == self.data_time.shape[0]-1:
            return self.data_string_time[this_day - 1], []
        else:
            return self.data_string_time[this_day - 1], self.data_string_time[this_day + 1]
def main():
    save_maps = False

    plotRSTs_instance = PlotRSTs()

    #for current_day in range(30):
    current_day = "1985-01-01 12:00:00"
    is_rst_condition_met = plotRSTs_instance.calculate_maps_data(current_day,
                                                                                   use_interpolation=True,
                                                                                   data_to_map='NCEP',
                                                                                   show_dots=True)
    map_figure, map_axis = plt.subplots()
    map_figure.set_figheight(8)
    map_figure.set_figwidth(7)
    rst_map = plotRSTs_instance.create_map(map_axis, show_rst_info=True, req_colormap='coolwarm')

    #rst_fig = large_fig(4, 3)
    #rst_map = plotRSTs_instance.create_map(show_rst_info=True)
    plt.show()

    if save_maps:
        directory = ("C:/Users/hatzv/Documents/Geography/Research_help/Pinhas synoptic classification/New_classification_algorithm/output/")
        map_name = "Change me"  # TODO make this name an appropriate one
        filename = directory + map_name + ".png"
        plt.savefig(filename)


if __name__ == "__main__":
    main()
