#!/usr/bin/python

import numpy as np
import pandas as pd
import quandl   # Necessary for obtaining financial data easily
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from pandas_datareader import data as web, wb
from hickory.core.hickory_base import Strategy, Portfolio

class MacdStocCrossStrategy(Strategy):
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
        
        # Create a 'signal' (invested or not invested) when the short moving average crosses the long
        # moving average, but only for the period greater than the shortest moving average window
        #signals['signal'][self.short_window:] = np.where(signals['short_mavg'][self.short_window:] 
        #    > signals['long_mavg'][self.short_window:], 1.0, 0.0)   

            
        # Create a 'signal' for Slow Stoc cross over <=20 && >=80
        signals['signal_stoch_x'][self.stoch_window:] = np.where(
            (signals['k_slow'][self.stoch_window:] > signals['d_slow'][self.stoch_window:])
            #& (signals['k_slow'][self.stoch_window:] <= 20)
            , 1.0, 0.0)  
       
        signals['signal_macd_x'][self.macd_window:] = np.where(
            (signals['MACD'][self.macd_window:] > signals['emaSmooth'][self.macd_window:])
            , 1.0, 0.0)  
        
        #        result = pd.DataFrame({'MACD': macd, 'emaSmooth': emasmooth, 'divergence': macd-emasmooth})

       
        signals['positions'] = signals['signal_stoch_x'].diff()
        signals.loc[signals.positions == -1.0, 'positions'] = 0.0
        
        # Take the difference of the signals in order to generate actual trading orders
        #signals['positions'] = signals['signal'].diff()   
        #signals['positions'] = signals['signal'].diff()   

        #print(signals.head())
        #print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx")
        print(signals[['divergence', 'k_slow', 'signal_stoch_x', 'signal_macd_x', 'positions']].to_string())
        
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
        #pd.rolling_min(lowp, period, min_periods=1)
        high_max = highp.rolling(center=False, min_periods=1, window=period).max()
        #pd.rolling_max(highp, period, min_periods=1)
        k_fast = 100 * (closep - low_min)/(high_max - low_min)
        #k_fast = k_fast.dropna()
        d_fast = self.simple_moving_average(k_fast, smoothing)
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
        #pd.ewma(prices, span=nslow, min_periods=1)
        emafast = prices.ewm(min_periods=1, ignore_na=False, span=nfast, adjust=True).mean()
        #pd.ewma(prices, span=nfast, min_periods=1)
        macd = emafast - emaslow
        emasmooth = macd.ewm(min_periods=1, ignore_na=False, span=smoothing, adjust=True).mean()
        #pd.ewma(macd, span=smoothing, min_periods=1)
        result = pd.DataFrame({'MACD': macd, 'emaSmooth': emasmooth, 'divergence': macd-emasmooth})
        return result
        
class MarketOnClosePortfolio(Portfolio):
    """Encapsulates the notion of a portfolio of positions based
    on a set of signals as provided by a Strategy.

    Requires:
    symbol - A stock symbol which forms the basis of the portfolio.
    bars - A DataFrame of bars for a symbol set.
    signals - A pandas DataFrame of signals (1, 0, -1) for each symbol.
    initial_capital - The amount in cash at the start of the portfolio."""

    def __init__(self, symbol, bars, signals, initial_capital=100000.0):
        self.symbol = symbol        
        self.bars = bars
        self.signals = signals
        self.initial_capital = float(initial_capital)
        self.positions = self.generate_positions()
        
    def generate_positions(self):
        positions = pd.DataFrame(index=self.signals.index).fillna(0.0)
        positions[self.symbol] = 100 * self.signals['positions']   # This strategy buys 100 shares
        return positions
                    
    def backtest_portfolio(self):
        pf = pd.DataFrame(index=self.bars.index)
        pf['holdings'] = self.positions.mul(self.bars['Close'], axis='index')
        pf['cash'] = self.initial_capital - pf['holdings'].cumsum()
        pf['total'] = pf['cash'] + self.positions[self.symbol].cumsum() * self.bars['Close']
        pf['returns'] = pf['total'].pct_change()
        #print("total len: " + str(len(pf['total'])))
        #print("total: " + pf['total'].to_string())
        
        return pf

        
def generate_strategy_result(symbol, period):
 
    end = datetime.date.today()
    start = end
    
    # Determine correct start/end date
    if (period == "WEEKLY"):
        start = end - datetime.timedelta(days=(3*365))
    elif (period == "MONTHLY"):
        start = end - datetime.timedelta(days=(15*365))
    else:
        period = "DAILY"
        start = end - datetime.timedelta(days=(1*365))
        
    bars = web.DataReader(symbol, "yahoo", start, end)
    
    if (period == "WEEKLY"):
        bars = bars.asfreq('W-FRI', method='pad')
    elif (period == "MONTHLY"):
        bars = bars.asfreq('M', method='pad')

    # Create a Moving Average Cross Strategy instance with a short moving
    # average window of 100 days and a long window of 400 days
    mac = MacdStocCrossStrategy(symbol, bars, short_window=14, long_window=27)
    signals = mac.generate_signals()

    # Create a portfolio of Stock Quote, with $100,000 initial capital
    portfolio = MarketOnClosePortfolio(symbol, bars, signals, initial_capital=100000.0)
    pf = portfolio.backtest_portfolio()
    
    fig = plt.figure(figsize=(15, 20))
    fig.patch.set_facecolor('white')     # Set the outer colour to white
    fig.suptitle(symbol + " " + period, fontsize=12, color='grey')

    #ax1 = fig.add_subplot(211,  ylabel='Price in $')
    ax1 = plt.subplot2grid((9, 1), (0, 0), rowspan=4, ylabel='Price in $')

    # Plot the "buy" trades against Stock
    #print(signals.ix[signals.positions == 1.0].index);
    #print(len(signals.ix[signals.positions == 1.0].index));
    #print(len(signals.short_mavg[signals.positions == 1.0]));
    
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
    
    #ax2.axhline(y = 80, color = "brown", lw = 0.5)
    #ax2.axhline(y = 20, color = "red", lw = 0.5)    
 
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

                # Plot the equity curve in dollars
    ax4 = plt.subplot2grid((9, 1), (8, 0), ylabel='Portfolio')

    # Plot the "buy" and "sell" trades against the equity curve
    
    if (len(pf.total[signals.positions == 1.0]) > 0):
        ax4.plot(pf.ix[signals.positions == 1.0].index, 
                 pf.total[signals.positions == 1.0],
                 '^', markersize=7, color='m')
    
    if (len(pf.total[signals.positions == -1.0]) > 0):    
        ax4.plot(pf.ix[signals.positions == -1.0].index, 
                 pf.total[signals.positions == -1.0],
                 'v', markersize=7, color='k')

             
    pf['total'].plot(ax=ax4, lw=1., grid=True, legend=None) 
    
    ax4.axes.xaxis.set_visible(False)

    # signal
    #ax3 = fig.add_subplot(413, ylabel='signal')
    #signals.signal.plot(ax=ax3)

    # signal
    #ax4 = fig.add_subplot(414, ylabel='signal')
    #signals.positions.plot(ax=ax4)

    # Plot the figure
    plt.tight_layout(h_pad=3)
    plt.show()
        
if __name__ == "__main__":

    #generate_strategy_result("0005.HK", "DAILY")
    generate_strategy_result("3988.HK", "WEEKLY")
    #generate_strategy_result("0005.HK", "MONTHLY")
