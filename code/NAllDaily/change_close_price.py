# 获取价格并插入到表格中

import pandas as pd
from get_price import getLatestPriceByRedisCache
from datetime import datetime
import tool


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

def update_close_prices(holdings_path, reverse):

    # 读取持仓文件
    holdings_df = pd.read_csv(holdings_path, encoding=tool.detect_encoding(holdings_path))

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


    # 创建一个股票代码到最新收盘价的映射
    price_mapping = dict(zip(price_df['Code'], price_df['NOW']))

    # 检查映射中是否存在缺失的代码
    missing_codes = [code for code in code_line if code not in price_mapping]
    if missing_codes:
        print("以下代码在价格映射中缺失:", missing_codes)

    # 增加“收盘价”列，并赋值
    # 直接使用 holdings_df['代码'] 从价格映射中获取收盘价，特殊代码设为 0
    holdings_df['收盘价'] = [
        0 if code in reverse else price_mapping.get(code, None) 
        for code in holdings_df['代码']
    ]

    MarketValue = (holdings_df['收盘价'] * holdings_df['当前拥股']).sum()
    DailyProfit = holdings_df['盈亏'].sum()
    Position = holdings_df['资产占比'].sum()

    print(MarketValue, DailyProfit, Position)

    # 修改保存方法，使用 to_csv 保存到 CSV 文件
    # holdings_df.to_csv(holdings_path, index=False)

def get_data_acconut(holdings_path):

    acconut_df = pd.read_csv(holdings_path, encoding=tool.detect_encoding(holdings_path))
    TotalAssets = acconut_df['总资产'].sum()
    Cash = acconut_df['可用金额'].sum()
    print(TotalAssets, Cash)


def main():
    today = datetime.today().strftime("%Y%m%d")
    # today = '20250527'
    position_file = rf'c:\Users\Top\Desktop\山西证券\山西证券-PositionStatics-{today}.csv'
    reverse = ["204001.SH", "131810.SZ", "888880.BJ"]
    update_close_prices(position_file, reverse)
    position_file = rf'c:\Users\Top\Desktop\山西证券\山西证券-Account-{today}.csv'
    get_data_acconut(position_file)

    # config_data = tool.read_ftp_config()
    # if config_data:
    #     reverse = config_data['reverse']
    #     for product in config_data['products']:
    #         for code in product['codes']:
    #             name = code['name']
    #             position_local_path = product['local_path']+f'{name}-PositionStatics-{today}.csv'
    #             print(name, position_local_path)
    #             update_close_prices(position_local_path, reverse)


if __name__ == "__main__":
    main()
    