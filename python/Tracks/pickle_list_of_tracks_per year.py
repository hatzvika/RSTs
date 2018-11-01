import pandas as pd
import numpy as np
import pickle


for year in range(1979, 2016):
    input_directory = 'C:/Users/hatzv/Documents/Geography/Post-doc/Results/DB for the knowledge center/Tracks DB/'
    input_filename = 'tracks_DB_09_' + str(year) + '-05_' + str(year + 1) + '.xlsx'
    track_df = pd.read_excel(input_directory + input_filename)

    tracks_list=[]
    for index, track_array in track_df.iterrows():
        track_array = np.array(track_array)
        track_length = track_array[1]
        track_array = track_array[2:2 + track_length]
        tracks_list.append(track_array)

    output_directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Data/Tracks DB/Tracks pkl/'
    output_filename = 'tracks_list_09_' + str(year) + '-05_' + str(year + 1) + '.pkl'
    with open(output_directory + output_filename, 'wb') as output:
        pickle.dump(tracks_list, output, pickle.HIGHEST_PROTOCOL)