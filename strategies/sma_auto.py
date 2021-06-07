from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt


# Create a Stratey
class SMAAuto(bt.Strategy):
    params = (
        ('long', 5),
        ('short', 10),
        ('stand', 89)
    )

    REST_DAYS = 0
    LAST_SELL_DATE = None
    AMOUNT_ON_HAND = 0
    DAYS_END = 10
    TARGET = 0.05

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
        self.last_buy = None
        self.days_left = self.DAYS_END
        self.cost = 0
        self.can_buy = False
        self.finish_buy = False
        self.target = self.TARGET
        self.can_sell = False

        # Add a MovingAverageSimple indicator
        self.sma_long = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.long)
        self.sma_short = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.short)
        self.sma_stand = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.stand)
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

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market

        # Not yet ... we MIGHT BUY if ...

        if self.sma_long[-2] < self.sma_long[-1] < self.sma_long[0] and\
                self.sma_stand > self.dataclose[0]:
            self.can_buy = True
        if self.can_buy:
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
                self.finish_buy = True

        if self.AMOUNT_ON_HAND > 0:
            value = self.AMOUNT_ON_HAND * self.dataclose[0]
            retn = (value - self.cost) / self.cost
            if retn > self.target:
                self.can_sell = True

        if self.can_sell and self.sma_short[-2] > self.sma_short[-1] > self.sma_short[0] and \
                self.AMOUNT_ON_HAND > 0 and self.finish_buy:
            # SELL, SELL, SELL!!! (with all possible default parameters)
            self.order = self.close()
            self.AMOUNT_ON_HAND = 0
            self.cost = 0
            self.days_left = self.DAYS_END
            self.LAST_SELL_DATE = self.datas[0].datetime.date(0)
            self.can_buy = False
            self.finish_buy = False
            self.can_sell = False


def stock_analysis(stock, from_date, to_date):
    this_stra = SMAAuto
    global cerebro
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(this_stra)

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
    cerebro.broker.setcash(100000)

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
