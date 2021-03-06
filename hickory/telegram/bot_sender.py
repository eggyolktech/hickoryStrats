#!/usr/bin/python

import configparser
import os
import urllib.request
import urllib.parse
from hickory.util import config_loader

config = config_loader.load()

MAX_MSG_SIZE = 4096

def broadcast(passage): 

    chat_list = config.items("telegram-chat")
    bot_send_url = config.get("telegram","bot-send-url")
    
    for key, chat_id in chat_list:
        print("Chat to send: " + key + " => " + chat_id);
        
        messages = [passage[i:i+MAX_MSG_SIZE] for i in range(0, len(passage), MAX_MSG_SIZE)]

        for message in messages:

            result = urllib.request.urlopen(bot_send_url, urllib.parse.urlencode({ "parse_mode": "HTML", "chat_id": chat_id, "text": message }).encode("utf-8")).read()
            print(result)

def main():
    
    passage = "Test"

    # Send a message to a chat room (chat room ID retrieved from getUpdates)
    broadcast(passage)

if __name__ == "__main__":
    main() 
