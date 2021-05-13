from datetime import datetime
import sys
sys.path.append('lib')
import csv
import yahoo_import
sys.path.append('bin')
import stock_analysis

import datetime  # For datetime objects

# read stock list
def read_csv(file):
    list_csv = open(file, "r")
    list_csv.readline()
    reader = csv.reader(list_csv)
    response = []
    for item in reader:
        response = response + item
    return response
# download data

# run every stratagy on every stock, keep the best stratagy, position, trade in stock status file

def index():
    list = read_csv('stocks/list.csv')
    from_date = datetime.datetime(2019, 1, 1)
    to_date = datetime.datetime.now()
    #to_date = datetime.datetime(2018, 1, 1)
    print(from_date)
    print(to_date)
    for stock in list:
        yahoo_import.pull_day(stock)

    for stock in list:
        stock_analysis.stock_analysis(stock, from_date, to_date)


index()