from python.Plot_RSTs.Plot_RSTs import PlotRSTs
#import numpy as np
from openpyxl import Workbook

# Parameters for the calculations that can change
use_interpolation = True
only_longest_separate = True
polyfit_rst = True

# Parameters for the calculations that can't change
data_to_map_var = 'Geostrophic Vorticity'
show_dots = False

excel_filename_NCEP = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Statistics/Results/RST_classification_NCEP_1979-2016.xls'
excel_filename_ERA = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Statistics/Results/RST_classification_ERA_1979-2016.xls'
excel_filename_ERA_2_5 = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Statistics/Results/RST_classification__ERA_2.5_1979-2016.xls'
#table_xls_NCEP = np.zeros([366, 70])  # days in a leap year, years
#table_xls_ERA = np.zeros([366, 70])  # days in a leap year, years
#table_xls_ERA_2_5 = np.zeros([366, 70])  # days in a leap year, years
wb_NCEP = Workbook()
ws_NCEP = wb_NCEP.active
wb_ERA = Workbook()
ws_ERA = wb_ERA.active
wb_ERA_25 = Workbook()
ws_ERA_25 = wb_ERA_25.active

year_list = [str(x) for x in range(1979, 2017)]

cols_counter = 2
for current_year in year_list:
    print(current_year)
    plotRSTs_NCEP_instance = PlotRSTs('NCEP', current_year)
    plotRSTs_ERA_instance = PlotRSTs('ERA_Interim', current_year)
    plotRSTs_ERA_25_instance = PlotRSTs('ERA Int 2.5', current_year)
    data_string_time = plotRSTs_NCEP_instance.data_string_time
    previous_month_day = ""
    leap_year_offset = 0
    rows_counter = 2
    for current_day in data_string_time:
        current_day_str = str(current_day)
        print(current_day_str)
        NCEP_daily_rst_classification = plotRSTs_NCEP_instance.calculate_maps_data(current_day_str,
                                                                                   use_interpolation=use_interpolation,
                                                                                   data_to_map=data_to_map_var,
                                                                                   show_dots=show_dots,
                                                                                   only_longest_separate=only_longest_separate,
                                                                                   polyfit_rst=polyfit_rst)
        ERA_daily_rst_classification = plotRSTs_ERA_instance.calculate_maps_data(current_day_str,
                                                                                 use_interpolation=use_interpolation,
                                                                                 data_to_map=data_to_map_var,
                                                                                 show_dots=show_dots,
                                                                                 only_longest_separate=only_longest_separate,
                                                                                 polyfit_rst=polyfit_rst)
        ERA_25_daily_rst_classification = plotRSTs_ERA_25_instance.calculate_maps_data(current_day_str,
                                                                                       use_interpolation=use_interpolation,
                                                                                       data_to_map=data_to_map_var,
                                                                                       show_dots=show_dots,
                                                                                       only_longest_separate=only_longest_separate,
                                                                                       polyfit_rst=polyfit_rst)

        current_month_day = current_day_str[5:10]
        if (previous_month_day == "02-28") and (current_month_day != "02-29"):
            leap_year_offset = 1

        ws_NCEP.cell(column=cols_counter, row=rows_counter+leap_year_offset, value=NCEP_daily_rst_classification)
        ws_ERA.cell(column=cols_counter, row=rows_counter+leap_year_offset, value=NCEP_daily_rst_classification)
        ws_ERA_25.cell(column=cols_counter, row=rows_counter+leap_year_offset, value=NCEP_daily_rst_classification)
        #table_xls_NCEP[days_counter + leap_year_offset, years_counter] =  NCEP_daily_rst_classification
        #table_xls_ERA[days_counter + leap_year_offset, years_counter] =  ERA_daily_rst_classification
        #table_xls_ERA_2_5[days_counter + leap_year_offset, years_counter] =  ERA_25_daily_rst_classification

        previous_month_day = current_month_day
        rows_counter = rows_counter + 1

    cols_counter = cols_counter + 1

wb_NCEP.save(excel_filename_NCEP)
wb_ERA.save(excel_filename_ERA)
wb_ERA_25.save(excel_filename_ERA_2_5)
