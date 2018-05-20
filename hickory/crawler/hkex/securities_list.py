#!/usr/bin/python

from hickory.util import stock_util
from hickory.db import stock_db
import os
import requests
import json

#from market_watch.db import 

def get_stock_json():

    stock_list = stock_db.get_stocks_list()
    master_list = []
    master_data_dict = {}
    master_data_dict["code"] = "ALL_HKEX"
    master_data_dict["label"] = "ALL Securities List"
    master_data_dict["list"] = stock_list

    master_list.append(master_data_dict)

    json_data = json.dumps(master_list)
    print(json_data)

    return json_data

def main():
    
    with open('../../data/list_HKEXList.json', 'w') as the_file:
        the_file.write(get_stock_json())

    #get_stock_json()

 
if __name__ == "__main__":
    main()                
              



