#!/usr/bin/python

import configparser
import os
import urllib.request
import urllib.parse
import sqlite3
import locale
from hickory.util import config_loader
from hickory.crawler.aastocks import stock_quote, stock_info

config = config_loader.load()

MAX_MSG_SIZE = 4096

def generate():

    locale.setlocale(locale.LC_ALL, '')
    
    conn = sqlite3.connect("/app/marketWatchBot/market_watch/db/market_db.dat")

    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("select * from stock_tracker where region = 'HK' order by log_date desc")

    rows = c.fetchall()

    html = """<html>
    <head>
        <meta charset="UTF-8">
        <title>Stock Tracer</title>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
        <style>
            .table-condensed{
                font-size: 11px;
            }
        </style>
    </head>
    <body>
    <div class="container">
    <table class="table table-striped table-bordered table-hover table-condensed">"""

    html = html + """<tr>
        <th>Date</th><th>Record</th><th>Code</th><th>Industry</th><th>Name</th>
        <th>Price (Rec)</th><th>Price (Latest)</th><th>Avg Turnover</th><th>Turnover (Latest)</th>
        </tr>"""

    for row in rows:
        # get real time info from aastocks
        quote_obj = stock_quote.get_stock_quote(row["log_code"].strip())
        info_obj = stock_info.get_info(row["log_code"].strip())

        avg_turnover = row["log_desc"].split("$")[1]
        log_record = row["log_desc"].split("$")[0]

        #price_change = float(row["log_price"]) - float(quote_obj.get("Close"))
        price_change = float(quote_obj.get("Close")) - float(row["log_price"])
        price_change_percent = '{:.2%}'.format(price_change/float(row["log_price"]))
        price_change_txt = '{0:.2f}'.format(price_change) + "/" + price_change_percent
        
        if (price_change > 0):
            price_change_txt = "<font color='blue'>+" + price_change_txt.replace("/", "/+") + "</font>"
        elif (price_change < 0):
            price_change_txt = "<font color='red'>" + price_change_txt + "</font>"
        
        #print("stock code: " + row["log_code"])
        #print(str(quote_obj.get("CodeName")).split(" ")[-1:])
        #print("close: " + quote_obj.get("Close"))
        #print("formatted close: " + locale.currency(float(quote_obj.get("Close"))))
        html = html + "<tr><td>%s</td><td>%s</td><td><a href='/streaming.html?code=%s' target='_blank'>%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
row["log_date"], log_record + row["log_period"], row["log_code"], row["log_code"], info_obj["industry"], info_obj["stockName"], locale.currency(row["log_price"]), locale.currency(float(quote_obj.get("Close"))) + " (" + price_change_txt + ")", avg_turnover.upper(), quote_obj.get("Turnover"))

    html = html + """</div></table>
    </body></html>"""

    print("Generating Report...")
    print(html)

    text_file = open("/var/www/eggyolk.tech/html/tracker.html", "w")
    text_file.write(html)
    text_file.close()

def main():
    
    generate()

if __name__ == "__main__":
    main() 
