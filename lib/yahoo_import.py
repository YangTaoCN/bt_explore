import platform
import yfinance as yf
import datetime
import os.path, time


class YahooImport:
    def __init__(self):
        pass

    def pull_day(self, stock):
        file_name = "../data/" + stock + ".csv"
        today = datetime.datetime.today().date()
        print(today)
        dt = yf.download(stock, start="2000-01-01", end=today)
        dt.to_csv(r"../data/" + stock + ".csv")

yh = YahooImport()
yh.pull_day('000333.sz')




