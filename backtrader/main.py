# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import backtrader as bt

if __name__ == '__main__':
    # 初始化引擎
    cerebro = bt.Cerebro()

    # 默认初始资金为10K，设置初始资金：
    cerebro.broker.setcash(100000.0)
    print('初始市值: %.2f' % cerebro.broker.getvalue())

    # 回测启动运行
    result = cerebro.run()
    print('期末市值: %.2f' % cerebro.broker.getvalue())