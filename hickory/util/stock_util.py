#!/usr/bin/python

def rf(text):

    if (text == "-"):
        return None
    else:
        text = text.replace(",","")
        if ("B" in text):
            return float(text.replace("B","")) * 1000000000
        elif ("M" in text):
            return float(text.replace("M","")) * 1000000
        elif ("K" in text):
            return float(text.replace("K","")) * 1000
        return text

def main():
    print(rf("12,333B"))

if __name__ == "__main__":
    main()

