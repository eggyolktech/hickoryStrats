#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import locale
import json
import re
from hickory.util import stock_util
from hickory.db import stock_us_db
from datetime import datetime

import concurrent.futures
import random
import traceback
import logging

EL = "\n"
DEL = "\n\n"
TAG_RE = re.compile(r'<[^>]+>')

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def remove_tags(text):
    return TAG_RE.sub('', text)

# Create a function called "chunks" with two arguments, l and n:
def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]    

def download_data(symbol):

    surl = "https://api.iextrading.com/1.0/stock/%s/chart/5y" % symbol
        
    r = requests.get(surl, headers=headers)
    jsondata = r.text 
 
    filename = '/usr/local/data/iextrading/chart_%s.json' % symbol
    with open(filename, 'w') as file:
        file.write(jsondata) # use `json.loads` to do the reverse
        print("%s downloaded" % filename)
    
def download_list():

    url = "https://api.iextrading.com/1.0/ref-data/symbols"

    print("URL: [" + url + "]")
    quote_result = {}

    r = requests.get(url, headers=headers)
    jsondata = r.text 
    data = json.loads(jsondata)
    
    enabledList = [d for d in data if d['isEnabled'] == True and "#" not in d['symbol']]
    enabledList = enabledList[:10]
    print("Enabled List Length: %s" % len(enabledList))

    return enabledList
   
def main():

    stocks = download_list()
    num_workers = 5 

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        
        # Start the load operations and mark each future with its URL
        future_to_manage = {executor.submit(download_data, stock['symbol']): stock for stock in stocks}
        
        for future in concurrent.futures.as_completed(future_to_manage):
            code = future_to_manage[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (code, exc))
                logging.error(" Error retrieving code: " + code)
                logging.error(traceback.format_exc())
            else:
                if (data == False):
                    print('%r result is %s' % (code, data))    

if __name__ == "__main__":
    main()                
              



