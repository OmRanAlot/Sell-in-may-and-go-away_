import pandas as pd
import yfinance as yf
import numpy as np
from main import *
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle

df_tickers = pd.read_csv("returns_S&P.csv")
df = pd.DataFrame(columns=["ticker", "sector", "sub-industry", "returns", "totalYears"])
print(df_tickers)
for x in df_tickers["ticker"]:
    try:
        ticker = yf.Ticker(x)
        info = ticker.info
        industry = info.get("industry")
        sector = info.get("sector")
        returns = calculate_returns(x)[0]
        totalYears = calculate_returns(x)[1]
        df.loc[len(df)] = [x, sector, industry, returns, totalYears]
        print(f"{x} complete")
    except:
        print(f"skipping {x}")

df.to_csv("returns_S&P.csv")

#Get all tickers nyse website
'''
url = "https://www.nyse.com/listings_directory/stock"

#set up settings
  #user agent to prevent being blocked and not get detect from my own computer
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
options = webdriver.ChromeOptions()      
options.add_argument(f"user-agent={user_agent}")
options.page_load_strategy = 'normal'

driver = webdriver.Chrome(options=options)
driver.get(url)
results = []
current_page = 1
running = True
while running:
    #get all the rows in the table
    WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'tr'))
        )
    table = driver.find_element(By.CSS_SELECTOR, "table.table-data.w-full.table-border-rows")

    rows = table.find_elements(By.TAG_NAME, 'tr')
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, 'td')  # Get all cells in the row
        if cells:  # Check if the row has cells
            # Collect cell text into a list
            row_data = [cell.text for cell in cells]
            results.append(row_data)  # Append the row data to results

    print("finshed")
    #find the next button and click it
    try:
        driver.find_element(By.CSS_SELECTOR, "a[rel='next']").click()
    except:
        running = False
    current_page += 1
    print("Going to page: " , current_page)
    
df = pd.DataFrame(results)
df.to_csv("tickers.csv", index=False)
df.to_pickle("tickers.pkl")

'''

# Get the S&P 500 tickers from Wikipedia and run the function on each one
'''url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
table = pd.read_html(url)[0]

columns = ["ticker", "industry", "sub-industry", "returns", "totalYears"]
df = pd.DataFrame(columns=columns)

for i in range(len(table["Symbol"])):
    try:
        ticker = table["Symbol"][i]
        industry = table["GICS Sector"][i]
        sub_industry = table["GICS Sub-Industry"][i]
        returns = calculate_returns(ticker)[0]
        totalYears = calculate_returns(ticker)[1]
        # print(ticker, industry, sub_industry, returns, totalYears)
        df.loc[len(df)] = [ticker, industry, sub_industry, returns, totalYears]

    except:
        pass

df.to_csv("returns_S&P.csv")'''
