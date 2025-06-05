# 获取价格并插入到表格中

import pandas as pd
from get_price import getLatestPriceByRedisCache
import chardet
from datetime import datetime

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']

def RepairACodeProc(ACode):
#     print(ACode)
    Result=ACode
    if(len(ACode)==9):
        return Result
    elif(len(ACode)==6):
        if(Result.find('0')==0 or Result.find('3')==0 or Result.find('127')==0 or Result.find('128')==0 or Result.find('123')==0 or Result.find('159')==0):
            Result = Result + '.SZ'
        elif(Result.find('4')==0 or Result.find('8')==0 or Result.find('9')==0):
            Result = Result + '.BJ'                        
        else:            
            Result = Result + '.SH'
    else:
        Result=Result.zfill(6) + '.SZ'         
    return Result

def update_close_prices(holdings_path):
    # 定义文件路径

    # 读取持仓文件
    holdings_df = pd.read_csv(holdings_path, encoding=detect_encoding(holdings_path))

    # 提取证券代码列
    security_code = holdings_df['证券代码'].tolist()

    # 调用 RepairACodeProc 方法处理每个证券代码
    repaired_security_codes = [RepairACodeProc(str(code)) for code in security_code]

    # 更新原表格的证券代码列
    holdings_df['代码'] = repaired_security_codes

    # 使用 holdings_df['代码'] 作为参数调用 getLatestPriceByRedisCache 函数
    code_line = holdings_df['代码'].tolist()

    # 修改此处，调用 getLatestPriceByRedisCache 函数
    price_df = getLatestPriceByRedisCache(code_line)

    # 打印获取的价格数据，用于调试
    print("获取的价格数据:", price_df)

    # 确保返回的 DataFrame 包含 'Code' 和 'PRECLOSE' 列（假设收盘价列名为 'PRECLOSE'）
    if 'Code' in price_df.columns and 'PRECLOSE' in price_df.columns:
        # 创建一个股票代码到最新收盘价的映射
        price_mapping = dict(zip(price_df['Code'], price_df['PRECLOSE']))

        # 检查映射中是否存在缺失的代码
        missing_codes = [code for code in code_line if code not in price_mapping]
        if missing_codes:
            print("以下代码在价格映射中缺失:", missing_codes)

        # 增加“收盘价”列，并赋值
        # 直接使用 holdings_df['代码'] 从价格映射中获取收盘价，特殊代码设为 1
        holdings_df['收盘价'] = [
            0 if code in ['204001.SH', '131810'] else price_mapping.get(code, None) 
            for code in holdings_df['代码']
        ]
    else:
        print("获取的价格数据缺少必要的列，请检查 get_price.py 函数的返回结果。")

    # 修改保存方法，使用 to_csv 保存到 CSV 文件
    holdings_df.to_csv(holdings_path, index=False)


if __name__ == "__main__":

    today = datetime.today().strftime("%Y%m%d")
    # today = '20250528'
    name = '尊享2号'
    code_name = '中泰XTP实盘_26节点'
    position_file = rf'c:\Users\Top\Desktop\{name}\{code_name}-PositionStatics-{today}.csv'
    update_close_prices(position_file)

    position_file = rf'c:\Users\Top\Desktop\{name}\{code_name}-PositionStatics-{today}.csv'
    update_close_prices(position_file)