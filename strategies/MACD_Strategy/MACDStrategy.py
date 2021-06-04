# MACD策略的信号线交叉交易法

# 原理
# 指数移动平均线(下称EMA), 指数移动平均线是移动平均线的一种，能够根据数据点的新旧程度分配不同的权重，
# 其更重视近期价格，减轻对往期价格的权重 ，而普通的移动平均线在所有价格上权重都一致，这是二者最大的不同。
# EMA线还有周期上的不同，长期投资者通常选择50、100、200周期来追踪数月、甚至是年的价格趋势。
# 而12天和26天的时间周期短，则广受短期投资者欢迎。而大部分股票软件的MACD线也是按照12天EMA和26天EMA进行计算的。

# 蓝线上穿信号线（橙色）的时候看涨，蓝线下穿信号线（橙色）的时候看跌。

# 蓝线是MACD线，它通过将一个价格短期EMA和价格长期EMA相减得到，在大部分股票软件中是EMA(12) - EMA(26).
# 信号线是MACD线的EMA，周期一般为9.

# 公式如下：

# MACD=价格EMA(12) - 价格EMA(26).
# 信号线=MACD的EMA(9)
# 图中一个个的方块，是由MACD线 - 信号线得到的差值，正值在上，负值在下。

# 买入：
# 当 MACD线在前一天的值 < 信号线前一天的值
# 且 当天MACD线的值 > 当天信号线的值 时
# 说明发生了金叉，此时看涨，第二天买入。

# 卖出：若已盈利10%，则卖出；若已亏损10%，则卖出。


import datetime
import os.path
import sys
import backtrader as bt
from backtrader.indicators import EMA


class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    @staticmethod
    def percent(today, yesterday):
        return float(today - yesterday) / today

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.volume = self.datas[0].volume

        self.order = None
        self.buyprice = None
        self.buycomm = None

        me1 = EMA(self.data, period=12)
        me2 = EMA(self.data, period=26)
        self.macd = me1 - me2
        self.signal = EMA(self.macd, period=9)

        bt.indicators.MACDHisto(self.data)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.bar_executed_close = self.dataclose[0]
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])
        if self.order:
            return

        if not self.position:
            condition1 = self.macd[-1] - self.signal[-1]
            condition2 = self.macd[0] - self.signal[0]
            if condition1 < 0 and condition2 > 0:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()

        else:
            condition = (self.dataclose[0] - self.bar_executed_close) / self.dataclose[0]
            if condition > 0.1 or condition < -0.1:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    cerebro.addstrategy(TestStrategy)

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '603186.csv')

    # 加载数据到模型中
    # data = bt.feeds.GenericCSVData(
    #     dataname=datapath,
    #     fromdate=datetime.datetime(2010, 1, 1),
    #     todate=datetime.datetime(2020, 4, 12),
    #     dtformat='%Y%m%d',
    #     datetime=2,
    #     open=3,
    #     high=4,
    #     low=5,
    #     close=6,
    #     volume=10,
    #     reverse=True
    # )
    
    # 加载数据到模型中
    data = bt.feeds.YahooFinanceCSVData(
        dataname='AAPL.csv',
        fromdate=datetime.datetime(2020, 5, 8),
        todate=datetime.datetime(2021, 5, 8)
    )
    cerebro.adddata(data)

    cerebro.broker.setcash(10000)

    cerebro.addsizer(bt.sizers.FixedSize, stake=100)

    cerebro.broker.setcommission(commission=0.005)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()