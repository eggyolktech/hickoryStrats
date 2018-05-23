#!/usr/bin/python

import resource

def set_max_mem(max_mem):

    #set resource limit
    rsrc = resource.RLIMIT_DATA
    soft, hard = resource.getrlimit(rsrc)
    print('Soft limit start as :' + str(soft))

    resource.setrlimit(rsrc, (max_mem * 1024, hard))
    soft, hard = resource.getrlimit(rsrc)

    print('Soft limit start as :' + str(soft))

def main():
    set_max_mem(100)    

if __name__ == "__main__":
    main() 
