#!/usr/bin/python

import numpy as np
import pandas as pd
import datetime
from datetime import tzinfo, timedelta, datetime
import time
import os

import traceback
import logging
from hickory.data import webdata


def SMA(df, column="Close", period=26):

    sma = df[column].rolling(window=period, min_periods=1, center=False).mean()
    return sma

def EMA(df, column="Close", period=20):

    ema = df[column].ewm(span=period, min_periods=period - 1).mean()
    return ema.to_frame('EMA')

def RSI(df, column="Close", period=14):
    # wilder's RSI
 
    delta = df[column].diff()
    up, down = delta.copy(), delta.copy()

    up[up < 0] = 0
    down[down > 0] = 0

    rUp = up.ewm(com=period - 1,  adjust=False).mean()
    rDown = down.ewm(com=period - 1, adjust=False).mean().abs()

    rsi = 100 - 100 / (1 + rUp / rDown)    

    return rsi.to_frame('RSI')

def BollingerBand(df, column="Close", period=20):

    sma = df[column].rolling(window=period, min_periods=period - 1).mean()
    std = df[column].rolling(window=period, min_periods=period - 1).std()

    up = (sma + (std * 2)).to_frame('BBANDUP')
    lower = (sma - (std * 2)).to_frame('BBANDLO')
    return up, lower

def main():

    print("main....")
    end = datetime.today()
    start = end - timedelta(days=(1*365))

    bars = webdata.DataReader("1398.HK", "google", start, end)
    print(bars.tail(20))

    signals = pd.DataFrame(index=bars.index)
    pd.options.mode.chained_assignment = None  # default='warn'

    # Create the set of short and long simple moving averages over the
    # respective periods
    signals['close'] = bars['Close']
    bars['Volume'] = bars['Volume'].replace('null', 0)
    signals['vol'] = bars['Volume']
    signals['turnover'] = bars['Close'] * bars['Volume'].astype(float)

    col = "Close"
    signals['sma50'] = SMA(bars, col, 50)
    signals['rsi14'] = RSI(bars, col, 14)

    print(signals.tail(20))

if __name__ == "__main__":
    main()

