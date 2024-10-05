from SellMayGoAwayV2 import *
import pandas as pd

df_sp = pd.read_csv('returns_S&P.csv')
df_nyse = pd.read_csv('returns_NYSE.csv')
df_nasdaq = pd.read_csv('returns_NASDAQ.csv')

industries = df_nyse["sector"].unique().tolist()

values_sp = df_sp["returns"].tolist()
sp_sector_avg = df_sp.groupby('sector')['returns'].mean().reset_index()

values_nyse = df_nyse["returns"].tolist()
nyse_sector_avg = df_nyse.groupby('sector')['returns'].mean().reset_index()

values_nasdaq = df_nasdaq["returns"].tolist()
nasdaq_sector_avg = df_nasdaq.groupby('sector')['returns'].mean().reset_index()

average_nasdaq = df_nasdaq["returns"].mean()
stderr_nasdaq = df_nasdaq["returns"].std()/np.sqrt(len(df_nasdaq))

# Merge the datasets to ensure sectors are aligned
merged_data = pd.merge(nasdaq_sector_avg, nyse_sector_avg, on='sector', how='inner', suffixes=('_nasdaq', '_nyse'))
merged_data = pd.merge(merged_data, sp_sector_avg, on='sector')
merged_data.rename(columns={'returns': 'avg_return_sp500'}, inplace=True)

width = 0.25
n_sectors = len(merged_data)
indicies = np.arange(n_sectors)

plt.bar(indicies, merged_data["avg_return_sp500"], width=width, label='S&P 500')
plt.bar(indicies+width, merged_data["returns_nyse"], width=width, label='NYSE')
plt.bar(indicies+2*width, merged_data["returns_nasdaq"], width=width, label='NASDAQ')

plt.xticks(indicies + width, merged_data['sector'], rotation=30, ha='right')

plt.tight_layout()
plt.legend()
plt.show()


