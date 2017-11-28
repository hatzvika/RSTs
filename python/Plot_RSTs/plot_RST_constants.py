# This file holds some values used by the Plot_RSTs script and which are seldom changed.

# The location of the data files
raw_data_prefix = "Sample Data/"

# The interpolation resolution of the maps' data (not for the find_torugh method)
interp_resolution = 0.5  # This is the interpolated resolution(degrees) we aim for

# The interpolation resolution for finding the RST coordinates
rst_resolution = 0.5 # Look at slp_check_distance if changing this value!!

# using grid points. 3 * 0.5(rst_resolution) = 1.5 deg.
slp_check_distance = 3

# Interpolation_method: 0 = nearest-neighbor interpolation, 1 = bilinear interpolation, 3 = cublic spline
interpolation_method = 3

# Number of possible RSTs found in a single map
max_number_of_RST = 100

# Number of lat rows to check for the start of an RST
num_of_RST_start_lats = 5

# Get only the longest RST, or all of them
longest_only = True

# The coordiantes for the plotted area
map_lat1 = 20
map_lat2 = 45
map_lon1 = 25
map_lon2 = 45

# The coordiantes for the RST area, in which the trough is searched (by find_trough())
rst_lat1 = 27.5
rst_lat2 = 42.5
rst_lon1 = 30
rst_lon2 = 42.5

# The coordiantes for the box areas, in which the conditions for an RST existance are calculated
rst_square1_lat1 = 27
rst_square1_lat2 = 31
rst_square1_lon1 = 33
rst_square1_lon2 = 37

rst_square2_lat1 = 31
rst_square2_lat2 = 35
rst_square2_lon1 = 33
rst_square2_lon2 = 37

rst_square3_lat1 = 29
rst_square3_lat2 = 33
rst_square3_lon1 = 32.5
rst_square3_lon2 = 37.5

map_text_fontsize = 12


