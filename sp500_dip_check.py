

#pip install yfinance

#pip install yahoofinancials

#pip install requests beautifulsoup4

import pandas as pd
import numpy as np
import yfinance as yf
#from yahoofinancials import YahooFinancials
from bs4 import BeautifulSoup
import requests
from csv import writer
from datetime import date
from datetime import timedelta


#csv file location: 
stored_data = '\\Users\\noahw\\Python-Finance\\S&P-Dip-Data.csv'

today = date.today() #Get todays Date
yesterday = today - timedelta(days = 1) #Get yesterdays date

#SP_data_pull() is used Extract all tickers from wiki list of S&P 500 tickers
#With the ticker table it then pulls the daily data from yfinance
#once the daily data is pulled, the function sorts by largest drop and trims to be stocks with a drop greater than 4%
def sp_data_pull():

    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find_all('table')
    #The first table is the table of all tickers
    wiki_tckr = table[0]
    #establish empty table
    ticker_table = []
    #get all table rows
    rows = wiki_tckr.find_all('tr')
    #For loop through table rows and extract data to table
    for i in rows:
        data = i.find_all_next('td')[0].text
        data = data.replace('\n','')
        ticker_table.append(data)

    #pull data from yfinance
    daily_data = yf.download(ticker_table, yesterday, today, rounding=2)

    Open = daily_data['Open']
    Close = daily_data['Close']
    percent_dif = ((Close - Open)/Open)*100

    #Transpose data to make it easier to work with
    df = pd.DataFrame(percent_dif)  #turn it into a dataframe
    df = df.transpose() # transpose the data
    #df = df.drop(df.columns[0], axis = 1) # The first column will be NaN since, drop it, need to check during week, over weekend this was not needed and broke it

    #sort table by percent drop
    Top_drop = df.sort_values(df.columns[0])
    #rename column to percent
  
    #Top_drop ###Uncomment if you want to see top drop table without filtering

    Top_tickers = Top_drop[Top_drop.iloc[:,0] < -3.00] # only keep values that dropped by greater than 3 percent
    return Top_tickers


#date = datetime.datetime.now()

data_to_csv = sp_data_pull()

data_to_csv.to_csv(stored_data, mode = 'a', index = True, header = True) #write the data from today to CSV

#Next Step is to write a function that will check the high point of the tickers in data compared to the open to see how much they rise. 
#Need to add a column (1st column ) in csv for date to make analysis easier
#Make sure to check line 57 above during the week



