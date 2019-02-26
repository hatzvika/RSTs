from python.Tracks.TracksDB import TracksDB
import xlsxwriter
import pandas as pd

start_year = 1979
end_year = 2016  # 2011

spawn_lat1 = 30
spawn_lat2 = 36
spawn_lon1 = 30
spawn_lon2 = 38

parent_zone_lon1 = 25
parent_zone_lon2 = 45

minimum_radius_48 = 350

excel_headlines = ['Date', 'Lat Daughter', 'Lon Daughter', 'Lat Parent', 'Lon Parent',
                   'Length', 'SLP Value', 'SLP Gradient', 'Radius', 'Max Radius 48', 'RST -6','Lat Difference', 'Track Number']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

df = pd.read_excel('C:/Users/hatzv/Documents/Geography/RSTs/python/Analysis/Results/RST_classification_all_hours_ERA_1979-2016.xlsx', 'Sheet')

counter = 0
final_list = [excel_headlines]
for current_year in range(start_year, end_year+1):
    tr_db = TracksDB(current_year)
    total_tracks = tr_db.get_total_tracks()
    for current_track in range(total_tracks):
        track = tr_db.get_track(current_track)
        if len(track) >= 5:  # 24 hours or longer tracks
            first_low = track[0]
            lat_first = tr_db.get_low_lat_degrees(first_low)
            lon_first = tr_db.get_low_lon_degrees(first_low)
            if (lat_first > spawn_lat1) and (lat_first < spawn_lat2) and (lon_first > spawn_lon1) and (lon_first < spawn_lon2): # Inside spawn area
                parent_low = tr_db.get_parent_low(first_low)
                if (parent_low is not None) and (parent_low is not 0): # Has a parent
                    lat_parent = tr_db.get_low_lat_degrees(parent_low)
                    lon_parent = tr_db.get_low_lon_degrees(parent_low)
                    if (lat_parent < lat_first) and (lon_parent > parent_zone_lon1) and (lon_parent < parent_zone_lon2): # Parent is in right latitudes
                        # Check for radius is first 48 hours. Only those of which are larger han 350Km are used.
                        start_radius = tr_db.get_low_radius(track[0])
                        max_radius_48 = start_radius
                        for low in range(min(len(track), 7)):
                            low_num = track[low]
                            if low_num > 0:
                                radius = tr_db.get_low_radius(low_num)
                                if radius > max_radius_48:
                                    max_radius_48 = radius
                        if max_radius_48 >= minimum_radius_48: # Low gets deep enough
                            # Find the RST classification 6 hours prior to the low.
                            print(counter)
                            time_first_low = tr_db.get_low_time(first_low, return_format='string')
                            hour = int(time_first_low[11:])
                            day = int(time_first_low[8:10])
                            month_int = int(time_first_low[5:7])
                            month = months[month_int-1]
                            year = int(time_first_low[0:4])  # Not the current_year because each DB file starts in YEAR and ends with YEAR+1
                            if year < 2017:
                                if hour == 0:
                                    hour = 18
                                    day -= 1
                                    if day == 0:
                                        month_int -=1
                                        if month_int == 0:
                                            day = days_in_month[-1]
                                            month = months[-1]
                                            year -= 1
                                        else:
                                            day = days_in_month[month_int-1]
                                            month = months[month_int-1]
                                else:
                                    hour = hour - 6

                                rst_class_minus_6 = df[(df['Month'] == month) & (df['Day'] == day) & (df['Hour'] == hour)][year]
                                rst_class_minus_6 = rst_class_minus_6.get_values()[0]
                                if type(rst_class_minus_6) is not str: # In case the date is 1st of March, in which case we look for Feb 28
                                    rst_class_minus_6 = df[(df['Month'] == month) & (df['Day'] == day-1) & (df['Hour'] == hour)][year]
                                    rst_class_minus_6 = rst_class_minus_6.get_values()[0]

                                slp_first = tr_db.get_low_lon_slp_value(first_low)
                                gradient_first = tr_db.get_low_gradient(first_low)
                                radius_first = tr_db.get_low_radius(first_low)
                                track_length = len(track)
                                final_list.append([time_first_low, lat_first, lon_first, lat_parent, lon_parent, track_length,
                                                   slp_first, gradient_first, radius_first, max_radius_48, rst_class_minus_6, lat_first-lat_parent, current_track])

                                counter += 1

# Create an new Excel file and add a worksheet.
workbook = xlsxwriter.Workbook('RST_lows.xlsx')
worksheet = workbook.add_worksheet()

total_cols = len(final_list[1])
for row in range(len(final_list)):
    for col in range(total_cols):
        worksheet.write(row, col, final_list[row][col])

# Add a format. Light red fill with dark red text.
format1 = workbook.add_format({'bg_color': '#FFC7CE',
                               'font_color': '#9C0006'})

# # Add a format. Green fill with dark green text.
# format2 = workbook.add_format({'bg_color': '#C6EFCE',
#                                'font_color': '#006100'})

# Write a conditional format over a range.
worksheet.conditional_format('L1:L'+str(len(final_list)), {'type': 'cell',
                                                           'criteria': '>=',
                                                           'value': 10,
                                                           'format': format1})

workbook.close()
