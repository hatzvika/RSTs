import pandas as pd
import numpy as np
import pickle


for year in range(1979, 2018):
    input_directory = 'C:/Users/hatzv/Documents/Geography/Post-doc/Results/DB for the knowledge center/Parenthood DB/'
    input_filename = 'detailed_parenthood_DB_01_Sep_' + str(year) + '-31_Aug_' + str(year + 1) + '.xlsx'
    parenthood_df = pd.read_excel(input_directory + input_filename)

    parenthood_list = np.array(parenthood_df.iloc[:, 0:10])

    output_directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Data/Tracks DB/Parenthood pkl/'
    output_filename = 'detailed_parenthood_01_Sep_' + str(year) + '-31_Aug_' + str(year + 1) + '.pkl'
    with open(output_directory + output_filename, 'wb') as output:
        pickle.dump(parenthood_list, output, pickle.HIGHEST_PROTOCOL)