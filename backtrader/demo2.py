import backtrader as bt
import datetime
import pandas as pd
import backtrader.feeds as btfeeds

# 取得Data Feed对象
def get_tushare_online_daily_data():
    """将A股票日线数据返回BT Data
    """
    # 参数部分
    stock_id = "000001.SZ"
    start = "20190101"
    end = "20191231"
    dt_start = datetime.datetime.strptime(start, "%Y%m%d")
    dt_end = datetime.datetime.strptime(end, "%Y%m%d")
    TOKEN = 'abcd1234'

    ts.set_token(TOKEN)
    pro = ts.pro_api()

    try:
        # 加载数据
        df = pro.daily(ts_code=stock_id, start_date=start, end_date='end')
        df.sort_values(by=["trade_date"], ascending=True,
                       inplace=True)    # 按日期先后排序
        df.reset_index(inplace=True, drop=True)

        # 开始数据清洗：
        # 按日期先后排序
        df.sort_values(by=["trade_date"], ascending=True, inplace=True)
        # 将日期列，设置成index
        df.index = pd.to_datetime(df.trade_date, format='%Y%m%d')
        # 增加一列openinterest
        df['openinterest'] = 0.00
        # 取出特定的列
        df = df[['open', 'high', 'low', 'close', 'vol', 'openinterest']]
        # 列名修改成指定的
        df.rename(columns={"vol": "volume"}, inplace=True)

        data = bt.feeds.PandasData(dataname=df, fromdate=dt_start, todate=dt_end)

        return data
    except Exception as err:
        print("下载{0}完毕失败！")
        print("失败原因 = " + str(err))
