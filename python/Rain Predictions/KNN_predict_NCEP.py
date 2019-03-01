# Predict the rain in each station for each year between 1991-2008, according to the rest of the years in the range.
# That means that for each year, there are other 17 years as a training set.

import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsRegressor
import pickle


start_year = 1991
end_year = 2008

pkls_directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Data/Rain Data/pkls/'

with open(pkls_directory + 'ncep_zscore_vals_df_1991-2008.pkl', 'rb') as ncep_zscore_input_data_file:
    ncep_zscore_data = pickle.load(ncep_zscore_input_data_file)
with open(pkls_directory + 'rain_data_df_1991-2008.pkl', 'rb') as rain_data_file:
    rain_data = pickle.load(rain_data_file)

rain_data.index = rain_data.index.map(str)
#ncep_zscore_data.drop(ncep_zscore_data.columns[list(range(25, 100))], axis=1, inplace=True)
ncep_zscore_data.index = rain_data.index


for current_year in range(start_year, end_year + 1):
    for current_month in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
        for station in rain_data.columns:
            for num_of_neighbours in range(1,30):
                # Remove missing rain data
                station_data = rain_data[station]
                missing_data_indices = station_data[station_data == -999].index.values
                clean_station_data = station_data.drop(missing_data_indices)
                clean_ncep_zscore_data = ncep_zscore_data.drop(missing_data_indices) #.round(3) ##### REMOVE round!!!

                # Create x_train, y_train and x_test, y_test
                y_test = clean_station_data[clean_station_data.index.str.startswith(str(current_year)+current_month)]
                x_test = clean_ncep_zscore_data[clean_ncep_zscore_data.index.str.startswith(str(current_year)+current_month)]
                y_train = clean_station_data.drop(y_test.index)
                x_train = clean_ncep_zscore_data.drop(x_test.index)

                knn = KNeighborsRegressor(n_neighbors=num_of_neighbours, weights='distance')
                knn.fit(x_train, y_train)
                pred = knn.predict(x_test)

                # # Try to figure out what's wrong
                # for index1, vector in x_test.iterrows():
                #     counter = 0
                #     min_distance1 = 1000
                #     min_distance2 = 1000
                #     min_distance3 = 1000
                #     min_index1 = 0
                #     min_index2 = 0
                #     min_index3 = 0
                #     for index2, comp_vect in x_train.iterrows():
                #         distance = np.sqrt(np.sum((vector-comp_vect)**2))
                #         if distance < min_distance1:
                #             min_distance3 = min_distance2
                #             min_distance2 = min_distance1
                #             min_distance1 = distance
                #             min_index3 = min_index2
                #             min_index2 = min_index1
                #             min_index1 = counter
                #         elif distance < min_distance2:
                #             min_distance3 = min_distance2
                #             min_distance2 = distance
                #             min_index3 = min_index2
                #             min_index2 = counter
                #         elif distance < min_distance3:
                #             min_distance3 = distance
                #             min_index3 = counter
                #
                #         counter += 1
                #     print(knn.kneighbors(np.array(vector).reshape(1, -1), 3))
                #     value1 = y_train.iloc[min_index1]
                #     value2 = y_train.iloc[min_index2]
                #     value3 = y_train.iloc[min_index3]
                #     print(((value1/min_distance1) + (value2/min_distance2) + (value3/min_distance3)) / ((1/min_distance1) + (1/min_distance2) + (1/min_distance3)))
                # # print(pred, y_test)
                print(knn.score(x_test, y_test), station)
        print()
