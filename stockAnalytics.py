import pandas as pd
from pandas_datareader import data as web, wb
from stockstats import StockDataFrame as Sdf

data = web.get_data_yahoo('SPY')

stock_df = Sdf.retype(data)
data['rsi']=stock_df['rsi_16']
del data['close_-1_s']
del data['close_-1_d']
del data['rs_16']
del data['rsi_16']

# volume delta against previous day
stock_df['volume_delta']

# KDJ, default to 9 days
#stock_df['kdjk_16']
#stock_df['kdjd_8']
#stock_df['kdjk_16_xu_kdjd_8']
stock_df[['kdjk', 'kdjd', 'kdjj']]
#stock_df['kdjj']

# three days KDJK cross up 3 days KDJD
#stock_df['kdj_3_xu_kdjd_3']




print(data[-50:])

#print(stock_df.get('kdj_3_xu_kdjd_3').tail())
