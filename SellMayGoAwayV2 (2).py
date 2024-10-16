#!/usr/bin/env python
# coding: utf-8

# In[628]:


pip install yfinance


# In[1]:


import yfinance as yf
import pandas as pd
import numpy as np
import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")


# # Function

# In[33]:


def calculate_returns(sym):
    # Fetch data for Stock Ticker
    ticket = yf.Ticker(sym)

    # Get historical market data
    hist = ticket.history(period='max')
    
    hist = hist.reset_index()
    
    hist['month'] =  hist.Date.dt.month
    
    # Ensure 'date' column is in datetime format
    hist['Date'] = pd.to_datetime(hist['Date'])

    # Set 'date' column as index
    hist.set_index('Date', inplace=True)
    
    # Group by month and get the first and last day of each month
    def get_first_last_days(group):
        return pd.concat([group.head(1), group.tail(1)])

    # Group by month and apply the function
    monthly_groups = hist.groupby(hist.index.to_period('M'))
    first_last_days = monthly_groups.apply(get_first_last_days).reset_index(level=0, drop=True)
    first_last_days.reset_index(inplace=True)
    df = first_last_days[(first_last_days['month']==5) |(first_last_days['month']==10)]
    
    # Function to check if a date is the end of the month
    def is_end_of_month(date):
        return date == date + pd.offsets.BusinessMonthEnd(0)

    # Apply the function to create the new column
    # df['end_of_month'] = df['Date'].apply(is_end_of_month)
    df.loc[:,'end_of_month'] = df['Date'].apply(is_end_of_month)
    
    may = df[(df['month']==5)].reset_index()
    # may df shows first and eod, we will skip every other row to only get eod
    may = may.iloc[::2].reset_index(drop=True)

    oct = df[(df['month']==10)].reset_index()
    oct = oct[oct['end_of_month']==True]

    may['oct_Close'] = oct['Close']
    may['year'] = may.Date.dt.year
    oct['year'] = oct.Date.dt.year
    
    df = may.merge(oct[['Close','year']],on='year')
    df.drop('oct_Close', axis=1, inplace=True)

    df.rename(columns = {'Close_x': 'may_Close',
          'Close_y':'oct_Close' },inplace=True)

    df['MayOct_rtn'] = (df['oct_Close'] - df['may_Close']) / df['may_Close']
    
    ######################################
    ##  Getting Nov to Apr returns       #
    ######################################
    
    df2 = first_last_days[(first_last_days['month']==4) |(first_last_days['month']==11)]
    df2.loc[:, 'end_of_month'] = df2['Date'].apply(is_end_of_month)
    
    # Create nov
    nov = df2[(df2['month']==11)].reset_index()
    nov = nov.iloc[::2].reset_index(drop=True)
    
    # Create april
    april = df2[(df2['month']==4)].reset_index()
    april = april[april['end_of_month']==True]

    # Create the april_Close and year column for nov
    nov['april_Close'] = april['Close']
    nov['year'] = nov.Date.dt.year
    
    # Create the year column for april
    april['year'] = april.Date.dt.year

    # Remove the first row
    april = april.drop(april.index[0])

    # Decrease the year by one for the later merge
    # This is so you can compare data of the following year for April, Ex. Nov 1st 2023 and April 30th 2024
    april['year'] = april['year'] - 1
    
    # Merge nov and april on year
    df2 = nov.merge(april[['Close','year']],on='year')

    # Create april_Close column
    df2.drop('april_Close', axis=1, inplace=True)
    df2.rename(columns = {'Close_x': 'nov_Close',
              'Close_y':'april_Close' },inplace=True)
    
    # Calculate the return
    df2['NovApril_rtn'] = (df2['april_Close'] - df2['nov_Close']) / df2['nov_Close']
    
    ##############################################
    ##  Merger May/Oct and Nov/Apr returns       #
    ##############################################
    
    df3 = df2[['year','nov_Close','april_Close','NovApril_rtn']].merge(df[['year','may_Close','oct_Close','MayOct_rtn']],on='year')
    
    NovAprBetter = df3[df3['NovApril_rtn'] > df3['MayOct_rtn']]['year'].count()
    total = df3['year'].count()
    
    pct = NovAprBetter / total
    
    print("Nov to April return for "+ sym + " was better " + str(NovAprBetter) + " out of " + str(total) + " , " + str(pct) )

    return df3


# In[34]:


SPY = calculate_returns('SPY')


# In[35]:


DJI = calculate_returns('DIA')


# In[36]:


NasComp = calculate_returns('QQQ')


# In[37]:


#Mid
SP400 = calculate_returns('IJH')


# In[38]:


Russell = calculate_returns('IWM')


# In[39]:


SPY['ticker'] = 'SPY'


# In[40]:


DJI['ticker'] = 'DJI'
NasComp['ticker'] = 'QQQ'
SP400['ticker'] = 'IJH'
Russell['ticker'] = 'IWM'


# In[41]:


SPY


# In[96]:


result = pd.concat([SPY,DJI, NasComp, SP400, Russell])


# In[97]:


result['NovBetter'] = result['NovApril_rtn'] > result['MayOct_rtn'] 


# In[98]:


result.ticker


# In[99]:


tbl = result.groupby(['ticker','NovBetter'])['year'].count().unstack()


# In[100]:


tbl


# In[19]:


tbl.to_csv('C:\Joohi\data.csv')


# In[16]:


import seaborn as sns
import matplotlib.pyplot as plt


# In[71]:


df = result[result['ticker']=='QQQ'][['year','ticker','NovApril_rtn','MayOct_rtn']]


# In[117]:


df['difference'] = df['MayOct_rtn'] - df['NovApril_rtn'] 


# In[122]:


df.sort_values(by='difference').to_csv('C:\Joohi\qqq.csv')


# In[76]:


# Set up the figure and axis
fig, ax = plt.subplots(figsize=(10, 6))

# Set the width of the bars
bar_width = 0.35

# Set the positions of the bars on the x-axis
years = df['year']
indices = np.arange(len(years))

# Plot bars for Nov-April and May-Oct returns
ax.bar(indices - bar_width / 2, df['NovApril_rtn'], bar_width, label='Nov-April Returns')
ax.bar(indices + bar_width / 2, df['MayOct_rtn'], bar_width, label='May-Oct Returns')

# Add labels, title, and legend
ax.set_xlabel('Year')
ax.set_ylabel('Returns')
ax.set_title('Nov-April vs May-Oct Returns Over Time for QQQ')
ax.set_xticks(indices)
ax.set_xticklabels(years, rotation=45, ha='right')
ax.legend()

# Display the plot
plt.tight_layout()
plt.show()


# In[ ]:





# In[17]:


# Line plot with seaborn, grouping by 'Category' column
sns.lineplot(x='year', y='NovApril_rtn', hue='ticker', data=result)

# Add title and labels
plt.title('Line Plot Grouped by Category')
plt.xlabel('Time')
plt.ylabel('Value')

# Display the plot
plt.show()


# In[103]:


result[result['ticker']=='QQQ']


# In[124]:


plt.figure(figsize=(12, 6))


# Line plot with seaborn, grouping by 'Category' column
sns.lineplot(x='year', y='NovApril_rtn', data=result[result['ticker']=='QQQ'],label='Nov-April Returns', marker='o', color='royalblue')
sns.lineplot(x='year', y='MayOct_rtn', data=result[result['ticker']=='QQQ'],label='May-Oct Returns', marker='o', color='orange')

highlight_years = result[(result['ticker']=='QQQ') & (result['MayOct_rtn']> result['NovApril_rtn'])].year

# Step 5: Highlight the years where May-Oct returns > Nov-Apr returns
for year in highlight_years:
    plt.axvline(x=year, color='lightgray', linestyle='--', alpha=0.6)

plt.axhline(y=0, color='grey', linestyle='-', linewidth=1)
# Add title and labels
plt.title('QQQ performance over time')
plt.xlabel('Time')
plt.ylabel('Returns')
plt.legend()
# Display the plot
plt.show()


# In[ ]:





# # Sectors

# In[78]:


# Communication Services ETF
xlc_etf = calculate_returns("XLC")

# Consumer Discretionary ETF
xly_etf = calculate_returns("XLY")

# Consumer Staples ETF
xlp_etf = calculate_returns("XLP")

# Energy ETF
xle_etf = calculate_returns("XLE")

# Financials ETF
xlf_etf = calculate_returns("XLF")

# Healthcare ETF
xlv_etf = calculate_returns("XLV")

# Industrials ETF
xli_etf = calculate_returns("XLI")

# Materials ETF
xlb_etf = calculate_returns("XLB")

# Real Estate ETF
xlre_etf = calculate_returns("XLRE")

# Technology ETF
xlk_etf = calculate_returns("XLK")

# Utilities ETF
xlu_etf = calculate_returns("XLU")


# In[79]:


xlc_etf['ticker'] = 'XLC'
xlk_etf['ticker'] = 'XLK'
xlb_etf['ticker'] = 'XLB'
xlre_etf['ticker'] = 'XLRE'
xli_etf['ticker'] = 'XLI'
xlv_etf['ticker'] = 'XLV'
xlf_etf['ticker'] = 'XLF'
xle_etf['ticker'] = 'XLE'
xlp_etf['ticker'] = 'XLP'
xly_etf['ticker'] = 'XLY'


# In[80]:


xlc_etf


# In[81]:


sectors = pd.concat([xlc_etf,xlk_etf, xlb_etf, xlre_etf, xli_etf,xlv_etf,xlf_etf,xle_etf,xlp_etf,xly_etf])


# In[82]:


sectors['NovBetter'] = sectors['NovApril_rtn'] > sectors['MayOct_rtn'] 


# In[83]:


tbl2 = sectors.groupby(['ticker','NovBetter'])['year'].count().unstack()


# In[85]:


tbl2.to_csv('C:\Joohi\sector.csv')



# In[127]:


sectors[sectors['ticker']=='XLF'].to_csv('C:/Joohi/xlf.csv')


# In[113]:


# Line plot with seaborn, grouping by 'Category' column
sns.lineplot(x='year', y='NovApril_rtn', data=sectors[sectors['ticker']=='XLF'],label='Nov-April Returns')
sns.lineplot(x='year', y='MayOct_rtn', data=sectors[sectors['ticker']=='XLF'],label='May-Oct Returns')

# Add title and labels
plt.title('XLF performance over time')
plt.xlabel('Time')
plt.ylabel('Returns')
plt.legend()
# Display the plot
plt.show()


# In[125]:


plt.figure(figsize=(12, 6))


# Line plot with seaborn, grouping by 'Category' column
sns.lineplot(x='year', y='NovApril_rtn', data=sectors[sectors['ticker']=='XLF'],label='Nov-April Returns', marker='o', color='green')
sns.lineplot(x='year', y='MayOct_rtn', data=sectors[sectors['ticker']=='XLF'],label='May-Oct Returns', marker='o', color='teal')

highlight_years = sectors[(sectors['ticker']=='XLF') & (sectors['MayOct_rtn']> sectors['NovApril_rtn'])].year

# Step 5: Highlight the years where May-Oct returns > Nov-Apr returns
for year in highlight_years:
    plt.axvline(x=year, color='lightgray', linestyle='--', alpha=0.6)

plt.axhline(y=0, color='grey', linestyle='-', linewidth=1)
# Add title and labels
plt.title('XLF performance over time')
plt.xlabel('Time')
plt.ylabel('Returns')
plt.legend()
# Display the plot
plt.show()


# # Banks

# In[129]:


# JPM
JPM = calculate_returns("JPM")
# BAC
BAC = calculate_returns("BAC")
# WFC
WFC = calculate_returns("WFC")
# C
c = calculate_returns("C")


# In[131]:


JPM['ticker'] = 'JPM'
BAC['ticker'] = 'BAC'
WFC['ticker'] = 'WFC'
c['ticker'] = 'C'


# In[132]:


banks = pd.concat([JPM,BAC, WFC, c])


# In[133]:


banks['NovBetter'] = banks['NovApril_rtn'] > banks['MayOct_rtn'] 


# In[134]:


tbl3 = banks.groupby(['ticker','NovBetter'])['year'].count().unstack()


# In[137]:


tbl3.to_csv('C:/Joohi/banks.csv')


# In[ ]:


banks[banks['ticker']=='XLF'].to_csv('C:/Joohi/xlf.csv')


# In[ ]:





# In[ ]:





# In[ ]:





# # Materials

# In[51]:


# JPM
LIN = calculate_returns("LIN")
# BAC
SHW = calculate_returns("SHW")
# WFC
APD = calculate_returns("APD")
# C
DD = calculate_returns("DD")


# # Significant Seven

# In[56]:


GOOGL = calculate_returns("GOOGL")

AMZN = calculate_returns("AMZN")

APPL = calculate_returns("AAPL")

NVDA = calculate_returns("NVDA")

MSFT = calculate_returns("MSFT")

TSLA = calculate_returns("TSLA")

META = calculate_returns("META")
FB = calculate_returns("FB")


# In[ ]:




