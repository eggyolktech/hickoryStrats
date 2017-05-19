import numpy as np
import pandas as pd
import quandl   # Necessary for obtaining financial data easily
import datetime
from datetime import tzinfo, timedelta, datetime
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import traceback
import logging

from pandas_datareader import data as web, wb
from hickoryBase import Strategy
import json

import urllib.request
import urllib.parse
import requests
import re
import configparser
import io

config = configparser.ConfigParser()
config.read('config.properties')

EL = "\n"
DEL = "\n\n"

class MacdStocCrossScanner(Strategy):
    """    
    Requires:
    symbol - A stock symbol on which to form a strategy on.
    bars - A DataFrame of bars for the above symbol.
    short_window - Lookback period for short moving average.
    long_window - Lookback period for long moving average."""

    def __init__(self, symbol, bars, short_window=100, long_window=400):
        self.symbol = symbol
        self.bars = bars

        self.short_window = short_window
        self.long_window = long_window
        self.stoch_window = 16
        self.macd_window = 26

    def generate_signals(self):
        """Returns the DataFrame of symbols containing the signals
        to go long, short or hold (1, -1 or 0)."""
        signals = pd.DataFrame(index=self.bars.index)
        signals['signal'] = 0.0
        signals['signal_stoch_x'] = 0.0
        signals['signal_macd_x'] = 0.0
        #signals['signal_stoch_short'] = 0.0
        
        # Create the set of short and long simple moving averages over the 
        # respective periods
        signals['close'] = self.bars['Close']
        signals['short_mavg'] = self.bars['Close'].rolling(window=self.short_window, min_periods=1, center=False).mean()
        signals['long_mavg'] = self.bars['Close'].rolling(window=self.long_window, min_periods=1, center=False).mean()
        
        slowstoc = self.slow_stochastic(self.bars['Low'], self.bars['High'], self.bars['Close'], period=16, smoothing=8)
        
        signals['k_slow'] = slowstoc[0]
        signals['d_slow'] = slowstoc[1]

        macd = self.moving_average_convergence(self.bars['Close'])
        
        signals = pd.concat([signals, macd], axis=1)
        
        #print(signals.to_string())
        
        # Create a 'signal' (invested or not invested) when the short moving average crosses the long
        # moving average, but only for the period greater than the shortest moving average window
        #signals['signal'][self.short_window:] = np.where(signals['short_mavg'][self.short_window:] 
        #    > signals['long_mavg'][self.short_window:], 1.0, 0.0)   
            
        # Create a 'signal' for Slow Stoc cross over <=20 && >=80
        if (len(signals) >= self.stoch_window):
            signals['signal_stoch_x'][self.stoch_window:] = np.where(
                (signals['k_slow'][self.stoch_window:] > signals['d_slow'][self.stoch_window:])
                & (signals['k_slow'][self.stoch_window:] <= 20)
                , 1.0, 0.0)
        else:
            signals['signal_stoch_x'] = 0.0
       
        if (len(signals) >= self.macd_window):
            signals['signal_macd_x'][self.macd_window:] = np.where(
                (signals['MACD'][self.macd_window:] > signals['emaSmooth'][self.macd_window:])
                , 1.0, 0.0)
        else:
            signals['signal_macd_x'] = 0.0
        
        #        result = pd.DataFrame({'MACD': macd, 'emaSmooth': emasmooth, 'divergence': macd-emasmooth})


        # Take the difference of the signals in order to generate actual trading orders
        signals['positions'] = signals['signal_stoch_x'].diff()
        signals.loc[signals.positions == -1.0, 'positions'] = 0.0

        #print(signals[['close', 'k_slow', 'd_slow', 'signal_stoch_x', 'divergence', 'signal_macd_x', 'positions']].head())
        #print(signals[['close', 'k_slow', 'd_slow', 'low_min', 'high_max', 'k_fast', 'd_fast']].to_string())
        #print(signals[['MACD', 'divergence']].head())
        
        return signals
        
    def simple_moving_average(self, prices, period=26):
        """
        :param df: pandas dataframe object
        :param period: periods for calculating SMA
        :return: a pandas series
        """
        sma = prices.rolling(window=period, min_periods=1, center=False).mean()
        #pd.rolling_mean(prices, period, min_periods=1)        
        return sma

    def fast_stochastic(self, lowp, highp, closep, period=16, smoothing=8):
        """ calculate slow stochastic
        Fast stochastic calculation
        %K = (Current Close - Lowest Low)/(Highest High - Lowest Low) * 100
        %D = 8-day SMA of %K
        """
        low_min = lowp.rolling(center=False, min_periods=1, window=period).min()
        high_max = highp.rolling(center=False, min_periods=1, window=period).max()
       
        #print("LOW_MIN")
        #print(low_min['20160511':'20160518'])
        #print("HIGH_P")
        #print(highp['20160511':'20160518'])
        #print("HIGH_MAX")
        #print(high_max['20160511':'20160518'])
        #print("CLOSEP")
        #print(closep['20160511':'20160518'])
        k_fast = 100 * (closep - low_min)/(high_max - low_min)
        d_fast = self.simple_moving_average(k_fast, smoothing)
        
        #print("K_FAST")
        #print(k_fast['20160511':'20160518'])
        #print("D_FAST")
        #print(d_fast['20160511':'20160518'])
        
        return k_fast, d_fast

    def slow_stochastic(self, lowp, highp, closep, period=16, smoothing=8):
        """ calculate slow stochastic
        Slow stochastic calculation
        %K = %D of fast stochastic
        %D = 8-day SMA of %K
        """
        k_fast, d_fast = self.fast_stochastic(lowp, highp, closep, period=period, smoothing=smoothing)

        # D in fast stochastic is K in slow stochastic
        k_slow = d_fast
        d_slow = self.simple_moving_average(k_slow, smoothing)
        return k_slow, d_slow
        
    def moving_average_convergence(self, prices, nslow=26, nfast=12, smoothing=9):
        emaslow = prices.ewm(min_periods=1, ignore_na=False, span=nslow, adjust=True).mean()
        emafast = prices.ewm(min_periods=1, ignore_na=False, span=nfast, adjust=True).mean()
        macd = emafast - emaslow
        emasmooth = macd.ewm(min_periods=1, ignore_na=False, span=smoothing, adjust=True).mean()
        result = pd.DataFrame({'MACD': macd, 'emaSmooth': emasmooth, 'divergence': macd-emasmooth})
        return result

def generate_scanner_chart(symbol, period, bars, signals):

    fig = plt.figure(figsize=(15, 20))
    fig.patch.set_facecolor('white')     # Set the outer colour to white
    fig.suptitle(symbol + " " + period, fontsize=12, color='grey')

    #ax1 = fig.add_subplot(211,  ylabel='Price in $')
    ax1 = plt.subplot2grid((9, 1), (0, 0), rowspan=4, ylabel='Price in $')

    #ax1.plot(signals.ix[signals.positions == 1.0].index, 
    #         signals.close[signals.positions == 1.0],
    #         '^', markersize=7, color='m')

    # Plot the "sell" trades against Stock
    #ax1.plot(signals.ix[signals.positions == -1.0].index, 
    #         signals.close[signals.positions == -1.0],
    #         'v', markersize=7, color='k')
    
    # Plot the closing price overlaid with the moving averages
    bars['Close'].plot(ax=ax1, color='r', lw=1.)
    signals[['short_mavg', 'long_mavg']].plot(ax=ax1, lw=1.)

    # Set the tick labels font
    for label in (ax1.get_xticklabels() + ax1.get_yticklabels()):
        label.set_fontname('Arial')
        label.set_fontsize(8)
        label.set_rotation(0)
    
    ax1.axes.xaxis.label.set_visible(False)
    ax1.grid(True)
    
    # Plot the Slow Stoc
    ax2 = plt.subplot2grid((9, 1), (4, 0), rowspan=2, ylabel='Slow Stoc')
    ax2.axes.xaxis.set_visible(False)
    signals[['k_slow', 'd_slow']].plot(ax=ax2, lw=1., grid=True, legend=None)
    
    ax2.fill_between(signals.index, 80, 100, facecolor='red', alpha=.2, interpolate=True)
    ax2.fill_between(signals.index, 0, 20, facecolor='red', alpha=.2, interpolate=True)
 
    # Plot the MACD
    ax3 = plt.subplot2grid((9, 1), (6, 0), rowspan=2, ylabel='MACD')
    ax3.axes.xaxis.set_visible(False)
    
    signals[['MACD', 'emaSmooth']].plot(x=signals.index, ax=ax3, lw=1., grid=True, legend=None)
    signals[['divergence']].plot(x=signals.index, ax=ax3, lw=0.1, grid=True, legend=None)
    
    ax3.fill_between(signals.index, signals['divergence'], 0,
                where=signals['divergence'] >= 0,
                facecolor='blue', alpha=.8, interpolate=True)
                
    ax3.fill_between(signals.index, signals['divergence'], 0,
                where=signals['divergence'] < 0,
                facecolor='red', alpha=.8, interpolate=True)

    # Plot the figure
    plt.tight_layout(h_pad=5)
    #plt.show()
    
    chartpath = "C:\\Temp\\charts\\" + 'macdStocX.' + symbol + "." + str(int(round(time.time() * 1000))) + '.png'
    #plt.savefig(chartpath, bbox_inches='tight')
    plt.savefig(chartpath)
    plt.clf()
    plt.close(fig)
    
    result = []
    result.append(chartpath)
    return result

def retrieve_bars_data_from_yahoo(symbol, datasrc, start, end):

    start_epoch = str(start.timestamp()).split(".")[0]
    end_epoch = str(end.timestamp()).split(".")[0]
    
    print("Retrieving data for [" + symbol + "] from " + str(start_epoch) + " to " + str(end_epoch))

    with requests.Session() as session:
        
        response = session.get('https://finance.yahoo.com/quote/2628.HK/history?p=2628.HK')
        print(session.cookies.get_dict())   

        regex = '"CrumbStore":{"crumb":"(.+?)"}'
        pattern = re.compile(regex)
        getcrumb = re.findall(pattern, str(response.content))
        print(str(getcrumb[0]))
        
        url = 'https://query1.finance.yahoo.com/v7/finance/download/'  + symbol + '?period1=' + start_epoch + '&period2=' + end_epoch + '&interval=1d&events=history&crumb=' + getcrumb[0]

        response = session.get(url)
        
        #print(response.content.decode("utf-8"))

        df = pd.read_csv(io.StringIO(response.content.decode("utf-8")), header=0, sep=',', index_col=0)
        
        # Converting the index as date
        df.index = pd.to_datetime(df.index)
        df = df[df.Open != "null"]
        
        df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']].apply(pd.to_numeric)
        
        print(df.Open.values)
        print(df.High.values)
        print(df.Low.values)
        print(df.Close.values)
        print(df.Volume.values)
        
        #print(df.to_string())
        return df

    
def retrieve_bars_data(symbol, datasrc, start, end):

    bars = None

    reciprocals = ['EUR=X', 'GBP=X', 'AUD=X', 'NZD=X']
    crosspairs = ['GBPJPY=X', 'EURJPY=X', 'EURGBP=X']
    
    #print(bars.to_string())
    
    #print("BARS HIGH Previous")
    #print(bars.head())
    
    #print("[" + symbol + "]")
    
    if ( any(st == symbol for st in reciprocals) ): 
        
        if (datasrc == "yahoo"):
            bars = web.DataReader(symbol, datasrc, start, end)
        elif (datasrc == "yahoo_direct"):
            bars = retrieve_bars_data_from_yahoo(symbol, datasrc, start, end)
        else :
            bars = retrieve_bars_data_from_yahoo(symbol, datasrc, start, end)
        
        bars['Open'] = np.reciprocal(bars['Open'])
        recHigh = np.reciprocal(bars['Low'])
        recLow = np.reciprocal(bars['High'])
        bars['High'] = recHigh
        bars['Low'] = recLow

        bars['Close'] = np.reciprocal(bars['Close'])
        bars['Adj Close'] = np.reciprocal(bars['Adj Close'])
    elif ( any(st == symbol for st in crosspairs) ):
        #print("In Crosspairs....")
        
        if (datasrc == "yahoo"):
            x1bars = web.DataReader(symbol[0:3] + '=X', datasrc, start, end)
            x2bars = web.DataReader(symbol[3:6] + '=X', datasrc, start, end)
        elif (datasrc == "yahoo_direct"):
            x1bars = retrieve_bars_data_from_yahoo(symbol[0:3] + '=X', datasrc, start, end)
            x2bars = retrieve_bars_data_from_yahoo(symbol[3:6] + '=X', datasrc, start, end)       
        else:
            x1bars = retrieve_bars_data_from_yahoo(symbol[0:3] + '=X', datasrc, start, end)
            x2bars = retrieve_bars_data_from_yahoo(symbol[3:6] + '=X', datasrc, start, end) 
        
        x1bars['Open'] = np.reciprocal(x1bars['Open'])
        recHigh = np.reciprocal(x1bars['Low'])
        recLow = np.reciprocal(x1bars['High'])
        x1bars['High'] = recHigh
        x1bars['Low'] = recLow

        x1bars['Close'] = np.reciprocal(x1bars['Close'])
        x1bars['Adj Close'] = np.reciprocal(x1bars['Adj Close'])
        
        bars = x1bars * x2bars
    
    else:
        if (datasrc == "yahoo"):
            bars = web.DataReader(symbol, datasrc, start, end)
        elif (datasrc == "yahoo_direct"):
            bars = retrieve_bars_data_from_yahoo(symbol, datasrc, start, end)
        else:
            bars = retrieve_bars_data_from_yahoo(symbol, datasrc, start, end)
        
    #print("BARS HIGH After")    
    #print(bars.head())   
        
    return bars  

def generate_scanner_result(symbol, period, datasrc='yahoo_direct'):
 
    end = datetime.today()
    start = end
    result = []
    
    # Determine correct start/end date
    if (period == "WEEKLY"):
        start = end - timedelta(days=(3*365))
    elif (period == "MONTHLY"):
        start = end - timedelta(days=(15*365))
    else:
        period = "DAILY"
        start = end - timedelta(days=(1*365))
    
    try:
        bars = retrieve_bars_data(symbol, datasrc, start, end)
    except:
        logging.error(" Error getting code: " + symbol)
        logging.error(traceback.format_exc())
        return result

    if (period == "WEEKLY"):
        bars = bars.asfreq('W-FRI', method='pad')
    elif (period == "MONTHLY"):
        bars = bars.asfreq('M', method='pad')

    # Create a Moving Average Cross Strategy instance with a short moving
    # average window of 100 days and a long window of 400 days
    mac = MacdStocCrossScanner(symbol, bars, short_window=14, long_window=27)
    signals = mac.generate_signals()
    
    #print(signals.to_string())
    
    if(len(signals.ix[signals.positions == 1.0].index) > 0):    
    
        then = signals.ix[signals.positions == 1.0].index[-1].date()
        now = datetime.now().date()
        difference =  (now - then) / timedelta(days=1)
        
        if (difference < 15):
            print(symbol + " " + period + ": [" + str(then) + ", " +  str(difference) + " days ago, chart: " + generate_scanner_chart(symbol, period, bars, signals)[0] + "]")
            result.append(symbol + " " + period + ": [" + str(then) + ", " +  str(difference) + " days ago")
            result.append(generate_scanner_chart(symbol, period, bars, signals)[0])
    
    #print("result: " + symbol + " - " + str(result))
    return result

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def send_to_tg_chatroom(passage): 

    chat_list = config.items("telegram-chat")
    bot_send_url = config.get("telegram","bot-send-url")
    
    for key, chat_id in chat_list:
        print("Chat to send: " + key + " => " + chat_id);

        result = urllib.request.urlopen(bot_send_url, urllib.parse.urlencode({ "parse_mode": "HTML", "chat_id": chat_id, "text": passage }).encode("utf-8")).read()
        
        print(result)
        
def generateScanner(type):

    passage = ""

    if (type == 'index'):
    
        with open('data/list_IndexList.json', encoding="utf-8") as data_file:    
            indexlists = json.load(data_file)  
            
        for index in indexlists:
        
            #break
            print ("\n============================================================================== " + index["code"] + " (" + index["label"] + ")")
            result_list = ""
            
            for stock in index["list"]:
                
                code = stock["code"].lstrip("0");

                if (is_number(code)):
                    code = code.rjust(4, '0') + ".HK"  

                #try:
                    #print (code + " (" + stock["label"] + ")")
                #except:
                    #print (code + " (" + str(stock["label"].encode("utf-8")) + ")")
                #    logging.error(traceback.format_exc())
                
                result = generate_scanner_result(code, "DAILY")

                if (len(result) > 0):
                    result_list = result_list + result[0] + EL
                    
            if (len(result_list) > 0):
                passage = passage + EL + index["code"] + " (" + index["label"] + ")" + DEL + result_list                
        
    elif (type == 'etf'):
    
        with open('data/list_ETFList.json', encoding="utf-8") as data_file:    
            etflists = json.load(data_file)              

        for etflist in etflists:
            #break
            print ("\n============================================================================== " + etflist["code"] + " (" + etflist["label"] + ")")
            result_list = ""
            
            for stock in etflist["list"]:
                
                code = stock["code"].lstrip("0");

                if (is_number(code)):
                    code = code.rjust(4, '0') + ".HK"  
                
                result = generate_scanner_result(code, "DAILY")
                
                if (len(result) > 0):
                    result_list = result_list + result[0] + EL
                    
            if (len(result_list) > 0):
                passage = passage + EL + etflist["code"] + " (" + etflist["label"] + ")" + DEL + result_list    
                
    elif (type == 'fx'):

        with open('data/list_FXList.json', encoding="utf-8") as data_file:    
            lists = json.load(data_file)              

        for list in lists:
            #break
            print ("\n============================================================================== " + list["code"] + " (" + list["label"] + ")")
            result_list = ""
            
            for stock in list["list"]:    
                code = stock["code"]
                result = generate_scanner_result(code, "DAILY")
                
                if (len(result) > 0):
                    result_list = result_list + result[0] + EL
                    
            if (len(result_list) > 0):
                passage = passage + EL + list["code"] + " (" + list["label"] + ")" + DEL + result_list 
    
    return passage
        
if __name__ == "__main__":

    #send_to_tg_chatroom(generateScanner('index'))
    #print(generate_scanner_result("2686668.HK", "DAILY"))
    #send_to_tg_chatroom(generateScanner('etf'))
    #send_to_tg_chatroom(generateScanner('fx'))    
    
    #generateScanner('etf')
    #generateScanner('fx')
    
    #send_to_tg_chatroom("Test")
    
    #generate_scanner_result("XAU=X", "DAILY")
    
  
    #generate_scanner_result("DEXJPUS", "DAILY", 'fred')
    generate_scanner_result("2800.HK", "DAILY")
    #generate_scanner_result("AUD=X", "DAILY")
    #generate_scanner_result("0012.HK", "DAILY")

