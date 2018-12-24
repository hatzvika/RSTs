import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

label_list = ['RST-E', 'RST-W', 'RST-C', 'PT weak', 'PT med', 'High-E', 'High-W', 'High-N', 'High-C', 'Weak L-N', 'Low-W', 'Weak L-E', 'Shrv L-C']
use_percent = 1
df = pd.read_excel('C:/Users/hatzv/Documents/Geography/RSTs/python/Analysis/Results/Kuri_synoptic_classification_2000_2004.xlsx', 'Try')
# figure = sns.jointplot(x=df.columns[2], y=df.columns[3], data=df, kind='hex')
# figure = sns.violinplot(x=df.columns[1], y=df.columns[3], data=df, scale='count', cut=0, gridsize=19)
# figure = sns.catplot(x=df.columns[3], hue=df.columns[1], data=df, kind='count')
subdf = df.loc[df['RST NCEP number'].isin((1, 3))]

if use_percent:
    # For percentage
    percent_df = (subdf['Semi-subjective']
                  .groupby(df['RST NCEP number'])
                  .value_counts(normalize=True)
                  .rename('Percent')
                  .reset_index())*100
    figure = sns.barplot(x='Semi-subjective', y='Percent', hue='RST NCEP number', data=percent_df)
    figure.set_xlabel('Synoptic Class')
    figure.set_ylabel('Percent')
    figure.set_xticklabels(label_list, rotation=70, fontsize=10) #, fontweight='bold')
    legend=plt.legend(loc='upper right')
    legend.get_texts()[0].set_text('Eastern Axis')
    legend.get_texts()[1].set_text('Central Axis')

    # for tick in figure.yaxis.get_major_ticks():
    #     tick.label1.set_fontweight('bold')
else:
    # For count
    figure = sns.countplot(x='Semi-subjective', hue='RST NCEP number', data=subdf)

plt.gcf().subplots_adjust(bottom=0.3)
plt.savefig('Fig 6.png', dpi=300)
plt.show()
