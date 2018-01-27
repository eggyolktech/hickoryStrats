#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import locale
import re
from hickory.db import stock_tech_db, stock_db
from hickory.util import stock_util
#from market_watch.db import market_db

EL = "\n"
DEL = "\n\n"
TAG_RE = re.compile(r'<[^>]+>')

DICT_CURRENCY = {'BTC':'BTC', 'EUR':'EUR', 'GBP':'GBP', 'AUD':'AUD', 'NZD':'NZD', 'JPY':'USDJPY', 'CAD':'USDCAD', 'HKD':'USDHKD', 'CHF':'USDCHF', 'SGD':'USDSGD', 'CNY':'USDCNY', 'CNYHKD':'CNYHKD', 'EURGBP':'EURGBP','HKDJPY':'HKDJPY', 'EURHKD':'EURHKD', 'GBPHKD':'GBPHKD', 'AUDHKD':'AUDHKD'}

def remove_tags(text):
    return TAG_RE.sub('', text)

def get_cn_stock_quote(code):
   
   quote_result = {}
   return quote_result

def get_fx_quote_message(code):

    code = DICT_CURRENCY[code.upper()]

    url = "https://finance.google.com/finance?q=CURRENCY%3A" + code

    #print("URL: [" + url + "]")

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    html = r.text 
    #print(html)
    soup = BeautifulSoup(html, "html.parser")
    
    divapp = soup.find("div", {"class": "appbar-snippet-primary"}) 
    div = soup.find("div", {"id": "currency_value"})

    if (not div):
        return "No FX Quote is found for " + code

    prices = div.find("span", {"class": "pr"})
    priceschange = div.find("span", {"class": "nwp"})

    time = div.find("div", {"class": "time"})

    if divapp:
        subject = divapp.text
    else:
        subject = code

    passage = "<b>" + subject.strip() + "</b>" + DEL
    passage = passage + prices.text.strip() + EL
    passage = passage + priceschange.text.strip().replace("-",
u'\U0001F53B').replace("+", u'\U0001F332') + EL
    passage = passage + "<i>" + time.text.strip() + "</i>"

    return passage

def get_us_stock_quote(code):

    url = "https://finance.google.com/finance?q=" + code

    #print("URL: [" + url + "]")
    quote_result = {}

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    html = r.text 
    #print(html)
    soup = BeautifulSoup(html, "html.parser")
    
    div = soup.find("div", {"class": "appbar"})

    if (not div):
        return quote_result

    appdiv = soup.find("div", {"class": "appbar-snippet-primary"})

    if (not appdiv):
        return quote_result

    name = appdiv.text
    price_panel = soup.find("div", {"id": "price-panel"})
    snap_table = soup.findAll("table", {"class": "snap-data"})[0]
    snap_rows = snap_table.findAll("tr")
    l_range = snap_rows[0].findAll("td")[1].text.strip()
    l_open = snap_rows[2].findAll("td")[1].text.strip()
    l_close = price_panel.find("span", {"class": "pr"}).text    

    if price_panel.find("span", {"class": "nwp"}): 
        last_update = price_panel.find("span", {"class": "nwp"}).text
    else:
        last_update = "N/A"
    #print(price_panel)
    change_info = price_panel.find("div", {"class": "id-price-change"}).text.strip()

    if change_info:
        change_val = change_info.split("(")[0].strip()
        change_pct = change_info.split("(")[1].replace(")","").strip()
    else:
        change_val = "0.00"
        change_pct = "0.00%"

    volume = snap_rows[3].findAll("td")[1].text.split("/")[0].replace(",","")
    if (len(snap_rows[3].findAll("td")[1].text.split("/")) > 1):
        mean_vol = snap_rows[3].findAll("td")[1].text.split("/")[1]
    else:
        mean_vol = None 

    if (mean_vol):
        f_vol_now = stock_util.rf(volume)
        f_vol_avg = stock_util.rf(mean_vol)
        quote_result["V2V"] = "%.2f" % (float(f_vol_now) / float(f_vol_avg))

    l_close = l_close.replace(",","").strip('\n')
 
    if ("0.00" in volume):
        turnover = "N/A"
        quote_result["Volume"] = volume.strip("\r\n")
        quote_result["Turnover"] = turnover
    elif (not stock_util.is_number(volume) and not stock_util.is_float(volume)): 
        turnover = "%.2f" % (float(volume[:-1]) * float(l_close)) + volume[-1]
        quote_result["Volume"] = volume.strip("\r\n")
        quote_result["Turnover"] = turnover
    else:
        turnover = "%.2f" % (float(volume) * float(l_close))
        quote_result["Volume"] = stock_util.rf2s(float(volume.strip("\r\n")))
        quote_result["Turnover"] = stock_util.rf2s(float(turnover))

    mkt_cap = snap_rows[4].findAll("td")[1].text.split("/")[0]
    pe_ratio = snap_rows[5].findAll("td")[1].text.split("/")[0]
    
    wk_low = snap_rows[1].findAll("td")[1].text.split("-")[0]
    wk_high = snap_rows[1].findAll("td")[1].text.split("-")[1]
    
    snap_table = soup.findAll("table", {"class": "snap-data"})[1]
    snap_rows = snap_table.findAll("tr")


    if (snap_rows[0].findAll("td")[1].text.strip() == "-"):
        dividend = None
        _yield = None
    elif (len(snap_rows[0].findAll("td")[1].text.split("/")) > 1):
        dividend = snap_rows[0].findAll("td")[1].text.split("/")[0]
        _yield = snap_rows[0].findAll("td")[1].text.split("/")[1]
    else:
        dividend = snap_rows[0].findAll("td")[1].text.split("/")[0]
        _yield = None 

    eps = snap_rows[1].findAll("td")[1].text.strip()
    shares = snap_rows[2].findAll("td")[1].text.strip()
    beta = snap_rows[3].findAll("td")[1].text.strip()
    inst_own = snap_rows[4].findAll("td")[1].text.strip()
    
    quote_result["CodeName"] = name.strip("\r\n")
    quote_result["Close"] = l_close.strip("\r\n")
    quote_result["ChangeVal"] = change_val.strip("\r\n")
    quote_result["ChangePercent"] = change_pct.strip("\r\n")

    if ("+" in quote_result["ChangeVal"]):
        quote_result["Direction"] = "UP"
    elif ("-" in quote_result["ChangeVal"]):
        quote_result["Direction"] = "DOWN"
    else:
        quote_result["Direction"] = "NONE"

    quote_result["MktCap"] = mkt_cap.strip("\r\n")

    quote_result["Range"] = l_range.strip("\r\n")

    quote_result["Open"] = l_open.strip("\r\n")

    quote_result["LastUpdate"] = last_update.replace("Real-time:","").strip("\r").strip("\n")

    quote_result["PE"] = pe_ratio.strip("\r\n")
    
    if (_yield):
        quote_result["Yield"] = _yield.strip("\r\n")
    if (dividend):
        quote_result["DivRatio"] = dividend.strip("\r\n")
    quote_result["EPS"] = eps.strip("\r\n")
    quote_result["Shares"] = shares.strip("\r\n")
    quote_result["Beta"] = beta.strip("\r\n")

    quote_result["52WeekLow"] = wk_low.strip()
    quote_result["52WeekHigh"] = wk_high.strip()
   
    return quote_result

def is_derivative(code):

    if (not code.isdigit()):
        return False
    else:
        code = code.lstrip("0")
        if (len(code) == 5 and code[0] in ('1','2','6')):
            return True

    return False

def get_stock_quote_derivative(code):

    quote_result = {}

    return quote_result

def get_stock_quote(code):

    if(is_derivative(code)):
        return get_stock_quote_derivative(code)

    quote_result = {}   
    return quote_result

def get_quote_message(code, region="HK", simpleMode=True):

    locale.setlocale( locale.LC_ALL, '' )
    passage = ""
    
    if (region == "HK"):
        quote_result = {}
        #quote_result = get_stock_quote(code)
    elif (region == "CN"):
        quote_result = {}
        #quote_result = get_cn_stock_quote(code)
    elif (region == "US"):
        print("Retrieveing code: " + code.upper())
        if (code.upper() in DICT_CURRENCY):
            return get_fx_quote_message(code)
        else:
            quote_result = get_us_stock_quote(code)
    
    #print(quote_result)
    if (not quote_result):
        passage = "Result not found for " + code
    else:    

        direction = u'\U0001F539'

        if (quote_result["Direction"] == "UP"):
            direction = u'\U0001F332'
        elif (quote_result["Direction"] == "DOWN"):
            direction = u'\U0001F53B'

        passage = "<b>" + quote_result["CodeName"] + "</b>" + EL
        passage = passage + direction + "" + "$%.3f" % float(quote_result["Close"]) + " (" + quote_result["ChangeVal"] + "/" + quote_result["ChangePercent"] + ")" + EL
        passage = passage + quote_result["Range"] + " (" + quote_result["Volume"] + "/" + quote_result["Turnover"] + ")"+ EL

        icon_v2v = ""
        if ("V2V" in quote_result):
            if (float(quote_result["V2V"]) > 1.5):
                 icon_v2v = u'\U0001F414'
            elif (float(quote_result["V2V"]) > 1.0):
                 icon_v2v = u'\U0001F424'
            passage = passage + icon_v2v +  "V/AV " + "x" + quote_result["V2V"] + EL
      
        if ("52WeekHigh" in quote_result and "52WeekLow" in quote_result): 
            if (not quote_result["52WeekHigh"] == "N/A" and not quote_result["52WeekLow"] == "N/A"):
                if (float(quote_result["Close"])) > float(quote_result["52WeekHigh"].replace(",","")):
                    passage = passage + u'\U0001F525' + "<i>52 Week High</i>" + EL
                elif (float(quote_result["Close"])) < float(quote_result["52WeekLow"].replace(",","")):
                    passage = passage + u'\U00002744' + "<i>52 Week Low</i>" + EL 
        
        if (simpleMode):
            return passage     

        passage = passage + EL 

        attrs = ["Open", "PrevClose", "LotSize", "PE", "Yield", "DivRatio", "EPS", "MktCap", "NAV", "52WeekHigh", "52WeekLow", "Exchange", "ImpVol", "RemainingDays", "Strike", "CallPrice", "SpotVsCall", "EffGearing", "Delta", "Premium", "OutStanding", "Moneyness", "Underlying", "Shares", "Beta", "LastUpdate"] 

        for attr in attrs:
            passage = passage + constructPassageAttributes(attr, quote_result)

    return passage

def constructPassageAttributes(key, qDict):

    if (key in qDict):
        return key + ": " + qDict[key] + EL
    else:
        return ""

def main():

    quote = get_us_stock_quote('AAPL')
    quote = get_us_stock_quote('DFT')
    #quote = get_us_stock_quote('SWFT')
    #quote = get_cn_stock_quote('000001')
    #quote = get_stock_quote('3054')
    for key, value in quote.items():
        print(key, ":", value)
    #print(get_stock_quote_derivative('28497'))
    #print(get_stock_quote_derivative('60002'))
    #print(get_quote_message('28497', "HK", False))
    #print(get_quote_message('60002', "HK", False))
    #print(get_quote_message('000001',"CN", False))
 
    #print(get_quote_message('DFT',"US", False))
    print(get_quote_message('GOOG',"US", False))
    print(get_quote_message('MSFT',"US", False))
    #print(get_quote_message('SNAP',"US", True))
    #print(get_quote_message('AMZN',"US", False))

    print(get_quote_message('btc',"US", False))
    print(get_fx_quote_message("BTC"))
    print(get_fx_quote_message("EUR"))
    print(get_fx_quote_message("jpy"))


if __name__ == "__main__":
    main()                
              



