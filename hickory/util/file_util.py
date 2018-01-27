#!/usr/bin/python

import resource
import pickle

ROOT = "/app/hickoryStrats/hickory/data/"

def save_obj(obj, name ):
    with open(ROOT + 'obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open(ROOT + 'obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

def main():

    print("Test")

if __name__ == "__main__":
    main() 
