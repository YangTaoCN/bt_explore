import platform
import yfinance as yf
import datetime

class YahooImport:
    def __init__(self):
        pass

    def pull_day(self, stock):
        today = datetime.datetime.today().isoformat()
        data = yf.Ticker(stock)
        info = data.info
        investment = info['shortName']
        print('Investment: ' + investment)

        df = data.history(period='1h', start='2000-1-1', end=today[:10])
        # price_last = df['Close'].iloc[-1]
        # price_yest = df['Close'].iloc[-2]
        print(df)

yh = YahooImport()
yh.pull_day('000333.sz')




