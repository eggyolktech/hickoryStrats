#!/usr/bin/python

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#%matplotlib inline

#By Rami Nasser

sym = 'SPY'
df_close = pd.DataFrame()
df_temp = pd.read_json('https://api.iextrading.com/1.0/stock/'+sym+'/chart/5y')
df_temp.set_index('date',inplace=True)
df_close = df_temp['close']

loc = df_close.index.get_loc('2015-08-17')
list_2015 = df_close[loc:loc+60].tolist()

loc = df_close.index.get_loc('2015-12-29')
list_2016 = df_close[loc:loc+60].tolist()

loc = df_close.index.get_loc('2018-01-26')
list_2018 = df_close[loc:loc+60].tolist()

plot_data = pd.DataFrame()

plot_data['2015'] = pd.Series(list_2015)/list_2015[0]*100
plot_data['2016'] = pd.Series(list_2016)/list_2016[0]*100
plot_data['2018'] = pd.Series(list_2018 + [258.05])/list_2018[0]*100

plt.style.use('fivethirtyeight')

title = 'How does the current S&P 500 correction compare to the Aug 2015 and Jan 2016 corrections?'
ax = plot_data.plot(figsize=(12,10), title=title)
ax.set_xlabel('The number of trading days since the beginning of the correction')
ax.set_ylabel('Normalized S&P 500')
plt.axhline(y=90, color='silver', linestyle='-.')
plt.savefig('Correction.png', bbox_inches='tight')
plt.show()
