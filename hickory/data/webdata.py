#!/usr/bin/python

import numpy as np
import pandas as pd
import datetime
from datetime import tzinfo, timedelta, datetime
import time

import traceback
import logging
import io
from pandas_datareader import data as web, wb
from bs4 import BeautifulSoup
import csv
import os
import urllib.request
import urllib.parse
import requests
from urllib.parse import quote

from hickory.util import yahoo_session_loader

EL = "\n"
DEL = "\n\n"
YAHOO_LIMIT = 50


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def DataReader(symbol, datasrc, start, end):

#    print("DataReader: " + symbol + "," + datasrc + "," + str(start) + "," + str(end))

    if (datasrc == "yahoo"):
        bars = web.DataReader(symbol, datasrc, start, end)
    elif (datasrc == "yahoo_direct"):
        #try:
        bars = retrieve_bars_data_from_yahoo(symbol, datasrc, start, end)

#        if (bars == None):
#            print("Symbol empty: " + symbol)

        if (len(bars) <= 50):
            #print("Issue in Yahoo API, switching to use Google")
            #bars = retrieve_bars_data_from_google(symbol)
            pass
        #except:
        #       
    else:
        bars = retrieve_bars_data_from_yahoo(symbol, datasrc, start, end)

    return bars


def init_cookies_and_crumb():

    yahoo_session_loader.load()

def reset_cookies_and_crumb():

    yahoo_session_loader.reset()

def retrieve_bars_data_from_yahoo(symbol, datasrc, start, end):

    start_epoch = str(start.timestamp()).split(".")[0]
    end_epoch = str(end.timestamp()).split(".")[0]

    if (".US" in symbol):
        symbol = symbol.replace(".US", "")
        symbol = symbol.replace(".", "-")
    
    #print("Retrieving data for [" + symbol + "] from " + str(start_epoch) + " to " + str(end_epoch))

    cookies = None
    crumb = None

    session = yahoo_session_loader.load()
    cookies = session.getCookies()
    crumb = session.getCrumb()

    if (cookies and crumb):

        url = 'https://query1.finance.yahoo.com/v7/finance/download/'  + symbol + '?period1=' + start_epoch + '&period2=' + end_epoch + '&interval=1d&events=history&crumb=' + crumb
        
        response = requests.get(url, cookies=cookies)
        #print("url: " + url);
        #print(response.content.decode("utf-8"))

        df = pd.read_csv(io.StringIO(response.content.decode("utf-8")), header=0, sep=',', index_col=0)

        # Converting the index as date
        df.index = pd.to_datetime(df.index)
        lidx = len(df.index) > 0

        if lidx > 0:
            df = df[df['Open'].notnull()]
        
        # Only required if df is not float64 type
        if( len(df.index) > 0 and df.Open.dtype != "float64"):
            df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']].apply(pd.to_numeric)

            if(not "=" in symbol):
                df = df[df.Volume > 0]
        elif (len(df.index) == 0):
            print("No historical data for code: [" + symbol + "]")
            raise ValueError

        #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        #print(df.head())
        #print(df.to_string())
        #print(df.tail())
        return df

def main():

    print("main....")
    end = datetime.today()
    #start = end - timedelta(days=(1*365))
    start = end - timedelta(days=(1*400))

    #bars = DataReader("0923.HK", "yahoo_direct", start, end)
    
    for code in ["AABA", "AA", "AAC", "A", "AAL", "AAMC"]:
        bars = DataReader(code, "yahoo_direct", start, end)
        #if (not bars == None):
        print(bars.tail())
 
    #bars = DataReader("0700.HK", "yahoo_direct", start, end)
    #print(bars.tail(20))
 
if __name__ == "__main__":
    main()                
              



