# 获取价格并插入到表格中

import pandas as pd
from get_price import getLatestPriceByRedisCache
import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']

def update_close_prices():
    # 定义文件路径
    holdings_path = r'c:\Users\Top\Desktop\FuYing\code\DailyAsset\持仓\昨日持仓.csv'

    # 读取持仓文件
    holdings_df = pd.read_csv(holdings_path, encoding=detect_encoding(holdings_path))

    # 提取股票代码列
    code_line = holdings_df['股票代码'].tolist()

    # 修改此处，调用 getLatestPriceByRedisCache 函数                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
    price_df = getLatestPriceByRedisCache(code_line)

    # 确保返回的 DataFrame 包含 'Code' 和 'PRECLOSE' 列（假设收盘价列名为 'PRECLOSE'）
    if 'Code' in price_df.columns and 'PRECLOSE' in price_df.columns:
        # 创建一个股票代码到最新收盘价的映射
        price_mapping = dict(zip(price_df['Code'], price_df['PRECLOSE']))

        # 更新今日持仓表格中的 close 列
        holdings_df['Close'] = holdings_df['股票代码'].map(price_mapping)
    else:
        print("获取的价格数据缺少必要的列，请检查 get_price.py 函数的返回结果。")

    # 修改保存方法，使用 to_csv 保存到 CSV 文件
    holdings_df.to_csv(holdings_path, index=False)


if __name__ == "__main__":
    update_close_prices()