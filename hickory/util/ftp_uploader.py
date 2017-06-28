#!/usr/bin/python

import ftplib
import os
from hickory.util import config_loader

config = config_loader.load()

def upload_to_scicube(filepath):

    s = config.get("scicube", "ftp-server");
    l = config.get("scicube", "ftp-login");
    p = config.get("scicube", "ftp-pass");
    d = config.get("scicube", "default-dir");

    session = ftplib.FTP(s, l, p)
    
    file = open(filepath,'rb')                  # file to send
    filename = os.path.basename(filepath).replace(".tmp", "")
    
    #print(session.pwd())
    print(d)    
    session.cwd(d)
    session.storbinary('STOR ' + filename, file) # send the file
    file.close()                                 # close file and FTP
    print("Filename: " + d + filename + " successfully uploaded!")
    session.quit()

def main():
    
    upload_to_scicube("/tmp/test")    

if __name__ == "__main__":
    main() 
