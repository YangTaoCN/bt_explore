from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

# Create a Stratey
class SMAOp(bt.Strategy):
    params = (
        ('maperiod', 23),
    )

    REST_DAYS = 0
    LAST_SELL_DATE = None
    LAST_BUY = None
    AMOUNT_ON_HAND = 0
    DAYS_END = 30
    SELL_RETURN = 0.10

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.days_left = self.DAYS_END
        self.cost = 0
        self.sell_return = self.SELL_RETURN

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

        # Indicators for the plotting show
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
                                            subplot=True)
        bt.indicators.StochasticSlow(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])
        rsi = bt.indicators.RSI(self.datas[0])
        bt.indicators.SmoothedMovingAverage(rsi, period=10)
        bt.indicators.ATR(self.datas[0], plot=False)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        can_buy = True
        if self.AMOUNT_ON_HAND > 0:
            value = self.AMOUNT_ON_HAND * self.dataclose[0]
            retn = (value - self.cost) / self.cost
            if retn > 0.2:
                can_buy = False

        if self.LAST_SELL_DATE:
            rest_day = self.datas[0].datetime.date(0) - self.LAST_SELL_DATE
            if rest_day.days < self.DAYS_END / 3:
                return

        if can_buy:
            rest = cerebro.broker.getvalue() - self.AMOUNT_ON_HAND * self.dataclose[0]
            if rest > 0 and self.days_left > 0:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                daily_buy = rest / self.days_left
                self.days_left -= 1
                max_buy = daily_buy / self.dataclose[0]
                self.order = self.buy(None, max_buy)
                self.AMOUNT_ON_HAND += max_buy
                self.cost += daily_buy

        else:
            # SELL, SELL, SELL!!! (with all possible default parameters)
            self.log('SELL CREATE, %.2f' % self.dataclose[0])
            self.order = self.close()
            self.AMOUNT_ON_HAND = 0
            self.cost = 0
            self.days_left = self.DAYS_END
            self.LAST_SELL_DATE = self.datas[0].datetime.date(0)

THIS_STRA = SMAOp

def stock_analysis(stock, from_date, to_date):
    global cerebro
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(THIS_STRA)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    datapath = os.path.join('data/' + stock + '.csv')
    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=from_date,
        # Do not pass values before this date
        todate=to_date,
        # Do not pass values after this date
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(10000)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    cerebro.plot()

