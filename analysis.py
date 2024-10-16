import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

df_sp = pd.read_csv('returns_S&P.csv')
df_nyse = pd.read_csv('returns_NYSE.csv')
df_nasdaq = pd.read_csv('returns_NASDAQ.csv')

industries = df_nyse["sector"].unique().tolist()

values_sp = df_sp["returns"].tolist()
sp_mean = df_sp['returns'].mean()
sp_stdev = df_sp['returns'].std()

print(df_sp["returns"].describe())


#Each sector versus overall market
average_return_by_sector = df_sp.groupby('sector')['returns'].mean().sort_values(ascending=False)
plt.bar(average_return_by_sector.index, average_return_by_sector.values)

#Normal Distribution curve line
# count, bins, _ = plt.hist(values_sp, bins=50, label='S&P 500')
# min, max = plt.xlim() #get limits
# x = np.linspace(min, max, 100)
# p = norm.pdf(x, sp_mean, sp_stdev)
# p = p * 10

# #add line
# plt.plot(x, p, 'k', linewidth=2)

plt.xlabel('Returns')
plt.ylabel('Frequency')
plt.title('Histogram of Returns')

plt.legend()
plt.show()








