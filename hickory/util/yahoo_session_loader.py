#!/usr/bin/python

import os
import configparser
import requests
import re

class YahooFinanceLoader:
    __single = None
    __cookies = None
    __crumb = None

    def __init__(self):
        if YahooFinanceLoader.__single:
            raise YahooFinanceLoader.__single
        YahooFinanceLoader.__single = self

        while True:

            with requests.Session() as session:

                response = session.get('https://finance.yahoo.com/quote/2628.HK/history?p=2628.HK')
                cookies = session.cookies

                regex = '"CrumbStore":{"crumb":"(.+?)"}'
                pattern = re.compile(regex)
                getcrumb = re.findall(pattern, str(response.content))
                crumb = getcrumb[0].replace('\\u002F','/')

                YahooFinanceLoader.__cookies = cookies
                YahooFinanceLoader.__crumb = crumb

                print("Session Cookies: [" + str(cookies.get_dict()) + "], Crumb: [" + getcrumb[0] + " ==> " + crumb + "]")

            if (not crumb == None and "/" not in crumb):
                break

    def getSingleton():
        if not YahooFinanceLoader.__single:
            YahooFinanceLoader.__single = YahooFinanceLoader()
        return YahooFinanceLoader.__single

    def getCookies(self):
        return YahooFinanceLoader.__cookies

    def getCrumb(self):
        return YahooFinanceLoader.__crumb

def load():

    singleton = YahooFinanceLoader.getSingleton()
    
    return singleton

def main():

    session = load()
    print(session.getCookies())
    print(session.getCrumb())
   
if __name__ == "__main__":
    main()        
        

