import numpy as np
import pandas as pd
import quandl   # Necessary for obtaining financial data easily
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from pandas_datareader import data as web, wb
from hickoryBase import Strategy, Portfolio

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

    def generate_signals(self):
        """Returns the DataFrame of symbols containing the signals
        to go long, short or hold (1, -1 or 0)."""
        signals = pd.DataFrame(index=self.bars.index)
        signals['signal'] = 0.0

        # Create the set of short and long simple moving averages over the 
        # respective periods
        signals['short_mavg'] = pd.rolling_mean(self.bars['Close'], self.short_window, min_periods=1)
        signals['long_mavg'] = pd.rolling_mean(self.bars['Close'], self.long_window, min_periods=1)
        
        #sma = self.simple_moving_average(self.bars['Close'])
        
        #print(str(len(signals['long_mavg'])))
        #print(str(len(sma)))
        
        slowstoc = self.slow_stochastic(self.bars['Low'], self.bars['High'], self.bars['Close'], period=16, smoothing=8)
        #print(str(len(signals['long_mavg'])))
        #print(str(len(slowstoc[0])))
        #print(str(len(slowstoc[1])))
        
        signals['k_slow'] = slowstoc[0]
        signals['d_slow'] = slowstoc[1]

        macd = self.moving_average_convergence(self.bars['Close'])
        
        signals = pd.concat([signals, macd], axis=1)
        
        print(signals.tail())
        
        #        result = pd.DataFrame({'MACD': emafast-emaslow, 'emaSlw': emaslow, 'emaFst': emafast})
        
        # Create a 'signal' (invested or not invested) when the short moving average crosses the long
        # moving average, but only for the period greater than the shortest moving average window
        signals['signal'][self.short_window:] = np.where(signals['short_mavg'][self.short_window:] 
            > signals['long_mavg'][self.short_window:], 1.0, 0.0)   

        # Take the difference of the signals in order to generate actual trading orders
        signals['positions'] = signals['signal'].diff()   

        return signals
        
    def simple_moving_average(self, prices, period=26):
        """
        :param df: pandas dataframe object
        :param period: periods for calculating SMA
        :return: a pandas series
        """
        sma = pd.rolling_mean(prices, period, min_periods=1)
        return sma

    def fast_stochastic(self, lowp, highp, closep, period=14, smoothing=3):
        """ calculate slow stochastic
        Fast stochastic calculation
        %K = (Current Close - Lowest Low)/(Highest High - Lowest Low) * 100
        %D = 3-day SMA of %K
        """
        low_min = pd.rolling_min(lowp, period, min_periods=1)
        high_max = pd.rolling_max(highp, period, min_periods=1)
        k_fast = 100 * (closep - low_min)/(high_max - low_min)
        #k_fast = k_fast.dropna()
        d_fast = self.simple_moving_average(k_fast, smoothing)
        return k_fast, d_fast

    def slow_stochastic(self, lowp, highp, closep, period=14, smoothing=3):
        """ calculate slow stochastic
        Slow stochastic calculation
        %K = %D of fast stochastic
        %D = 3-day SMA of %K
        """
        k_fast, d_fast = self.fast_stochastic(lowp, highp, closep, period=period, smoothing=smoothing)

        # D in fast stochastic is K in slow stochastic
        k_slow = d_fast
        d_slow = self.simple_moving_average(k_slow, smoothing)
        return k_slow, d_slow
        
    def moving_average_convergence(self, prices, nslow=26, nfast=12, smoothing=9):
        emaslow = pd.ewma(prices, span=nslow, min_periods=1)
        emafast = pd.ewma(prices, span=nfast, min_periods=1)
        macd = emafast - emaslow
        emasmooth = pd.ewma(macd, span=smoothing, min_periods=1)
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
        return pf
        
if __name__ == "__main__":

    # Obtain daily bars of AAPL from Yahoo Finance for the period
    # 1st Jan 1990 to 1st Jan 2002 - This is an example from ZipLine
    symbol = 'AAPL'
    bars = web.DataReader(symbol, "yahoo", datetime.datetime(2016, 5, 1), datetime.datetime(2017, 4, 30))

    # Create a Moving Average Cross Strategy instance with a short moving
    # average window of 100 days and a long window of 400 days
    mac = MacdStocCrossStrategy(symbol, bars, short_window=14, long_window=27)
    signals = mac.generate_signals()

    # Create a portfolio of AAPL, with $100,000 initial capital
    portfolio = MarketOnClosePortfolio(symbol, bars, signals, initial_capital=100000.0)
    pf = portfolio.backtest_portfolio()

    print(bars.tail())
    
    fig = plt.figure(figsize=(15, 20))
    #fig = plt.figure()
    fig.patch.set_facecolor('white')     # Set the outer colour to white

    #ax1 = fig.add_subplot(211,  ylabel='Price in $')
    ax1 = plt.subplot2grid((9, 1), (0, 0), rowspan=4, ylabel='Price in $')

    # Plot the AAPL closing price overlaid with the moving averages
    bars['Close'].plot(ax=ax1, color='r', lw=1.)
    signals[['short_mavg', 'long_mavg']].plot(ax=ax1, lw=1.)

    # Plot the "buy" trades against AAPL
    ax1.plot(signals.ix[signals.positions == 1.0].index, 
             signals.short_mavg[signals.positions == 1.0],
             '^', markersize=10, color='m')

    # Plot the "sell" trades against AAPL
    ax1.plot(signals.ix[signals.positions == -1.0].index, 
             signals.short_mavg[signals.positions == -1.0],
             'v', markersize=10, color='k')
    
    #myFmt = mdates.DateFormatter('%Y-%m')
    #ax1.xaxis.set_major_formatter(myFmt)    
    
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
    ax2.axhline(y = 80, color = "brown", lw = 0.5)
    ax2.axhline(y = 20, color = "red", lw = 0.5)    
 
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
    
    #signals[['divergence']].plot(x=signals.index.values, ax=ax3, kind='bar', lw=1.) 
    #signals[['MACD']].plot(x=signals.index.values, ax=ax3, lw=1.)  
    #signals[['emaSmooth']].plot(x=signals.index.values, ax=ax3, lw=1.)  
    
    #print(signals[['divergence']].tail())
    #print(signals[['MACD']].tail())
    #print(signals[['emaSmooth']].tail())
     

    # Plot the equity curve in dollars
    ax4 = plt.subplot2grid((9, 1), (8, 0), ylabel='Portfolio')
    pf['total'].plot(ax=ax4, lw=1., grid=True, legend=None)

    # Plot the "buy" and "sell" trades against the equity curve
    ax4.plot(pf.ix[signals.positions == 1.0].index, 
             pf.total[signals.positions == 1.0],
             '^', markersize=10, color='m')
    ax4.plot(pf.ix[signals.positions == -1.0].index, 
             pf.total[signals.positions == -1.0],
             'v', markersize=10, color='k')
             
    ax4.axes.xaxis.set_visible(False)

    # signal
    #ax3 = fig.add_subplot(413, ylabel='signal')
    #signals.signal.plot(ax=ax3)

    # signal
    #ax4 = fig.add_subplot(414, ylabel='signal')
    #signals.positions.plot(ax=ax4)

    # Plot the figure
    #fig.show(block=True)
    plt.tight_layout(h_pad=3)
    plt.show()