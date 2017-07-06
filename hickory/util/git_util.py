#!/usr/bin/python

import os
from git import Repo
from hickory.util import config_loader

config = config_loader.load()

def commit(repo_dir, file_list):
    
    print("git commit started at repo: " + repo_dir)
    print(file_list)
    repo = Repo(repo_dir)
    commit_message = 'Daily watch list files upload'
    repo.index.add(file_list)
    repo.index.commit(commit_message)
    print("git commit completed")

def commitAll(repo_dir):
    
    print("git commit started at repo: " + repo_dir)
    #print(file_list)
    repo = Repo(repo_dir)
    git = repo.git
    commit_message = 'Daily watch list files commit all'
    git.add("-A")
    git.commit("-am", commit_message)
    print("git commit all completed")


def push_remote(repo_dir):

    print("git push to remote at repo: " + repo_dir)
    repo = Repo(repo_dir)
    origin = repo.remote('origin')
    origin.push()
    print("git push completed")
def main():

    file_list = [
        'web/js/dailyWatcherETFListData.js',
        'web/js/dailyWatcherIndexListData.js'
    ]
   
    repo_dir = "/app/hickoryStratsWatcher/"
    #commit(repo_dir, file_list)
    commitAll(repo_dir)
    push_remote(repo_dir)

if __name__ == "__main__":
    main() 
