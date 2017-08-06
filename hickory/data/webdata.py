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

import urllib.request
import urllib.parse
import requests
from urllib.parse import quote

from hickory.util import yahoo_session_loader

EL = "\n"
DEL = "\n\n"

def DataReader(symbol, datasrc, start, end):

    if (datasrc == "yahoo"):
        bars = web.DataReader(symbol, datasrc, start, end)
    elif (datasrc == "yahoo_direct"):
        bars = retrieve_bars_data_from_yahoo(symbol, datasrc, start, end)
    else :
        bars = retrieve_bars_data_from_yahoo(symbol, datasrc, start, end)

    return bars

def retrieve_bars_data_from_yahoo(symbol, datasrc, start, end):

    start_epoch = str(start.timestamp()).split(".")[0]
    end_epoch = str(end.timestamp()).split(".")[0]

    symbol = symbol.replace(".US", "")

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

        # Only required if df is not float64 type
        if( len(df.index) > 0 and df.Open.dtype != "float64"):
            df = df[df.Open != "null"]
            df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']].apply(pd.to_numeric)

            if(not "=" in symbol):
                df = df[df.Volume > 0]

        elif (len(df.index) == 0):
            print("No historical data for code: [" + symbol + "]")
            raise ValueError

        #print(df.Open.values)
        #print(df.to_string())
        #print(df.tail())
        return df

def main():

    print("main....")
    end = datetime.today()
    start = end - timedelta(days=(1*365))

    bars = DataReader("1353.HK", "yahoo_direct", start, end)
    print(bars.tail(20))
 
if __name__ == "__main__":
    main()                
              



