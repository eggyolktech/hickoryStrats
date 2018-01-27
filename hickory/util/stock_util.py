#!/usr/bin/python

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

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

def rfNum(number, numDecimal):
    
    if (number and is_number(number)):
        return ("%." + str(numDecimal) + "f") % number
    else:
        return number

def rf2s(number):
    if (number and (is_number(number) or is_float(number))):

        length = len(str(number).split(".")[0])
        #print(length)
        if (length >= 10):
            return ("%.2f" % (number/1000000000) + "B")
        elif (length >= 7):
            return ("%.2f" % (number/1000000) + "M")
        elif (length >= 4):
            return ("%.2f" % (number/1000) + "K")
        elif (length >= 2):
            return ("%.2f" % (number))
        else:
            return str(number)
    else:
        return number

def rfDeltaPercentage(new, old):
    change = (float(new) - float(old))/float(old) * 100
    change_val = ("%.2f" % change) + "%"
    return rfDirection(change_val)

def rfDirection(change):

    if ("-" in change):
        change = change.replace("-", u'\U0001F53B')
    else:
        change = u'\U0001F332' + change
        
    return change


def main():
    print(rf("12,333B"))


    print(rf2s(1233313131093918.231))
    print(rf2s(123))
    print(rf2s(13918.231))
    print(rf2s(12393918.231))
    print(rf2s(193918.231))

if __name__ == "__main__":
    main()

