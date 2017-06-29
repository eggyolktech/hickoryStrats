#!/usr/bin/python

import os
from git import Repo
from hickory.util import config_loader

config = config_loader.load()

def push(repo_dir, file_list):
    
    print("git push started at repo: " + repo_dir)
    print(file_list)
    repo = Repo(repo_dir)
    commit_message = 'Daily watch list files upload'
    repo.index.add(file_list)
    repo.index.commit(commit_message)
    origin = repo.remote('origin')
    origin.push()
    print("git push completed")

def main():

    file_list = [
        'web/js/dailyWatcherETFListData.js',
        'web/js/dailyWatcherIndexListData.js'
    ]
   
    push("/app/hickoryStratsWatcher/", file_list)    

if __name__ == "__main__":
    main() 
