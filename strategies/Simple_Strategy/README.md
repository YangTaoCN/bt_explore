# 懒人炒股心经要点

- 早盘大跌可加仓，程序认为如果早上10点，股票的价格是开盘9：30的98%，跌了2%，那么程序就认为早盘大跌，准备加仓。
- 早盘大涨要减仓，程序认为如果早上10点，股票的价格是开盘9：30的102%，涨了2%，那么程序就认为早盘大涨，准备减仓。
- 下午大涨要减仓，程序认为如果下午3点，股票的价格是2点的102%，涨了2%，那么程序就认为下午大涨，准备减仓。
- 下午大跌次日买，程序认为如果下午4点收盘，股票的价格是2点的98%，跌了2%，那么程序就认为下午大跌，将于次日早上开盘9：30买入。

# 数据
arkk.json, qqq.json, spy.json
simply_strategy.py，198行

# 运行
在Terminal中，输入: python3 simply_strategy.py


# 不同的波动率
simply_strategy.py，199行中的2代表上涨2%就是大涨，下跌2%就是大跌