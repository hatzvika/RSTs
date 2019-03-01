# This program creates a db with the rain data from all stations for each day.
# -999 is a missing value

import pandas as pd
import pickle


data_directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Data/Rain Data/rain_in_stations/'

# Read the data files for this year
filenames = ['Allone_Bashan', 'Bet_Dagan', 'Elkana', 'Elon', 'En_ha_horesh', 'Gevaram', 'Ginosar', 'Hafez_Hayyim', 'Haifa', 'Har_Kenaan',
             'Jerusalem', 'Kefar_Giladi', 'Meron', 'Mizpe_Harashim', 'Negba', 'Qiryat_Anavim', 'Rosh_Zurim', 'Yad_Hanna']

for_index_df = pd.read_csv(data_directory + filenames[0] + '_f', delimiter=r"\s+", lineterminator='\n', header=None)
rain_data_df = pd.DataFrame(index=for_index_df[1])
for filename in filenames:
    current_file_df = pd.read_csv(data_directory + filename + '_f', delimiter=r"\s+", lineterminator='\n', header=None)
    rain_data_df[filename] = current_file_df[2].values


output_directory = 'C:/Users/hatzv/Documents/Geography/RSTs/python/Data/Rain Data/pkls/'
output_filename = 'rain_data_df_1991-2008.pkl'
with open(output_directory + output_filename, 'wb') as output:
    pickle.dump(rain_data_df, output, pickle.HIGHEST_PROTOCOL)
