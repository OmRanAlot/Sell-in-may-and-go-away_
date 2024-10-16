import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

# Group by month and get the first and last day of each month
def get_first_last_days(group):
    return pd.concat([group.head(1), group.tail(1)])

# Function to check if a date is the end of the month
def is_end_of_month(date):
    return date == date + pd.offsets.BusinessMonthEnd(0)

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
    
    # print("Nov to April return for "+ sym + " was better " + str(NovAprBetter) + " out of " + str(total) + " , " + str(pct) )

    return [pct, total, df3]



df = pd.read_csv("returns_S&P.csv")
tickers = df["ticker"].to_list()
count = 1
for i in tickers:
    x = calculate_returns(i)[2].tail(2)
    try:
        if x["NovApril_rtn"].values[0] > x["MayOct_rtn"].values[0]:
            count +=1
    except:
        pass
print(count)
# --------------------------------------------------------------------------------SECTORS
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

print(xlu_etf[2].tail(2))


# ------------------------------------------------------------------------------BANK
# # JPM
# LIN = calculate_returns("LIN")
# # BAC
# SHW = calculate_returns("SHW")
# # WFC
# APD = calculate_returns("APD")
# # C
# DD = calculate_returns("DD")

# -----------------------------------------------------------------------------TECH

# GOOGL = calculate_returns("GOOGL")

# AMZN = calculate_returns("AMZN")

# APPL = calculate_returns("AAPL")

# NVDA = calculate_returns("NVDA")

# MSFT = calculate_returns("MSFT")

# TSLA = calculate_returns("TSLA")

# META = calculate_returns("META")
# FB = calculate_returns("FB")






