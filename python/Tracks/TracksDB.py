# This class holds all the cyclone tracks and low centers created for the Mediterranean in Matlab.
import pickle

# These imports are for making the parent search faster (log(n) instead of n)
import numpy as np
from python.utils.binary_search import binary_search

class TracksDB:
    def __init__(self, year):

        # First read the pickled tracks and low centers, which are stored as numpy arrays
        directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Data/Tracks DB/'
        tracks_filename = 'Tracks pkl/tracks_list_09_' + str(year) + '-05_' + str(year+1) + '.pkl'
        lows_filename = 'Lows pkl/lows_list_01_Sep_' + str(year) + '-31_Aug_' + str(year+1) + '.pkl'
        parenthood_filename = 'Parenthood pkl/detailed_parenthood_01_Sep_' + str(year) + '-31_Aug_' + str(year+1) + '.pkl'

        with open(directory + lows_filename, 'rb') as lows_input_data:
            self.lows_list = pickle.load(lows_input_data)

        with open(directory + tracks_filename, 'rb') as tracks_input_data:
            self.tracks_list = pickle.load(tracks_input_data)

        with open(directory + parenthood_filename, 'rb') as parenthood_input_data:
            self.parenthood_list = np.array(pickle.load(parenthood_input_data))

    def get_low_time(self, low_id, return_format='string'):
        low_id -= 1  # Because Python starts counting from 0

        year = int(self.lows_list[low_id, 1])
        month = int(self.lows_list[low_id, 2])
        day = int(self.lows_list[low_id, 3])
        hour = int(self.lows_list[low_id, 4])

        if return_format == 'string':
            time_string = f'{year}-{month:02}-{day:02}-{hour:02}'
            return time_string
        else:
            return [year, month, day, hour]

    def get_low_lat_degrees(self, low_id):
        return self.lows_list[low_id-1, 5]

    def get_low_lon_degrees(self, low_id):
        return self.lows_list[low_id-1, 6]

    def get_low_lon_slp_value(self, low_id):
        return int(self.lows_list[low_id-1, 7])

    def get_low_lon_gradient(self, low_id):
        return int(self.lows_list[low_id-1, 8])

    def get_low_radius(self, low_id):
        return int(self.lows_list[low_id-1, 9])

    def get_total_lows(self):
        return self.lows_list.shape[0]

    def get_track(self, track_id):
        # The track id doesn't really matter, so we don't use track_id-1 like in lows.
        # This is because the low ids are inside each track and needs to be correctly looked up for.
        # However, tracks are not being called by their id anywhere in the code
        return self.tracks_list[track_id]

    def get_total_tracks(self):
        return len(self.tracks_list)

    def get_parent_low(self, low_id):
        # The daughter low is on the first column and the parent is on the second.
        parent_index = binary_search(self.parenthood_list[:, 0], low_id)
        if parent_index is not None:
            return self.parenthood_list[parent_index, 1]
        else:
            return None

    def get_total_parents(self):
        return len(self.parenthood_list)
