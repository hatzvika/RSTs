from python.Tracks.TracksDB import TracksDB
import xlsxwriter

start_year = 1979
end_year = 2017  # 2011

spawn_lat1 = 30
spawn_lat2 = 37
spawn_lon1 = 30
spawn_lon2 = 38

parent_zone_lon1 = 25
parent_zone_lon2 = 45

excel_headlines = ['Date', 'Lat Daughter', 'Lon Daughter', 'Lat Parent', 'Lon Parent', 'Length', 'SLP Value', 'SLP Gradient', 'Radius', 'Lat Difference']

final_list = [excel_headlines]
for current_year in range(start_year, end_year+1):
    tr_db = TracksDB(current_year)
    total_tracks = tr_db.get_total_tracks()
    for current_track in range(total_tracks):
        track = tr_db.get_track(current_track)
        if len(track) >= 4:  # 24 hours or longer tracks
            first_low = track[0]
            lat_first = tr_db.get_low_lat_degrees(first_low)
            lon_first = tr_db.get_low_lon_degrees(first_low)
            if (lat_first > spawn_lat1) and (lat_first < spawn_lat2) and (lon_first > spawn_lon1) and (lon_first < spawn_lon2):
                parent_low = tr_db.get_parent_low(first_low)
                if (parent_low is not None) and (parent_low is not 0):
                    lat_parent = tr_db.get_low_lat_degrees(parent_low)
                    lon_parent = tr_db.get_low_lon_degrees(parent_low)
                    if (lat_parent < lat_first) and (lon_parent > parent_zone_lon1) and (lon_parent < parent_zone_lon2):
                        time = tr_db.get_low_time(first_low, return_format='string')
                        slp_first = tr_db.get_low_lon_slp_value(first_low)
                        gradient_first = tr_db.get_low_lon_gradient(first_low)
                        radius_first = tr_db.get_low_radius(first_low)
                        track_length = len(track)
                        final_list.append([time, lat_first, lon_first, lat_parent, lon_parent, track_length, slp_first, gradient_first, radius_first, lat_first-lat_parent])



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
worksheet.conditional_format('J1:J'+str(len(final_list)), {'type': 'cell',
                                                           'criteria': '>=',
                                                           'value': 5,
                                                           'format': format1})

workbook.close()