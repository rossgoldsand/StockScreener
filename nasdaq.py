import json
import yfinance as yf
import pandas as pd
import math

CUR_DATE = '2020-12-27'
START_DATE = '2020-12-16'

#Higher difficulty factor means harder to accept a stock
DIFFICULTY_FACTOR = 5

def main(): 

    l = get_tickers()
    l = [x for x in l if '.' not in x]
    l = [x for x in l if '^' not in x]
    viable_stocks = []
    count = 0
    try:
        for ticker in l[1834:]:
            """
            if count > 3:
                break
            count += 1
            """
            print(ticker)
            s = get_stock(ticker)
            if s == None:
                continue

            if analyze_stock(s) == True:
                viable_stocks.append(ticker)
    except KeyboardInterrupt:
        pass
    print(viable_stocks)
        

def cleanup_list(l):
    return [x for x in l if math.isnan(x)==False]

def lows(data):
    #Get the list of lows
    lows = list(data['Low'])
    lows = cleanup_list(lows)
    count = 0 #counts the number of times a single day's low was not greater than the previous days
    num_entries = len(lows)
    if num_entries == 0:
        return False
    max_count = num_entries / DIFFICULTY_FACTOR

    for i in range(1,len(lows)):
        if lows[i] <= lows[i-1]:
            count += 1
    
    if count <= max_count:
        #print("passed lows")
        return True
    else:
        return False

def highs(data):
    highs = list(data['High'])
    highs = cleanup_list(highs)

    num_entries = len(highs)
    if num_entries == 0:
        return False
    max_count = num_entries / DIFFICULTY_FACTOR
    count = 0
    
    for i in range(1,len(highs)):
        if highs[i] <= highs[i-1]:
            count += 1

    mean = sum(highs) / len(highs)

    if count <= max_count and mean > 1:
        #print("passed highs")
        return True
    else:
        return False

def volume(data):
    vols = list(data['Volume'])
    vols = cleanup_list(vols)
    #print(vols)
    if len(vols) == 0:
        return False

    mean = sum(vols) / len(vols)
    yesterday = vols[-1]
    if mean > 50000 and yesterday > mean:
        #print(f"mean: {mean} passed vol")
        return True
    else:
        #print(mean)
        return False


def analyze_stock(stock):
    #Get the stocks data
    data = stock.history(period='1d', start=START_DATE, end=CUR_DATE)
    #print(data)

    #Check if the lows requirement is satisfied
    lows_bool = lows(data)

    #Check if the highs requirement is satisfied
    highs_bool = highs(data)
    #Check if the volume requirement is satisfied
    vol_bool = volume(data)

    if highs_bool == True and lows_bool == True and vol_bool == True:
        print("good!!!")
        return True
    else:
        return False
    
        
def get_stock(ticker):
    s = yf.Ticker(ticker)

    try:
        s.info
        return s
    except Exception:
        print("Ticker not found")
        return None




def get_tickers():
    df = pd.read_csv('companylist.csv')
    data = df['Symbol']   

    l = []
    for x in data:
        l.append(x)
    return l
    
main()

