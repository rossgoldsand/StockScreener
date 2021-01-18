import json
import yfinance as yf
import pandas as pd
import math
from datetime import date, timedelta


CUR_DATE = date.today().__str__()
YESTERDAY = (date.today() - timedelta(1)).__str__()
total_period = 70
pullback_period = 10
recovery_period = 5
START_DATE = (date.today() - timedelta(total_period)).__str__() 
RECOVERY_DATE = (date.today() - timedelta(recovery_period)).__str__()
PULLBACK_DATE = (date.today() - timedelta(pullback_period)).__str__()
YEAR_START_DATE = (date.today() - timedelta(365)).__str__()

#Higher difficulty factor means harder to accept a stock - shorter time frame requires smaller difficulty factor
DIFFICULTY_FACTOR = 3

def main():

    print(date.today())
    l = get_tickers()
    l = [x for x in l if '.' not in x]
    viable_stocks = []

    count = 0

    try:
        for ticker in l:
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

def lows(data, factor=DIFFICULTY_FACTOR):
    #Get the list of lows
    lows = list(data['Low'])
    lows = cleanup_list(lows)
    count = 0 #counts the number of times a single day's low was not greater than the previous days
    num_entries = len(lows)
    if num_entries == 0:
        return False
    max_count = num_entries / factor

    for i in range(1,len(lows)):
        if lows[i] <= lows[i-1]:
            count += 1
    
    if count <= max_count:
        return True
    else:
        return False

def highs(data, factor=DIFFICULTY_FACTOR):
    highs = list(data['High'])
    highs = cleanup_list(highs)

    num_entries = len(highs)
    if num_entries == 0:
        return False
    max_count = num_entries / factor
    count = 0
    
    for i in range(1,len(highs)):
        if highs[i] <= highs[i-1]:
            count += 1

    mean = sum(highs) / len(highs)

    if count <= max_count and mean > 1 and mean < 300:
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
    data = stock.history(period='1d', start=START_DATE, end=PULLBACK_DATE)
    #print(data)

    #Check if the lows requirement is satisfied
    lows_bool = lows(data)

    #Check if the highs requirement is satisfied
    highs_bool = highs(data)
    #Check if the volume requirement is satisfied
    vol_bool = volume(data)

    if highs_bool == True and lows_bool == True and vol_bool == True:
        if check_max(stock) == True: 
            data = stock.history(period='1d', start=PULLBACK_DATE, end=RECOVERY_DATE)
            if lows(data) == False and highs(data) == False:
                data = stock.history(period='1d', start=RECOVERY_DATE, end=CUR_DATE)
                if lows(data) == True and highs(data) == True:
                    print("good!!!")
                    return True
    else:
        return False

def check_max(stock):
    data = stock.history(period='1d', start=YEAR_START_DATE, end=CUR_DATE)
    highs = list(data['High'])
    highs = cleanup_list(highs)

    m = max(highs)
    cur = highs[-1]
    max_cur = m*0.83 #0.83 means 83% of the high. Feel free to change this as needed.

    print(f'high: {m} cur: {cur} max_cur = {max_cur}')

    if cur < max_cur:
        return True
    else:
        return False

        
def get_stock(ticker):
    s = yf.Ticker(ticker)
    new_ticker = ticker + '.TO'
    sto = yf.Ticker(new_ticker)

    try:
        sto.info
        return sto
    except Exception:
        try:
            s.info
            return s
        except Exception:
            print("Ticker not found")
            return None




def get_tickers():
    with open('tsx_stocks.json') as f:
        data = json.load(f)
        data = data['results']
    f.close()

    l = []

    for line in data:
        l.append(line['symbol'])
    return l




main()

