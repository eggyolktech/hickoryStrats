#!/usr/bin/python

from hickory.util import config_loader
import requests
import locale
import json
import re
from datetime import datetime

EL = "\n"
DEL = "\n\n"
TAG_RE = re.compile(r'<[^>]+>')

config = config_loader.load()
APIKEY = config.get("alphavantage","apikey")

def remove_tags(text):
    return TAG_RE.sub('', text)

def get_fx_quote_message(fromCur, toCur):

    url = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=%s&to_currency=%s&apikey=%s" % (fromCur, toCur, APIKEY)

    print("URL: [" + url + "]")
    quote_result = {}

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    jsondata = r.text 
    data = json.loads(jsondata)
    print(data)
    
    if (not "Realtime Currency Exchange Rate" in data):
        return quote_result
        
    quote_obj = data["Realtime Currency Exchange Rate"]
    
    rate = quote_obj["5. Exchange Rate"]
    last = quote_obj["6. Last Refreshed"]
    timezone = quote_obj["7. Time Zone"]
    
    locale.setlocale( locale.LC_ALL, '' )
    passage = ""
    
    forex = u'\U0001F4B1'

    passage = forex + " <b>FX Rate</b>" + EL
    passage = passage + ("$1 <b>%s</b>" % fromCur) + (" = $%s" % rate) + " <b>" + toCur + "</b>" + EL
    passage = passage + "Last Updated: %s %s" % (last, timezone)
    passage = passage + EL 

    return passage

def main():

    print(get_fx_quote_message("GOG","USD"))
    print(get_fx_quote_message("BTC","USD"))
    print(get_fx_quote_message("XRP","USD"))
    print(get_fx_quote_message("LTC","USD"))
    #print(get_fx_quote_message("USD","JPY"))
    #print(get_fx_quote_message("USD","CNY"))
    #print(get_fx_quote_message("EUR","JPY"))


if __name__ == "__main__":
    main()                
              



