from datetime import datetime
import tool
import deal_reverse
import handle_sql
import pandas as pd
from get_price import getLatestPriceByRedisCache
from datetime import datetime, timedelta
import csv

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

def deal_part_data(today, account_file, position_file, deal_local_path, product_name, account_name, fund_accounts, reverse):
    
    for fund_account, other_name in fund_accounts.items():
        print(today, account_file, position_file, deal_local_path, product_name, account_name, other_name, fund_account, reverse)

        # 从position获取 市值 盈亏 资产占比
        holdings_df = pd.read_csv(position_file, encoding=tool.detect_encoding(position_file))

        # 筛选包含当前 fund_account 的数据
        filtered_holdings_df = holdings_df[holdings_df['资金账号'].astype(str) == str(fund_account)]

        security_code = filtered_holdings_df['证券代码'].tolist()
        repaired_security_codes = [RepairACodeProc(str(code)) for code in security_code]
        filtered_holdings_df['代码'] = repaired_security_codes
        code_line = filtered_holdings_df['代码'].tolist()
        price_df = getLatestPriceByRedisCache(code_line)
        price_mapping = dict(zip(price_df['Code'], price_df['NOW']))
        missing_codes = [code for code in code_line if code not in price_mapping]
        if missing_codes:
            print("以下代码在价格映射中缺失:", missing_codes)

        # 增加“收盘价”列，并赋值直接使用 filtered_holdings_df['代码'] 从价格映射中获取收盘价，特殊代码设为 0
        filtered_holdings_df['收盘价'] = [
            0 if code in reverse else price_mapping.get(code, None) 
            for code in filtered_holdings_df['代码']
        ]

        market_value = (filtered_holdings_df['收盘价'] * filtered_holdings_df['当前拥股']).sum()
        # daily_profit_sum = filtered_holdings_df['当日盈亏'].sum()
        # 将资产占比列的百分比字符串转换为小数
        filtered_holdings_df['资产占比'] = filtered_holdings_df['资产占比'].str.rstrip('%').astype(float) / 100
        position_ratio_sum = filtered_holdings_df['资产占比'].sum()
        print('position', market_value, position_ratio_sum)

        # 从account获取 总资产 可用金额
        # 这里假设每个资金账号对应的数据在 account_file 里是独立的，如果不是需要调整逻辑
        acconut_df = pd.read_csv(account_file, encoding=tool.detect_encoding(account_file))
        filtered_acconut_df = acconut_df[acconut_df['资金账号'].astype(str) == str(fund_account)]

        total_assets = filtered_acconut_df['总资产'].sum()
        cash = filtered_acconut_df['可用金额'].sum()
        freeze_cash = filtered_acconut_df['冻结金额'].sum()
        print('account', total_assets, cash, freeze_cash)

        # 上一个交易日 
        yesterday_date_str = handle_sql.get_previous_trading_day(today)

        # 读取历史数据
        account_history = handle_sql.select_account(yesterday_date_str, fund_account)
        print('账号历史数据', account_history)
        if isinstance(account_history, (list, tuple)) and len(account_history) == 0:
            yesterday_total_assets = 0.01
        else:
            yesterday_total_assets = float(account_history[0]['totalassets'])
        print('上一个交易日总资产', yesterday_total_assets)
        # print('账号历史数据', account_history[0])

        # 获取申购赎回金额
        subscription_redemption = handle_sql.select_SGSH_amount(today, fund_account)
        if isinstance(subscription_redemption, (list, tuple)) and len(subscription_redemption) == 0:
            sgsh_amount = 0
        else:
            sgsh_amount = sum(float(item['amount']) for item in subscription_redemption)
            # sgsh_amount = float(subscription_redemption[0]['amount'])
            print('申购赎回', sgsh_amount)
        print('申购赎回金额：', sgsh_amount)

        # 计算日涨跌幅
        print(today, account_name, subscription_redemption) 
        if sgsh_amount >= 0:  # 申购
            daily_return = (total_assets - abs(sgsh_amount) - yesterday_total_assets) / (yesterday_total_assets + abs(sgsh_amount)) if (yesterday_total_assets + abs(sgsh_amount)) != 0 else 0
            daily_profit_sum = total_assets - abs(sgsh_amount) - yesterday_total_assets
        else:
            daily_return = (total_assets + abs(sgsh_amount) - yesterday_total_assets) / (yesterday_total_assets - abs(sgsh_amount)) if (yesterday_total_assets - abs(sgsh_amount)) != 0 else 0
            daily_profit_sum = total_assets + abs(sgsh_amount) - yesterday_total_assets
        # 将 today 转换为日期类型
        today = datetime.strptime(today, '%Y%m%d')

        # 计算月起始日期
        last_month_date = today.replace(month=today.month, year=today.year, day=1)
        # 计算年起始日期
        last_year_date = today.replace(year=today.year, month=1, day=1)

        # 计算月涨跌幅和月盈亏
        monthly_data = handle_sql.select_account_by_range(last_month_date.strftime('%Y%m%d'), today.strftime('%Y%m%d'), fund_account)
        print('月数据', monthly_data)
        if not monthly_data.empty:
            monthly_profit = monthly_data['daily'].sum()
            monthly_profit += daily_profit_sum
            monthly_return = 1
            for daily_per in monthly_data['dailyper']:
                daily_per_value = float(daily_per.strip('%')) / 100
                monthly_return *= (1 + daily_per_value)
            monthly_return *= (1 + daily_return)
            monthly_return -= 1
        else:
            monthly_return = daily_return
            monthly_profit = daily_profit_sum

        # 计算年涨跌幅和年盈亏
        annual_data = handle_sql.select_account_by_range(last_year_date.strftime('%Y%m%d'), today.strftime('%Y%m%d'), fund_account)
        if not annual_data.empty:
            annual_profit = annual_data['daily'].sum()
            annual_profit += daily_profit_sum
            annual_return = 1
            for daily_per in annual_data['dailyper']:
                daily_per_value = float(daily_per.strip('%')) / 100
                annual_return *= (1 + daily_per_value)
            annual_return *= (1 + daily_return)
            annual_return -= 1
        else:
            annual_return = daily_return
            annual_profit = daily_profit_sum

        # 计算总涨跌幅和总盈亏
        start_date = '19000101'
        total_data = handle_sql.select_account_by_range(start_date, today.strftime('%Y%m%d'), fund_account)
        if not total_data.empty:
            total_profit = total_data['daily'].sum()
            total_profit += daily_profit_sum
            total_return = 1
            for daily_per in total_data['dailyper']:
                daily_per_value = float(daily_per.strip('%')) / 100
                total_return *= (1 + daily_per_value)
            total_return *= (1 + daily_return)
            total_return -= 1
        else:
            total_return = daily_return
            total_profit = daily_profit_sum

        # 计算国债逆回购
        reverse = deal_reverse.process_csv_file(deal_local_path, fund_account)
        print('国债逆回购', deal_local_path, reverse)

        # 生成结果
        result = {
            'Date': today.strftime('%Y%m%d'),
            'FundAccount': fund_account,
            'Account': other_name,
            'Product': product_name,
            'TotalAssets': round(total_assets, 2),
            'MarketValue': round(market_value, 2),
            'Cash': round(cash + reverse + freeze_cash, 2),
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

def add_2hao_sql():
    import pandas as pd
    # 假设 CSV 文件路径，需替换为实际路径
    csv_file_path = 'C:/Users/Top/Desktop/尊享2号 _product.csv'
    try:
        # 读取 CSV 文件
        df = pd.read_csv(csv_file_path, encoding=tool.detect_encoding(csv_file_path))
        # 遍历 DataFrame 中的每一行
        for index, row in df.iterrows():
            result = row.to_dict()
            formatted_result = {
                'Date': result.get('Date', ''),
                'Product': result.get('Product', ''),
                'DailyPer': f"{float(result.get('DailyPer', 0)):.2f}%",
                'Daily': round(float(result.get('Daily', 0)), 2)
            }
            print(formatted_result)
            # # 使用 handle_sql.add_account(result) 插入数据
            # result = {'Date': 20250603, 'FundAccount': 109157019055, 'Account': '中泰证券', 'Product': '尊享2号', 'DailyPer': '1.07%', 'Daily': 181024.81}
            # 转换 Date 字段为日期字符串
            if 'Date' in formatted_result:
                date_str = str(formatted_result['Date'])
                formatted_result['Date'] = f'{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}'
            # 然后再调用插入数据的方法
            handle_sql.add_product(formatted_result)
        print('数据插入成功')
    except Exception as e:
        print(f'数据插入失败: {e}')


def iterate_dates(date_list):
    config = tool.read_ftp_config()
    if config:
        reverse_flag = config['reverse']
        for date in date_list:
            for product_info in config['products']:
                product_title = product_info['name']
                for code_info in product_info['codes']:
                    code_name = code_info['name']
                    accounts = code_info['fund_account']

                    position_path = product_info['local_path']+f'{code_name}-PositionStatics-{date}.csv'
                    account_path = product_info['local_path']+f'{code_name}-Account-{date}.csv'
                    deal_path = product_info['local_path']+f'{code_name}-Deal-{date}.csv'

                    deal_part_data(date, account_path, position_path, deal_path, product_title, code_name, accounts, reverse_flag)


def main_test():
    from datetime import datetime, timedelta

    start_date = datetime.strptime('20250513', '%Y%m%d')
    end_date = datetime.strptime('20250603', '%Y%m%d')
    current_date = start_date
    date_list = []
    while current_date <= end_date:
        current_dates_str = current_date.strftime('%Y%m%d')
        if handle_sql.check_isstockday(current_dates_str):
            date_list.append(current_dates_str)
        current_date += timedelta(days=1)
    iterate_dates(date_list)


def main():
    today = datetime.today().strftime("%Y%m%d")
    # today = '20250609'
    config_data = tool.read_ftp_config()

    if config_data:
        reverse = config_data['reverse']
        for product in config_data['products']:
            product_name = product['name']
            for code in product['codes']:
                name = code['name']
                fund_accounts = code['fund_account']

                position_local_path = product['local_path']+f'{name}-PositionStatics-{today}.csv'
                account_local_path = product['local_path']+f'{name}-Account-{today}.csv'
                deal_local_path = product['local_path']+f'{name}-Deal-{today}.csv'

                deal_part_data(today, account_local_path, position_local_path, deal_local_path, product_name, name, fund_accounts, reverse)


if __name__ == "__main__":
    main()
    # main_test()
    # add_2hao_sql()