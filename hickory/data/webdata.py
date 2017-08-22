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

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def DataReader(symbol, datasrc, start, end):

    if (datasrc == "yahoo"):
        bars = web.DataReader(symbol, datasrc, start, end)
    elif (datasrc == "yahoo_direct"):
        #try:
        bars = retrieve_bars_data_from_yahoo(symbol, datasrc, start, end)
        #except:
        #       
    elif (datasrc == "google"):
        bars = retrieve_bars_data_from_google(symbol)
    else:
        bars = retrieve_bars_data_from_yahoo(symbol, datasrc, start, end)

    return bars


def init_cookies_and_crumb():

    yahoo_session_loader.load()


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
            #print("No historical data for code: [" + symbol + "]")
            raise ValueError

        #print(df.Open.values)
        #print(df.to_string())
        #print(df.tail())
        return df

def retrieve_bars_data_from_google(code):

    if (code[0] == "0"):
        code = code[1:]

    if (".HK" in code):
        code = code.replace(".HK","")

    if (is_number(code)):
        code = "HKG:" + code.rjust(4, '0')
    else:
        code = code.upper()

    #print("Retrieved Data from Google for code: [" + code + "]")
    url1 = 'http://www.google.com.hk/finance/historical?q=' + code + '&num=200&start=0'
    url2 = 'http://www.google.com.hk/finance/historical?q=' + code + '&num=200&start=200'
    r1 = urllib.request.urlopen(url1)
    r2 = urllib.request.urlopen(url2)
    soup = BeautifulSoup(r1, "html5lib")
    tabulka = soup.find("table", {"class" : "gf-table historical_price"})

    soup = BeautifulSoup(r2, "html5lib")
    tabulkb = soup.find("table", {"class" : "gf-table historical_price"})

    if not os.name == 'nt':
        csvfilename = "/tmp/histdata/" + code.replace(":", "") + '.csv'
    else:
        csvfilename = "C:\\Temp\\histdata\\" + code.replace(":", "") + '.csv'

    with open(csvfilename, 'w') as csvfile:

        fieldnames = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in tabulka.findAll('tr')[1:]:
            col = row.findAll('td')
            date = col[0].string.strip()
            sopen = col[1].string.replace(",", "").strip()
            high = col[2].string.replace(",", "").strip()
            low = col[3].string.replace(",", "").strip()
            close = col[4].string.replace(",", "").strip()
            volume = col[5].string.replace(",", "").strip()

            #print(",".join([date, sopen, high, low, close, volume]))
            writer.writerow({'Date': date, 'Open': sopen, 'High': high, 'Low': low, 'Close': close, 'Volume': volume})

        if (tabulkb and len(tabulkb.findAll('tr')) > 0):
            for row in tabulkb.findAll('tr')[1:]:
                col = row.findAll('td')
                date = col[0].string.strip()
                sopen = col[1].string.replace(",", "").strip()
                high = col[2].string.replace(",", "").strip()
                low = col[3].string.replace(",", "").strip()
                close = col[4].string.replace(",", "").strip()
                volume = col[5].string.replace(",", "").strip()

                #print(",".join([date, sopen, high, low, close, volume]))
                writer.writerow({'Date': date, 'Open': sopen, 'High': high, 'Low': low, 'Close': close, 'Volume': volume})

    df = pd.DataFrame.from_csv(csvfilename, header=0, sep=',', index_col=0)
    df.sort_index(inplace=True)

    #print(df.head())
    return df


def main():

    print("main....")
    end = datetime.today()
    start = end - timedelta(days=(1*365))

    bars = DataReader("1333.HK", "google", start, end)
    print(bars.tail(20))
 
    bars = DataReader("1353.HK", "google", start, end)
    print(bars.tail(20))
 
if __name__ == "__main__":
    main()                
              



