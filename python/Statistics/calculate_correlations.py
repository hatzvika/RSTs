import pandas as pd
import numpy as np
from scipy.stats.stats import pearsonr

# Read the excel files and put into Pandas data frames
df_NCEP = pd.read_excel('C:/Users/hatzv/Documents/Geography/RSTs/python/Statistics/Results/Monthly_trends_RSTs_NCEP_1979-2016.xlsx', 'All RSTs')
df_ERA = pd.read_excel('C:/Users/hatzv/Documents/Geography/RSTs/python/Statistics/Results/Monthly_trends_RSTs_ERA_1979-2016.xlsx', 'All RSTs')
df_ERA_2_5 = pd.read_excel('C:/Users/hatzv/Documents/Geography/RSTs/python/Statistics/Results/Monthly_trends_RSTs_ERA_2_5_1979-2016.xlsx', 'All RSTs')

# Get only the data we look for - the result for each month of each year (12*38 results)
subdf_NCEP = df_NCEP.iloc[0:12, 0:38].fillna(0)
subdf_ERA = df_ERA.iloc[0:12, 0:38].fillna(0)
subdf_ERA_2_5 = df_ERA_2_5.iloc[0:12, 0:38].fillna(0)

# Transform into a 1-D array for the correlation function
arr_NCEP = np.array(subdf_NCEP)
arr_NCEP = np.reshape(arr_NCEP, 12*38)
arr_ERA = np.array(subdf_ERA)
arr_ERA = np.reshape(arr_ERA, 12*38)
arr_ERA_2_5 = np.array(subdf_ERA_2_5)
arr_ERA_2_5 = np.reshape(arr_ERA_2_5, 12*38)

# Correlate
print("")
print("-----------------------------------------------------------")
print("Correlations for each month in each year (12*38 points)")
print("-----------------------------------------------------------")
print("NCEP vs. ERA 2.5    : " + str(pearsonr(arr_NCEP, arr_ERA_2_5)))  # Returns (Pearson's correlation coefficient, 2-tailed p-value)
print("NCEP vs. ERA 0.75   : " + str(pearsonr(arr_NCEP, arr_ERA)))
print("ERA 2.5 vs. ERA 0.75: " + str(pearsonr(arr_ERA_2_5, arr_ERA)))

# Get only the data we look for - the result for yearly sums (12 results)
subdf_NCEP = df_NCEP.iloc[12, 0:38].fillna(0)
subdf_ERA = df_ERA.iloc[12, 0:38].fillna(0)
subdf_ERA_2_5 = df_ERA_2_5.iloc[12, 0:38].fillna(0)

# Correlate
print("")
print("-----------------------------------------------------------")
print("Correlations for yearly totals (38 points)")
print("-----------------------------------------------------------")
print("NCEP vs. ERA 2.5    : " + str(pearsonr(subdf_NCEP, subdf_ERA_2_5)))  # Returns (Pearson's correlation coefficient, 2-tailed p-value)
print("NCEP vs. ERA 0.75   : " + str(pearsonr(subdf_NCEP, subdf_ERA)))
print("ERA 2.5 vs. ERA 0.75: " + str(pearsonr(subdf_ERA_2_5, subdf_ERA)))

# Get only the data we look for - the result for Oct-Dec sums (12 results)
subdf_NCEP = df_NCEP.iloc[13, 0:38].fillna(0)
subdf_ERA = df_ERA.iloc[13, 0:38].fillna(0)
subdf_ERA_2_5 = df_ERA_2_5.iloc[13, 0:38].fillna(0)

# Correlate
print("")
print("-----------------------------------------------------------")
print("Correlations for total Oct-Dec of every year (38 points)")
print("-----------------------------------------------------------")
print("NCEP vs. ERA 2.5    : " + str(pearsonr(subdf_NCEP, subdf_ERA_2_5)))  # Returns (Pearson's correlation coefficient, 2-tailed p-value)
print("NCEP vs. ERA 0.75   : " + str(pearsonr(subdf_NCEP, subdf_ERA)))
print("ERA 2.5 vs. ERA 0.75: " + str(pearsonr(subdf_ERA_2_5, subdf_ERA)))

# Get only the data we look for - the result for Oct-Apr sums (12 results)
subdf_NCEP = df_NCEP.iloc[14, 0:38].fillna(0)
subdf_ERA = df_ERA.iloc[14, 0:38].fillna(0)
subdf_ERA_2_5 = df_ERA_2_5.iloc[14, 0:38].fillna(0)

# Correlate
print("")
print("-----------------------------------------------------------")
print("Correlations for total Oct-Apr of every year (38 points)")
print("-----------------------------------------------------------")
print("NCEP vs. ERA 2.5    : " + str(pearsonr(subdf_NCEP, subdf_ERA_2_5)))  # Returns (Pearson's correlation coefficient, 2-tailed p-value)
print("NCEP vs. ERA 0.75   : " + str(pearsonr(subdf_NCEP, subdf_ERA)))
print("ERA 2.5 vs. ERA 0.75: " + str(pearsonr(subdf_ERA_2_5, subdf_ERA)))

# Create the change over time correlation for each month (12 results)
NCEP_vs_ERA_2_5_monthly = np.zeros(12)
NCEP_vs_ERA_monthly = np.zeros(12)
ERA_2_5_vs_ERA_monthly = np.zeros(12)

for month in range(12):
    subdf_NCEP = df_NCEP.iloc[month, 0:38].fillna(0)
    subdf_ERA = df_ERA.iloc[month, 0:38].fillna(0)
    subdf_ERA_2_5 = df_ERA_2_5.iloc[month, 0:38].fillna(0)

    NCEP_vs_ERA_2_5_monthly[month] = pearsonr(subdf_NCEP, subdf_ERA_2_5)[0]
    NCEP_vs_ERA_monthly[month] = pearsonr(subdf_NCEP, subdf_ERA)[0]
    ERA_2_5_vs_ERA_monthly[month] = pearsonr(subdf_ERA_2_5, subdf_ERA)[0]


# Correlate
print("")
print("-----------------------------------------------------------")
print("Correlations for each month over time (38 points per month)")
print("-----------------------------------------------------------")
print("Jan    Feb   Mar   Apr   May   Jun   Jul   Aug   Sep   Oct   Nov   Dec")
print("NCEP vs. ERA 2.5    : " + str(NCEP_vs_ERA_2_5_monthly))  # Returns (Pearson's correlation coefficient, 2-tailed p-value)
print("NCEP vs. ERA 0.75   : " + str(NCEP_vs_ERA_monthly))
print("ERA 2.5 vs. ERA 0.75: " + str(ERA_2_5_vs_ERA_monthly))




