import csv
from datetime import datetime, timedelta
import tool
import deal_reverse
import handle_sql
import pandas as pd
from get_price import getLatestPriceByRedisCache

def RepairACodeProc(ACode):
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

def deal_part_data(today, account_file, position_file, deal_local_path, product_name, account_name, other_name, fund_account, reverse):
    print(today, account_file, position_file, deal_local_path, product_name, account_name, other_name, fund_account[0])

    # 从position获取 市值 盈亏 资产占比
    holdings_df = pd.read_csv(position_file, encoding=tool.detect_encoding(position_file))
    security_code = holdings_df['证券代码'].tolist()
    repaired_security_codes = [RepairACodeProc(str(code)) for code in security_code]
    holdings_df['代码'] = repaired_security_codes
    code_line = holdings_df['代码'].tolist()
    price_df = getLatestPriceByRedisCache(code_line)
    price_mapping = dict(zip(price_df['Code'], price_df['NOW']))
    missing_codes = [code for code in code_line if code not in price_mapping]
    if missing_codes:
        print("以下代码在价格映射中缺失:", missing_codes)

    # 增加“收盘价”列，并赋值直接使用 holdings_df['代码'] 从价格映射中获取收盘价，特殊代码设为 0
    reverse = ["204001.SH", "131810.SZ", "888880.BJ"] # TODO 读取配置文件

    holdings_df['收盘价'] = [
        0 if code in reverse else price_mapping.get(code, None) 
        for code in holdings_df['代码']
    ]

    market_value = (holdings_df['收盘价'] * holdings_df['当前拥股']).sum()
    daily_profit_sum = holdings_df['盈亏'].sum()
    # 将资产占比列的百分比字符串转换为小数
    holdings_df['资产占比'] = holdings_df['资产占比'].str.rstrip('%').astype(float) / 100
    position_ratio_sum = holdings_df['资产占比'].sum()
    print('position', market_value, daily_profit_sum, position_ratio_sum)

    # 从account获取 总资产 可用金额
    acconut_df = pd.read_csv(account_file, encoding=tool.detect_encoding(account_file))
    total_assets = acconut_df['总资产'].sum()
    cash = acconut_df['可用金额'].sum()
    print('account', total_assets, cash)

    # 上一个交易日 TODO
    yesterday_date_str = handle_sql.select_nearest_date('Daily_Account', today)
    yesterday_date_str = '20250604'

    # 读取历史数据
    account_history = handle_sql.select_account(yesterday_date_str, fund_account[0])
    print('账号历史数据', account_history)
    if isinstance(account_history, (list, tuple)) and len(account_history) == 0:
        yesterday_total_assets = 0
    else:
        yesterday_total_assets = float(account_history[0]['totalassets'])
    print('上一个交易日总资产', yesterday_total_assets)
    # print('账号历史数据', account_history[0])

    # 获取申购赎回金额
    subscription_redemption = handle_sql.select_SGSH_amount(today, fund_account[0])
    if isinstance(subscription_redemption, (list, tuple)) and len(subscription_redemption) == 0:
        sgsh_amount = 0
    else:
        sgsh_amount = float(subscription_redemption[0]['amount'])
        print('申购赎回', subscription_redemption[0])
    print('申购赎回金额：', sgsh_amount)

    # 计算日涨跌幅
    print(today, account_name, subscription_redemption) 
    if sgsh_amount >= 0:  # 申购
        daily_return = (total_assets - abs(sgsh_amount) - yesterday_total_assets) / (yesterday_total_assets + sgsh_amount) if yesterday_total_assets + sgsh_amount != 0 else 0
    else:
        daily_return = (total_assets + abs(sgsh_amount) - yesterday_total_assets) / yesterday_total_assets if yesterday_total_assets != 0 else 0

    # # 计算月起始日期
    # last_month_date = current_date - timedelta(days=30)
    # # 计算年起始日期
    # last_year_date = current_date - timedelta(days=365)

    # TODO 计算月涨跌幅和月盈亏
    # monthly_return, monthly_profit = calculate_period_stats(historical_data, last_month_date, current_date,
    #                                                         today, account_name, daily_return)
    monthly_return = None
    monthly_profit = None
    if monthly_return is None:
        monthly_return = daily_return
        monthly_profit = daily_profit_sum

    # # 计算年涨跌幅和年盈亏
    # annual_return, annual_profit = calculate_period_stats(historical_data, last_year_date, current_date,
    #                                                       today, account_name, daily_return)
    annual_return = None
    if annual_return is None:
        annual_return = daily_return
        annual_profit = daily_profit_sum

    # # 计算总涨跌幅和总盈亏
    # total_return, total_profit = calculate_period_stats(historical_data, datetime.min, current_date,
    #                                                      today, account_name, daily_return)
    total_return = None
    if total_return is None:
        total_return = daily_return
        total_profit = daily_profit_sum
    

    # 计算国债逆回购
    reverse = deal_reverse.process_csv_file(deal_local_path)
    print('国债逆回购', deal_local_path, reverse)

    # 生成结果
    result = {
        'Date': today,
        'FundAccount': fund_account[0],
        'Account': other_name,
        'Product': product_name,
        'TotalAssets': round(total_assets, 2),
        'MarketValue': round(market_value, 2),
        'Cash': round(cash + reverse, 2),
        'Position': f"{position_ratio_sum * 100:.2f}%",
        'DailyPer': f"{daily_return * 100:.2f}%",
        'Daily': round(daily_profit_sum, 2),
        'MonthlyPer': f"{monthly_return * 100:.2f}%",
        'Monthly': round(monthly_profit, 2),
        'YearlyPer': f"{annual_return * 100:.2f}%",
        'Yearly': round(annual_profit, 2),
        'TotalPer': f"{total_return * 100:.2f}%",
        'Total': round(total_profit, 2)
    }
    print("结果----", result)
    handle_sql.add_account(result)


def main():
    today = datetime.today().strftime("%Y%m%d")
    # today = '20250603'
    config_data = tool.read_ftp_config()

    if config_data:
        reverse = config_data['reverse']
        for product in config_data['products']:
            product_name = product['name']
            for code in product['codes']:
                name = code['name']
                other_name = code['other_name']
                fund_account = code['fund_account']

                position_local_path = product['local_path']+f'{name}-PositionStatics-{today}.csv'
                account_local_path = product['local_path']+f'{name}-Account-{today}.csv'
                deal_local_path = product['local_path']+f'{name}-Deal-{today}.csv'

                deal_part_data(today, account_local_path, position_local_path, deal_local_path, product_name, name, other_name, fund_account, reverse)


if __name__ == "__main__":
    main()