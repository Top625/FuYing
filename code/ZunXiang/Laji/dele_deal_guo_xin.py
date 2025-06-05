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


def calculate_period_stats(historical_data, start_date, end_date, current_date_str):
    daily_return_product = 1
    daily_profit_sum = 0
    for data in historical_data:
        data_date = datetime.strptime(data['时间'], '%Y%m%d')
        if start_date <= data_date <= end_date:
            daily_return = float(data['日涨跌幅'].strip('%')) / 100
            daily_return_product *= (1 + daily_return)
            daily_profit_sum += float(data['日盈亏'])
    # 如果没有历史数据，使用当前日涨跌幅和日盈亏
    if not historical_data or (start_date > datetime.strptime(current_date_str, '%Y%m%d')):
        return None, None
    return daily_return_product - 1, daily_profit_sum


def main():
    # 定义文件路径
    account_file = r'c:\Users\Top\Desktop\FuYing\code\Nine\ftp\九章国信-Account-20250526.csv'
    position_file = r'c:\Users\Top\Desktop\FuYing\code\Nine\ftp\九章国信-PositionStatics-20250526.csv'
    output_file = r'c:\Users\Top\Desktop\FuYing\code\Nine\ftp\九章国信-result.csv'

    # 检测文件编码
    account_encoding = detect_encoding(account_file)
    position_encoding = detect_encoding(position_file)

    # 读取 FOF 国君 - Account - 20250526.csv 文件
    with open(account_file, 'r', encoding=account_encoding) as f:
        account_reader = csv.reader(f)
        account_header = next(account_reader)
        account_row = next(account_reader)

        # 获取各列名对应的索引
        account_name_index = account_header.index('账号名称')
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
        name_index = position_header.index('账号名称')
        current_shares_index = position_header.index('当前拥股')
        latest_price_index = position_header.index('最新价')
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

    # 计算日涨跌幅
    yesterday_total_assets = 35000000.00
    daily_return = (total_assets / yesterday_total_assets) - 1

    # 获取当前日期
    current_date = datetime.now()
    current_date_str = current_date.strftime('%Y%m%d')

    # 读取历史数据
    historical_data = read_historical_data(output_file)

    # 计算月起始日期
    last_month_date = current_date - timedelta(days=30)
    # 计算年起始日期
    last_year_date = current_date - timedelta(days=365)

    # 计算月涨跌幅和月盈亏
    monthly_return, monthly_profit = calculate_period_stats(historical_data, last_month_date, current_date,
                                                            current_date_str)
    if monthly_return is None:
        monthly_return = daily_return
        monthly_profit = daily_profit_sum

    # 计算年涨跌幅和年盈亏
    annual_return, annual_profit = calculate_period_stats(historical_data, last_year_date, current_date,
                                                          current_date_str)
    if annual_return is None:
        annual_return = daily_return
        annual_profit = daily_profit_sum

    # 计算总涨跌幅和总盈亏
    total_return, total_profit = calculate_period_stats(historical_data, datetime.min, current_date, current_date_str)
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
    main()