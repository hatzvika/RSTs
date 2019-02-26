from python.Tracks.TracksDB import TracksDB
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np

# Testing lows
a = TracksDB(1979)

req_low = 56
time = a.get_low_time(req_low, return_format='string')
lat = a.get_low_lat_degrees(req_low)
lon = a.get_low_lon_degrees(req_low)
slp = a.get_low_lon_slp_value(req_low)
gradient = a.get_low_gradient(req_low)
radius = a.get_low_radius(req_low)
length = a.get_total_lows()

print(time, '\n', lat, '\n', lon, '\n', slp, '\n', gradient, '\n', radius, '\n', length)

# Testing tracks
req_track = 2
track = a.get_track(req_track)
total_tracks = a.get_total_tracks()
print(track, total_tracks)

# Testing parenthood
req_low_for_parent = 50948
parent = a.get_parent_low(req_low_for_parent)
print(parent)

# Testing over the map
tracks_map = Basemap(llcrnrlon=0,
                     llcrnrlat=0,
                     urcrnrlon=70,
                     urcrnrlat=70,
                     projection='merc',
                     resolution='i')
tracks_map.drawcoastlines()
tracks_map.drawparallels(np.arange(0, 70, 10), labels=[1, 0, 0, 0], fontsize=8)
tracks_map.drawmeridians(np.arange(0, 70, 10), labels=[0, 0, 0, 1], fontsize=8)

for track in a.tracks_list[1:2]:
    lons=[]
    lats=[]
    for low_id in track:
        if low_id != -1000:
            lons.append(a.get_low_lon_degrees(low_id))
            lats.append(a.get_low_lat_degrees(low_id))

    y,x = tracks_map(lons, lats)
    tracks_map.plot(y, x, marker=None, linewidth=1, color='red')
plt.show()
#print(np.transpose(np.array(lats)), np.transpose(np.array(lons)))
