import pandas as pd
import numpy as np
import pickle


for year in range(1979, 2016):
    input_directory = 'C:/Users/hatzv/Documents/Geography/Post-doc/Results/DB for the knowledge center/Low Centers DB/'
    input_filename = 'low_centers_DB_01_Sep_' + str(year) + '-31_Aug_' + str(year + 1) + '.xlsx'
    lows_df = pd.read_excel(input_directory + input_filename)

    lows_list = np.array(lows_df.iloc[:, 0:10])

    output_directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Data/Tracks DB/Lows pkl/'
    output_filename = 'lows_list_01_Sep_' + str(year) + '-31_Aug_' + str(year + 1) + '.pkl'
    with open(output_directory + output_filename, 'wb') as output:
        pickle.dump(lows_list, output, pickle.HIGHEST_PROTOCOL)