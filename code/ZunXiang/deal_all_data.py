import csv
from collections import defaultdict
import chardet
import os
from datetime import datetime, timedelta

from pandas.io import parsers

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

def calculate_period_stats(historical_data, start_date, end_date, current_date_str, today_daily_return):
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

def main(input_file, output_file, subscription_redemption_path, today):
    # 检测输入文件编码
    input_encoding = detect_encoding(input_file)

    # 定义新表格的列名
    new_header = ['产品', '时间', '总资产', '市值', '现金', '仓位', '日涨跌幅', '日盈亏', '月涨跌幅', '月盈亏', '年涨跌幅', '年盈亏', '总涨跌幅', '总盈亏']

    # 用于存储按时间分组的数据
    data_by_date = defaultdict(lambda: {
        '总资产': 0,
        '市值': 0,
        '现金': 0,
        '日盈亏': 0,
        '月盈亏': 0,
        '年盈亏': 0,
        '总盈亏': 0  
    })

    # 读取输入文件
    with open(input_file, 'r', encoding=input_encoding) as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            date = row['时间']
            data_by_date[date]['总资产'] += float(row['总资产'])
            data_by_date[date]['市值'] += float(row['市值'])
            data_by_date[date]['现金'] += float(row['现金'])
            data_by_date[date]['日盈亏'] += float(row['日盈亏'])
            data_by_date[date]['月盈亏'] += float(row['月盈亏'])
            data_by_date[date]['年盈亏'] += float(row['年盈亏'])
            data_by_date[date]['总盈亏'] += float(row['总盈亏']) 

    # 对日期进行排序
    sorted_dates = sorted(data_by_date.keys())
    print(sorted_dates)

    # 准备新表格的数据
    new_data = []
    # yesterday_total_assets = 0
    historical_data = read_historical_data(output_file)
    print(historical_data)

    for date in sorted_dates:
        total_assets = data_by_date[date]['总资产']
        market_value = data_by_date[date]['市值']
        cash = data_by_date[date]['现金']
        daily_profit = data_by_date[date]['日盈亏']
        monthly_profit = data_by_date[date]['月盈亏']
        annual_profit = data_by_date[date]['年盈亏']
        total_profit = data_by_date[date]['总盈亏']

        # 计算仓位
        position = market_value / total_assets if total_assets != 0 else 0

        if date == sorted_dates[0]:  # 处理第一天
            pass
        else:
            # 计算昨天的日期
            yesterday = datetime.strptime(date, '%Y%m%d') - timedelta(days=4)
            yesterday_date_str = yesterday.strftime('%Y%m%d')
            yesterday_total_assets = data_by_date[yesterday_date_str]['总资产']

            # 获取申购赎回金额
            # subscription_redemption = get_subscription_redemption_amount(None, date, subscription_redemption_path)
            # print(subscription_redemption) 
            subscription_redemption = 0

            if subscription_redemption >= 0:  # 申购
                daily_return = (total_assets - abs(subscription_redemption) - yesterday_total_assets) / (yesterday_total_assets + subscription_redemption) if yesterday_total_assets + subscription_redemption != 0 else 0
            else:
                daily_return = (total_assets + abs(subscription_redemption) - yesterday_total_assets) / yesterday_total_assets if yesterday_total_assets != 0 else 0
            yesterday_total_assets = total_assets


            current_date = datetime.strptime(today, '%Y%m%d')
            last_month_date = current_date - timedelta(days=30)
            last_year_date = current_date - timedelta(days=365)

            # 计算月涨跌幅
            monthly_return, _ = calculate_period_stats(historical_data, last_month_date, current_date, date, daily_return)
            if monthly_return is None:
                monthly_return = daily_return

            # 计算年涨跌幅
            annual_return, _ = calculate_period_stats(historical_data, last_year_date, current_date, date, daily_return)
            if annual_return is None:
                annual_return = daily_return

            # 计算总涨跌幅
            total_return, _ = calculate_period_stats(historical_data, datetime.min, current_date, date, daily_return)
            if total_return is None:
                total_return = daily_return

            # 格式化资产类数据和涨跌幅数据
            new_row = {
                '产品': '尊享2号' + date,
                '时间': date,
                '总资产': round(total_assets, 2),
                '市值': round(market_value, 2),
                '现金': round(cash, 2),
                '仓位': f"{round(position * 100, 2)}%",
                '日涨跌幅': f"{round(daily_return * 100, 2)}%",
                '日盈亏': round(daily_profit, 2),
                '月涨跌幅': f"{round(monthly_return * 100, 2)}%" if monthly_return is not None else f"{round(daily_return * 100, 2)}%",
                '月盈亏': round(monthly_profit, 2),
                '年涨跌幅': f"{round(annual_return * 100, 2)}%" if annual_return is not None else f"{round(daily_return * 100, 2)}%",
                '年盈亏': round(annual_profit, 2),
                '总涨跌幅': f"{round(total_return * 100, 2)}%" if total_return is not None else f"{round(daily_return * 100, 2)}%",
                '总盈亏': round(total_profit, 2)  
            }
            new_data.append(new_row)

    # 检查文件是否存在，不存在则写入表头
    file_exists = os.path.exists(output_file)
    with open(output_file, 'a', newline='', encoding=detect_encoding(output_file)) as outfile:
        writer = csv.DictWriter(outfile, fieldnames=new_header)
        if not file_exists:
            writer.writeheader()
        for row in new_data:
            writer.writerow(row)

    print(f"新表格已更新，保存路径为: {output_file}")

if __name__ == "__main__":
    today = datetime.today().strftime("%Y%m%d")
    # today = '20250527'
    name = '尊享2号'
    # 定义输入和输出文件路径
    input_file = rf'c:\Users\Top\Desktop\{name}\part-result.csv'
    output_file = rf'c:\Users\Top\Desktop\{name}\all-result.csv'
    subscription_redemption_path = rf'C:\Users\Top\Desktop\{name}\申购赎回记录.csv'
    main(input_file, output_file, subscription_redemption_path, today)