import csv
import numpy as np
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
    print(list)

index()