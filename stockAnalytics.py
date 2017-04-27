import pandas as pd
from pandas_datareader import data as web, wb
from stockstats import StockDataFrame as Sdf

data = web.get_data_yahoo('SPY')

stock_df = Sdf.retype(data)
data['rsi']=stock_df['rsi_14']

del data['close_-1_s']
del data['close_-1_d']
del data['rs_14']
del data['rsi_14']

print(data.tail())