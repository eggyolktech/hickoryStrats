#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import locale

#from market_watch.db import market_db

EL = "\n"
DEL = "\n\n"

def get_stock_quote(code):

    url = "http://www.aastocks.com/en/mobile/Quote.aspx?symbol=" + code

    #print("URL: [" + url + "]")
    
    quote_result = {}

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    html = r.text 
    #print(html)
    soup = BeautifulSoup(html, "html.parser")
    
    # if no close result, just return empty
    if (not soup.find("td", {"class": "quote_table_header_text"}).text.strip()):
        return quote_result

    quote_result["CodeName"] = (soup.find("td", {"class": "quote_table_header_text"}).text)

    div_last = soup.find("div", {"class": "text_last"})

    quote_result["Close"] = (div_last.text.strip().replace(",",""))

    td_last = soup.find("td", {"class": "cell_last"})
    quote_result["ChangeVal"] = (td_last.find_all("div")[2].find_all("span")[0].text)
    quote_result["ChangePercent"] = (td_last.find_all("div")[2].find_all("span")[1].text)

    if ("+" in quote_result["ChangeVal"]):
        quote_result["Direction"] = "UP"
    elif ("-" in quote_result["ChangeVal"]):
        quote_result["Direction"] = "DOWN"
    else:
        quote_result["Direction"] = "NONE"

    quote_result["Range"] = (td_last.find_all("div")[3].text.strip())

    td_last = soup.find("td", {"class": "cell_last_height"})
    quote_result["Open"] = (td_last.find_all("td")[2].find("span").text)
    quote_result["PrevClose"] = (td_last.find_all("td")[3].find("span").text)
    quote_result["Volume"] = (td_last.find_all("td")[4].find("span").text)
    #quote_result[""] = (soup.find("div", {"class": "ctl00_cphContent_pQuoteDetail"}))
    div_content = soup.find("div", {"id": "ctl00_cphContent_pQuoteDetail"})
    quote_result["LastUpdate"] = (div_content.find("font", {"class": "font12_white"}).text)

    rows = div_content.find_all("table")[0].find_all("tr", recursive=False)

    quote_result["LotSize"] = (rows[2].find_all("td")[0].find("span").text)
    quote_result["Turnover"] = (rows[2].find_all("td")[1].find("span").text)
    quote_result["PE"] = (rows[3].find_all("td")[0].find("span").text)
    quote_result["Yield"] = (rows[3].find_all("td")[1].find("span").text)
    quote_result["DivRatio"] = (rows[4].find_all("td")[0].find("span").text)
    quote_result["EPS"] = (rows[4].find_all("td")[1].find("span").text)
    quote_result["MktCap"] = (rows[5].find_all("td")[0].find("span").text)
    quote_result["NAV"] = (rows[5].find_all("td")[1].find("span").text)

    div52 = soup.find("div", {"id": "ctl00_cphContent_p52Week"})
    
    if (div52.find("span").text == "N/A"):
        quote_result["52WeekLow"] = "N/A"
        quote_result["52WeekHigh"] = "N/A"
    else:
        quote_result["52WeekLow"] = (div52.find("span").text.split("-")[0].strip())
        quote_result["52WeekHigh"] = (div52.find("span").text.split("-")[1].strip())
    
    return quote_result

def get_quote_message(code, simpleMode=True):

    locale.setlocale( locale.LC_ALL, '' )
    passage = ""
    
    quote_result = get_stock_quote(code)
    print(quote_result)
    if (not quote_result):
        passage = "Result not found for " + code
    else:    

        direction = u'\U0001F539'

        if (quote_result["Direction"] == "UP"):
            direction = u'\U0001F53C'
        elif (quote_result["Direction"] == "DOWN"):
            direction = u'\U0001F53D'

        passage = "<b>" + quote_result["CodeName"] + "</b>" + EL
        passage = passage + direction + " " + locale.currency(float(quote_result["Close"])) + " (" + quote_result["ChangeVal"] + "/" + quote_result["ChangePercent"] + ")" + EL
        passage = passage + quote_result["Range"] + " (" + quote_result["Volume"] + "/" + quote_result["Turnover"] + ")"+ EL
        if (float(quote_result["Close"])) > float(quote_result["52WeekHigh"]):
            passage = passage + u'\U0001F525' + "<i>52 Week High</i>" + EL
        elif (float(quote_result["Close"])) < float(quote_result["52WeekLow"]):
            passage = passage + u'\U00002744' + "<i>52 Week Low</i>" + EL 

        if (simpleMode):
            return passage     

        passage = passage + EL + "Open: " + quote_result["Open"] + EL
        passage = passage + "PrevClose: " + quote_result["PrevClose"] + EL
        passage = passage + "Lot Size: " + quote_result["LotSize"] + EL
        passage = passage + "PE: " + quote_result["PE"] + EL
        passage = passage + "Yield: " + quote_result["Yield"] + EL
        passage = passage + "DivRatio: " + quote_result["DivRatio"] + EL
        passage = passage + "EPS: " + quote_result["EPS"] + EL
        passage = passage + "MktCap: " + quote_result["MktCap"] + EL
        passage = passage + "NAV: " + quote_result["NAV"] + EL
        passage = passage + "52 Week High: " + quote_result["52WeekHigh"] + EL
        passage = passage + "52 Week Low: " + quote_result["52WeekLow"] + EL
        passage = passage + "<i>LastUpdate: " + quote_result["LastUpdate"] + "</i>" + EL

    return passage

def main():

    quote = get_stock_quote('3054')
    
    for key, value in quote.items():
        print(key, ":", value)
 
if __name__ == "__main__":
    main()                
              



