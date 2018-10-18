import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

use_percent = 1
df = pd.read_excel('C:/Users/hatzv/Documents/Geography/RSTs/python/Statistics/Results/Kuri_synoptic_classification_2000_2004.xlsx', 'Try')
# figure = sns.jointplot(x=df.columns[2], y=df.columns[3], data=df, kind='hex')
# figure = sns.violinplot(x=df.columns[1], y=df.columns[3], data=df, scale='count', cut=0, gridsize=19)
# figure = sns.catplot(x=df.columns[3], hue=df.columns[1], data=df, kind='count')
subdf = df.loc[df['RST NCEP number'].isin((1, 3))]

if use_percent:
    # For percentage
    percent_df = (subdf['Semi-subjective']
                  .groupby(df['RST NCEP number'])
                  .value_counts(normalize=True)
                  .rename('Prop')
                  .reset_index())
    figure = sns.barplot(x='Semi-subjective', y='Prop', hue='RST NCEP number', data=percent_df)

else:
    # For count
    figure = sns.countplot(x='Semi-subjective', hue='RST NCEP number', data=subdf)

plt.show()
