#!/usr/bin/python

import configparser
import os
import urllib.request
import urllib.parse
import sqlite3
import locale
import math
import datetime
from bs4 import BeautifulSoup
from hickory.util import config_loader
from hickory.crawler.aastocks import stock_quote, stock_info
from hickory.db import stock_sector_db

config = config_loader.load()
period = "ALL"

def generate():

    locale.setlocale(locale.LC_ALL, '')
    now = datetime.datetime.now()
    
    industries = stock_sector_db.get_hot_industries(period)

    html = """<html>
    <head>
        <meta charset="UTF-8">
        <title>Sector Heatmap</title>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
        <script>
            
            $(document).ready(function(){
            
                if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
                    $("div[class='col-sm-3']").toggleClass('col-sm-3 col-sm-6');
                }
            });
            
            function on(layer) {
                document.getElementById("overlay" + layer).style.display = "block";
            }

            function off(layer) {
                document.getElementById("overlay" + layer).style.display = "none";
            }

        </script>

        <style>

            .table-condensed, .row {
                font-size: 12.5px;
            }
            
            .overlay {
                position: fixed;
                display: none;
                width: 100%;
                height: 100%;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: rgba(0,0,0,0.5);
                z-index: 2;
                cursor: pointer;
            }

            #text{
                position: absolute;
                top: 50%;
                left: 50%;
                font-size: 50px;
                color: white;
                transform: translate(-50%,-50%);
                -ms-transform: translate(-50%,-50%);
            }
            
        </style>
    </head>
    <body>"""

    html = html + """<div class="container-fluid">
    <h3><img height="40" src="https://s.w.org/images/core/emoji/2.3/svg/1f413.svg"/>Goldenwokchaan Heatmap</h3>
    <p style="font-size: 11px">TO: 25m+ / MktCap: 2.5B+ / RS: """ + period + """<small> (Last updated: """ + now.strftime("%Y-%m-%d %H:%M") + """)</small></p>
        """
    num_rows = math.ceil(len(industries) / 4)

    for i in range(0, num_rows):
        html = html + """<div class="row">"""

        for j in range (0, 4):
            if (i*4 + j < len(industries)):
                # determine background color
                bgcolor = "lavender"
                if (j%2 == 1):
                    bgcolor = "lavenderblush"

                html = html + """<div class="col-sm-3" style="background-color:""" + bgcolor + """;">"""
                
                # if industry found
                if (i*4 + j < len(industries)):
                    stocks = stock_sector_db.get_hot_stocks_by_industry(industries[i*4 + j], period)
                    html = html + ("""<h6><b><a href="#" onclick="on(%s)">%s</a></b> (%s)</h6>""" % (industries[i*4 + j], industries[i*4 + j], len(stocks)))

                    # get industry stock list
                    stk_html = """<table class="table table-striped table-bordered table-hover table-condensed">"""
                    #print(len(stock_sector_db.get_hot_stocks_by_industry(industries[i*4 + j], period)))
                    for stock in stocks:
                        
                        if ("+" in stock["last_change_pct"]):
                            change_pct = "+" + "%.2f" % float(stock["last_change_pct"][1:-1]) + "%"
                            change_style = "color: green;"
                        elif ("-" in stock["last_change_pct"]):
                            change_pct = "-" + "%.2f" % float(stock["last_change_pct"][1:-1]) + "%"
                            change_style = "color: red;"
                        else:
                            change_pct = "%.2f" % float(stock["last_change_pct"][:-1]) + "%"
                            change_style = ""
                       
                        style_bg = "" 
                        if (float(stock["last_vol_ratio"]) > 5):
                            style_bg = "background-color: yellow;" 
                        elif (float(stock["last_vol_ratio"]) > 1.5):
                            style_bg = "background-color: lime;"

                        stk_html = stk_html + """<tr style='""" + style_bg + """'>
                                        <td><a href="/streaming.html?code=%s" target="_blank">%s</a></td><td>%s</td><td>%s</td><td style="%s">%s</td><td>%s</td>
                                        </tr>""" % (stock["code"], stock["code"], stock["name"], stock["last_close"], change_style, change_pct, "X" + "%.1f" % (stock["last_vol_ratio"]))
                    stk_html  = stk_html + """</table>"""
                    html = html + stk_html + """<div id="%s" class="overlay" onclick="off()"><div id="text">Overlay Text</div></div>""" % ("overlay" + industries[i*4 + j])

                html = html + """</div>"""

        html = html + """</div>"""
    
    html = html + """</div>"""
    html = html + """</body></html>"""

    print("Generating Report ...")
    #print(html)
    soup = BeautifulSoup(html, "html.parser")

    text_file = open("/var/www/eggyolk.tech/html/heatmap.html", "w")
    text_file.write(soup.prettify())
    text_file.close()

def main():
    
    generate()

if __name__ == "__main__":
    main() 
