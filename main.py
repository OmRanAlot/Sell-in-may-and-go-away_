import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
warnings.filterwarnings("ignore")





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


SPY = calculate_returns('SPY')
DJI = calculate_returns('DIA')
NasComp = calculate_returns('QQQ')
SP400 = calculate_returns('IJH')
Russell = calculate_returns('IWM')

SPY['ticker'] = 'SPY'
DJI['ticker'] = 'DJI'
NasComp['ticker'] = 'QQQ'
SP400['ticker'] = 'IJH'
Russell['ticker'] = 'IWM'

result = pd.concat([SPY,DJI, NasComp, SP400, Russell])

result['NovBetter'] = result['NovApril_rtn'] > result['MayOct_rtn'] 

tbl = result.groupby(['ticker','NovBetter'])['year'].count().unstack()

df = result[result['ticker']=='QQQ'][['year','ticker','NovApril_rtn','MayOct_rtn']]
df['difference'] = df['MayOct_rtn'] - df['NovApril_rtn'] 

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


result[result['ticker']=='QQQ']

# Set up the figure and axis
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


#Sectors
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


sectors = pd.concat([xlc_etf,xlk_etf, xlb_etf, xlre_etf, xli_etf,xlv_etf,xlf_etf,xle_etf,xlp_etf,xly_etf])

sectors['NovBetter'] = sectors['NovApril_rtn'] > sectors['MayOct_rtn'] 
tbl2 = sectors.groupby(['ticker','NovBetter'])['year'].count().unstack()


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



# Group by month and get the first and last day of each month
def get_first_last_days(group):
    return pd.concat([group.head(1), group.tail(1)])

# Function to check if a date is the end of the month
def is_end_of_month(date):
    return date == date + pd.offsets.BusinessMonthEnd(0)

def calculate_returns_ad(sym):
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
    
    # print("Nov to April return for "+ sym + " was better " + str(NovAprBetter) + " out of " + str(total) + " , " + str(pct) )

    return [pct, total, df3]



df = pd.read_csv("returns_S&P.csv")
tickers = df["ticker"].to_list()
count = 1
for i in tickers:
    x = calculate_returns_ad(i)[2].tail(2)
    try:
        if x["NovApril_rtn"].values[0] > x["MayOct_rtn"].values[0]:
            count +=1
    except:
        pass
print(count)



