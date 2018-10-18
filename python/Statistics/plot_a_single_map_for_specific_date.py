import matplotlib.pyplot as plt
from python.Plot_RSTs.Plot_RSTs import PlotRSTs
import python.Plot_RSTs.plot_RST_constants as consts


show_info = False
# save_map = True

# Parameters for the calculations that can change
use_interpolation = True
only_longest_separate = True
polyfit_rst = True

# Parameters for the calculations that can't change
data_to_map_var = 'Geostrophic Vorticity'
show_dots = False

year = '2010'  # YYYY
month = '11'  # MM
day = '16'  # DD
hour = '12'

plotRSTs_instance = PlotRSTs('NCEP', int(year), int(hour))
current_day_str = year + '-' + month + '-' + day + ' ' + hour + ':00:00'
print(current_day_str)

daily_rst_classification, slp_data, geostrophic_vorticity_map, is_rst_condition_met = plotRSTs_instance.calculate_maps_data(
    current_day_str,
    use_interpolation=use_interpolation,
    data_to_map=data_to_map_var,
    show_dots=show_dots,
    only_longest_separate=only_longest_separate,
    polyfit_rst=polyfit_rst)

map_figure, map_axis = plt.subplots(figsize=(10, 10))
rst_map = plotRSTs_instance.create_map(map_axis, show_rst_info=False, req_colormap='coolwarm', show_info=show_info)

# if save_map:
#     # directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Results/Test_success_rates/All_RSTs_1998-2000/'
#     directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Results/Test_success_rates/Oct-May_2004_2006/'
#     map_name = current_day_str[0:10]
#     filename = directory + map_name + ".png"
#     plt.savefig(filename)
# else:
#     plt.show
plt.show()


