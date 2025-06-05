import csv
from datetime import datetime, timedelta
import chardet
import os


def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']


def read_historical_data(output_file):
    historical_data = []
    # 检测文件编码
    output_encoding = detect_encoding(output_file)

    if os.path.exists(output_file):
        with open(output_file, 'r', encoding=output_encoding) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                historical_data.append(row)
    return historical_data


def calculate_period_stats(historical_data, start_date, end_date, current_date_str, name_index, today_daily_return):
    daily_return_product = 1
    daily_profit_sum = 0
    for data in historical_data:
        print(data['产品'])
        print(name_index)
        if data['产品'] == name_index:
            data_date = datetime.strptime(data['时间'], '%Y%m%d')
            if start_date <= data_date <= end_date:
                daily_return = float(data['日涨跌幅'].strip('%')) / 100
                daily_return_product *= (1 + daily_return)
                daily_profit_sum += float(data['日盈亏'])
    # 如果没有历史数据，使用当前日涨跌幅和日盈亏
    if not historical_data or (start_date > datetime.strptime(current_date_str, '%Y%m%d')):
        return None, None
    daily_return_product *= (1 + today_daily_return)
    return daily_return_product - 1, daily_profit_sum

def get_subscription_redemption_amount(product_name=None, date_str=None, file_path=None):
    """
    读取申购赎回记录表格，根据产品名和日期获取申购或赎回的金额。

    :param product_name: 产品名称，可选参数，默认为 None
    :param date_str: 日期字符串，格式需与表格中日期格式一致
    :param file_path: 申购赎回记录表格的文件路径
    :return: 带有正负值的金额，申购为正，赎回为负；若未匹配到记录则返回 0
    """
    if date_str is None or file_path is None:
        return 0
    encoding = detect_encoding(file_path)
    with open(file_path, 'r', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # 如果 product_name 为 None，只匹配日期
            if product_name is None and row['时间'] == date_str:
                if row['操作类型'] == '申购':
                    return float(row['金额'])
                elif row['操作类型'] == '赎回':
                    return -float(row['金额'])
            # 否则，尝试匹配产品名和日期
            elif product_name is not None and '产品' in row and row['产品'] == product_name and row['时间'] == date_str:
                if row['操作类型'] == '申购':
                    return float(row['金额'])
                elif row['操作类型'] == '赎回':
                    return -float(row['金额'])
    return 0


def deal_part_data(today, account_file, position_file, output_file):
    # 检测文件编码
    account_encoding = detect_encoding(account_file)
    position_encoding = detect_encoding(position_file)

    # 读取 FOF 国君 - Account - 20250526.csv 文件
    with open(account_file, 'r', encoding=account_encoding) as f:
        account_reader = csv.reader(f)
        account_header = next(account_reader)
        account_row = next(account_reader)

        # 获取各列名对应的索引
        account_name_index = account_header.index('证券公司')
        total_assets_index = account_header.index('总资产')
        cash_index = account_header.index('可用金额')

        # 明确提取总资产和可用金额
        account_name = account_row[account_name_index]
        total_assets = float(account_row[total_assets_index])
        cash = float(account_row[cash_index])

    # 读取 FOF 国君 - PositionStatics - 20250526.csv 文件
    market_value = 0
    position_ratio_sum = 0
    daily_profit_sum = 0

    with open(position_file, 'r', encoding=position_encoding) as f:
        position_reader = csv.reader(f)
        position_header = next(position_reader)

        # 获取各列名对应的索引
        name_index = position_header.index('证券公司')
        current_shares_index = position_header.index('当前拥股')
        latest_price_index = position_header.index('收盘价')
        position_ratio_index = position_header.index('资产占比')
        daily_profit_index = position_header.index('当日盈亏')

        for row in position_reader:
            # 检查账号名称是否匹配
            if row[name_index] == account_name:
                current_shares = int(row[current_shares_index])
                latest_price = float(row[latest_price_index])
                market_value += current_shares * latest_price
                position_ratio_sum += float(row[position_ratio_index].strip('%')) / 100
                daily_profit_sum += float(row[daily_profit_index])

    # 获取当前日期
    # 将 today 字符串转换为 datetime 对象
    current_date = datetime.strptime(today, '%Y%m%d')
    current_date_str = today

    # 读取历史数据
    historical_data = read_historical_data(output_file)

    # 计算昨天的日期
    yesterday = current_date - timedelta(days=4)
    yesterday_date_str = yesterday.strftime('%Y%m%d')

    # 初始化 yesterday_total_assets 为 None
    yesterday_total_assets = None
    print(account_name)
    if account_name == '北京德外大街':
        account_name = '国泰海通'
    elif account_name == '国信证券':
        account_name = '国信'

    # 遍历历史数据，查找昨天的记录
    for data in historical_data:
        if data['时间'] == yesterday_date_str and data['产品'] == account_name:
            yesterday_total_assets = float(data['总资产'])
            break
    
   # 获取申购赎回金额
    subscription_redemption_path = r'C:\Users\Top\Desktop\九章量化\申购赎回记录.csv'
    subscription_redemption = get_subscription_redemption_amount(account_name, current_date, subscription_redemption_path)
    print(subscription_redemption, yesterday_total_assets, account_name) 
    if subscription_redemption >= 0:  # 申购
        daily_return = (total_assets - abs(subscription_redemption) - yesterday_total_assets) / (yesterday_total_assets + subscription_redemption) if (yesterday_total_assets + subscription_redemption) != 0 else 0
    else:
        daily_return = (total_assets + abs(subscription_redemption) - yesterday_total_assets) / yesterday_total_assets if yesterday_total_assets != 0 else 0

    # 计算日涨跌幅
    # daily_return = (total_assets / yesterday_total_assets) - 1
    # 计算月起始日期
    last_month_date = current_date - timedelta(days=30)
    # 计算年起始日期
    last_year_date = current_date - timedelta(days=365)

    # 计算月涨跌幅和月盈亏
    monthly_return, monthly_profit = calculate_period_stats(historical_data, last_month_date, current_date,
                                                            current_date_str, account_name, daily_return)
    if monthly_return is None:
        monthly_return = daily_return
        monthly_profit = daily_profit_sum

    # 计算年涨跌幅和年盈亏
    annual_return, annual_profit = calculate_period_stats(historical_data, last_year_date, current_date,
                                                          current_date_str, account_name, daily_return)
    if annual_return is None:
        annual_return = daily_return
        annual_profit = daily_profit_sum

    # 计算总涨跌幅和总盈亏
    total_return, total_profit = calculate_period_stats(historical_data, datetime.min, current_date,
                                                         current_date_str, account_name, daily_return)
    if total_return is None:
        total_return = daily_return
        total_profit = daily_profit_sum

    # 生成结果
    result = {
        '产品': account_name,
        '时间': current_date_str,
        '总资产': round(total_assets, 2),
        '市值': round(market_value, 2),
        '现金': round(cash, 2),
        '仓位': f"{position_ratio_sum * 100:.2f}%",
        '日涨跌幅': f"{daily_return * 100:.2f}%",
        '日盈亏': round(daily_profit_sum, 2),
        '月涨跌幅': f"{monthly_return * 100:.2f}%",
        '月盈亏': round(monthly_profit, 2),
        '年涨跌幅': f"{annual_return * 100:.2f}%",
        '年盈亏': round(annual_profit, 2),
        '总涨跌幅': f"{total_return * 100:.2f}%",
        '总盈亏': round(total_profit, 2)
    }

    output_encoding = detect_encoding(output_file)

    # 将结果保存到 CSV 文件
    with open(output_file, 'a', newline='', encoding=output_encoding) as csvfile:
        fieldnames = ['产品', '时间', '总资产', '市值', '现金', '仓位', '日涨跌幅', '日盈亏', '月涨跌幅', '月盈亏', '年涨跌幅', '年盈亏', '总涨跌幅', '总盈亏']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(result)

    print(result)


if __name__ == "__main__":
    # 定义文件路径
    today = datetime.today().strftime("%Y%m%d")
    # today = '20250527'
    account_file = rf'c:\Users\Top\Desktop\九章量化\北京德外大街-Account-{today}.csv'
    position_file = rf'c:\Users\Top\Desktop\九章量化\北京德外大街-PositionStatics-{today}.csv'
    output_file = rf'c:\Users\Top\Desktop\九章量化\part-result.csv'
    deal_part_data(today, account_file, position_file, output_file)

    account_file = rf'c:\Users\Top\Desktop\九章量化\国信证券-Account-{today}.csv'
    position_file = rf'c:\Users\Top\Desktop\九章量化\国信证券-PositionStatics-{today}.csv'
    output_file = r'c:\Users\Top\Desktop\九章量化\part-result.csv'
    deal_part_data(today, account_file, position_file, output_file)