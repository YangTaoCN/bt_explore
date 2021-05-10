import sys
sys.path.append(r'../lib')
sys.path.append(r'../bin')
import csv
import yahoo_import
import stock_analysis

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
    list = read_csv('../stocks/list.csv')
    for stock in list:
        yahoo_import.pull_day(stock)

    for stock in list:
        stock_analysis.stock_analysis(stock)


index()