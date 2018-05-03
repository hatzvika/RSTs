import matplotlib.pyplot as plt
from python.Plot_RSTs.Plot_RSTs import PlotRSTs
import python.Plot_RSTs.plot_RST_constants as consts


show_info = False
save_maps = True

# Parameters for the calculations that can change
use_interpolation = True
only_longest_separate = True
polyfit_rst = True

# Parameters for the calculations that can't change
data_to_map_var = 'Geostrophic Vorticity'
show_dots = False

# start_year = 1998
# end_year = 2000
start_year = 2006
end_year = 2006

year_list = [str(x) for x in range(start_year, end_year+1)]

for current_year in year_list:
    print(current_year)
    plotRSTs_instance = PlotRSTs('NCEP', current_year)
    data_string_time = plotRSTs_instance.data_string_time
    previous_month_day = ""
    leap_year_offset = 0
    rows_counter = 2
    for current_day in data_string_time:
        current_day_str = str(current_day)
        print(current_day_str)

        daily_rst_classification, slp_data, geostrophic_vorticity_map, is_rst_condition_met = plotRSTs_instance.calculate_maps_data(
            current_day_str,
            use_interpolation=use_interpolation,
            data_to_map=data_to_map_var,
            show_dots=show_dots,
            only_longest_separate=only_longest_separate,
            polyfit_rst=polyfit_rst)

        map_figure, map_axis = plt.subplots(figsize=(10, 10))
        rst_map = plotRSTs_instance.create_map(map_axis, show_rst_info=True, req_colormap='coolwarm', show_info=show_info)

        if save_maps:
            # directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Results/Test_success_rates/All_RSTs_1998-2000/'
            directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Results/Test_success_rates/Oct-May_2004_2006/'
            map_name = current_day_str[0:10]
            filename = directory + map_name + ".png"
            plt.savefig(filename)
        else:
            plt.show()


        # if daily_rst_classification != consts.rst_orientation_no_rst:
        #     map_figure, map_axis = plt.subplots(figsize=(10, 10))
        #     rst_map = plotRSTs_instance.create_map(map_axis, show_rst_info=True, req_colormap='coolwarm')
        #
        #     if save_maps:
        #         directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Results/Test_success_rates/All_RSTs_1998-2000/'
        #         map_name = current_day_str[0:10]
        #         filename = directory + map_name + ".png"
        #         plt.savefig(filename)
        #     else:
        #         plt.show()


