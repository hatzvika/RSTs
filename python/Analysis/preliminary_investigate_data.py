import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


predictors = pd.read_excel('C:/Users/hatzv/Documents/Geography/RSTs/python/Analysis/Results/Indices_for_RST_evaluation.xlsx')
# g = sns.PairGrid(predictors)
# g.map_diag(sns.distplot)
# g.map_upper(plt.scatter)
# g.map_lower(sns.kdeplot)
#
# plt.show()

# Compute the correlation matrix
corr = predictors.corr()

# Generate a mask for the upper triangle
mask = np.zeros_like(corr, dtype=np.bool)
mask[np.triu_indices_from(mask)] = True

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(11, 9))

# Generate a custom diverging colormap
cmap = sns.diverging_palette(220, 10, as_cmap=True)

# Draw the heatmap with the mask and correct aspect ratio
sns.heatmap(corr, mask=mask, cmap=cmap, center=0,
            square=True, linewidths=.5)

plt.show()