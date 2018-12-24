import pandas as pd
import numpy as np
from pandas import ExcelWriter
import win32clipboard as clipboard


df = pd.read_excel('C:/Users/hatzv/Documents/Geography/RSTs/python/Analysis/Results/RST_classification_NCEP_1948-2017.xlsx')
my_array = np.transpose(np.array(df))
my_array = my_array.reshape((366 * 70))

new_array=[]
for loop in range(366*2, my_array.shape[0]):
    if my_array[loop] == 'East':
        new_array.append(1)
    elif my_array[loop] == 'West':
        new_array.append(2)
    elif my_array[loop] == 'Central':
        new_array.append(3)
    elif my_array[loop] == 'No RST':
        new_array.append('')

print(new_array[420:430])
print(len(new_array))

"""
Copies an array into a string format acceptable by Excel.
Columns separated by \t, rows separated by \n
"""
# Create string from array
line_strings = []
for line in np.array(new_array):
    line_strings.append("\t".join(line.astype(str)).replace("\n", ""))
array_string = "\r\n".join(line_strings)

# Put string into clipboard (open, clear, set, close)
clipboard.OpenClipboard()
clipboard.EmptyClipboard()
clipboard.SetClipboardText(array_string)
clipboard.CloseClipboard()