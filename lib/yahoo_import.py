import platform
import yfinance as yf
import datetime
import os.path, time



def pull_day(stock):
    file_name = "../data/" + stock + ".csv"
    today = datetime.datetime.today().date()
    dt = yf.download(stock, start="2000-01-01", end=today)
    dt.to_csv(r"../data/" + stock + ".csv")






