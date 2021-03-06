#The  hypothesis is that stocks that drop hard one day will rebond a certain amount the next day
#If we can find how much they rebound vs how much they dropped perhaps we can buy stocks thay dropped and sell
#them when they reach their predicted high point the next day

#This code is intended to be run once a day once the stock market closes. The intent of the function is to 
#look up the tickers in the S&P 500 and find once the dropped greater than a certain percentage (3% to start)
#The function stores tickers that droped greater than 3% and then the next day, it sees how much those tickers 
#rose from open, (High - Open). It stores the data for how much the stocks dropped and then how much they rose 
#in seperate csv files.
#This will be run on a machine to collect data, once enough data is collected, a regression will be analyzed to see
#if there is a trend for how much a stocl dropped vs how much it can rise the next day

### Installs, uncoment if needed
#pip install yfinance
#pip install yahoofinancials
#pip install requests beautifulsoup4

### mports
import pandas as pd
import numpy as np
import yfinance as yf
#from yahoofinancials import YahooFinancials
from bs4 import BeautifulSoup
import requests
from csv import writer
from datetime import date
from datetime import timedelta
import time 

###define some variables
#csv file locations: Change these based on the locations of your machine. 
stored_data_drop = '\\Users\\noahw\\Python-Finance\\S&P-Dip-Data.csv'
stored_data_next_day = '\\Users\\noahw\\Python-Finance\\S&P-Dip-Data_next_day.csv'

today = date.today() #Get todays Date
yesterday = today - timedelta(days = 1) #Get yesterdays date

### Functions, there are 2 main functions defined here. SP_data_pull() and next_day_rise()

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

    #sort table by percent drop
    Top_drop = df #changing the name of the dataframe
    # Top_drop = df.sort_values(df.columns[0]) # Uncomment this if you want to order the values by most dropped

    Top_tickers_data = Top_drop[Top_drop.iloc[:,0] < -3.00] # only keep values that dropped by greater than 3 percent
    Top_TCKRS = Top_tickers_data.index.values.tolist() #Get a list of the tickers in the drop data
    Top_tickers_data.insert(loc=0, column='Date', value=today)   #add the date to the first column of the table for use when analyzing data
    return Top_tickers_data, Top_TCKRS
    

# The next_day_rise() function takes the tickers from the drop data and checks how much they rose the next day
#This data will be used to show how stocks that dropped hard one day may rise the next day
def next_day_rise(tickers):
    today = date.today() #ensure we have todays date
    #The intent of this function is to pull the tickers from the SP_data_pull function and determine the max percent they rose the next day (max - open, 1day)

    # print(tickers) #This line is just a test to show it is pulling the right tickers from SP_data_pull()
    next_day_data = yf.download(tickers, today, rounding = 2)
    next_day_open = next_day_data['Open'] #Pull the open from next day data
    next_day_high = next_day_data['High'] #pull the high point in the next day data
    next_day_max_rise = ((next_day_high-next_day_open)/next_day_open)*100 # finds the percent the dropped stocks rose the next day. 

    next_day_df = pd.DataFrame(next_day_max_rise) #convert to Data frame
    next_day_df = next_day_df.transpose() #transpose to match drop data
    next_day_df.insert(loc=0, column='Date', value = today) #add the date to the first column of the table for use when analyzing data


    next_day_df.to_csv(stored_data_next_day, mode = 'a', index = True, header = True) #store the next day drop in the csv file

#Now that everything is defined, this section calls the functions 

data_to_csv = sp_data_pull() 
drop_data_to_csv = data_to_csv[0] #returns the drop data to go to the csv file
drop_tickers = data_to_csv[1] #returns the tickers from the drop data

drop_data_to_csv.to_csv(stored_data_drop, mode = 'a', index = True, header = True) #write the data from today to CSV

next_day_rise(drop_tickers) #use the tickers from the drop data in the next_day_rise() function


#Both data outputs now add a date column as the first column for data organization. 
# Data is in alphabetical order by ticker, both drop data and next day data should be in same order
# Code now stores drop data and next day rise data in seperate CSV files, will combine for analysis
#once ready for use, add a while loop to call the functions and add a sleep() call to run this once a day. 
