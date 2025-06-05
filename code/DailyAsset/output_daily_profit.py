# 最终输出
# 已经完成：
# 基于日涨跌幅计算月盈亏\年盈亏\总盈亏
# 根据持仓数量计算持仓总额


import pandas as pd
from datetime import datetime, timedelta
import chardet


def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']


def get_last_month_date():
    today = datetime.now()
    last_month = today.replace(day=1) - timedelta(days=1)
    return last_month.strftime('%Y-%m-%d')


def get_last_year_date():
    today = datetime.now()
    last_year = today.replace(year=today.year - 1)
    return last_year.strftime('%Y-%m-%d')


def calculate_monthly_profit(strategy_type, last_month_date, history_df):
    # 筛选出策略类型匹配且日期大于等于上个月当天的数据
    filtered_df = history_df[(history_df['名称'] == strategy_type) & (history_df['时间'] >= last_month_date)]
    if filtered_df.empty:
        return 0
    # 获取上个月当天的昨日仓位
    last_month_yesterday_position = filtered_df.iloc[0]['昨日持仓']
    # 计算所有日涨跌幅的乘积
    total_return = 1
    for daily_return in filtered_df['日涨跌幅']:
        total_return *= (1 + daily_return)
    # 计算月盈亏
    monthly_profit = last_month_yesterday_position * (total_return - 1)
    return monthly_profit


def calculate_yearly_profit(strategy_type, last_year_date, history_df):
    # 筛选出策略类型匹配且日期大于等于去年当天的数据
    filtered_df = history_df[(history_df['名称'] == strategy_type) & (history_df['时间'] >= last_year_date)]
    if filtered_df.empty:
        return 0
    # 获取去年当天的昨日仓位
    last_year_yesterday_position = filtered_df.iloc[0]['昨日持仓']
    # 计算所有日涨跌幅的乘积
    total_return = 1
    for daily_return in filtered_df['日涨跌幅']:
        total_return *= (1 + daily_return)
    # 计算年盈亏
    yearly_profit = last_year_yesterday_position * (total_return - 1)
    return yearly_profit


def calculate_total_profit(strategy_type, history_df):
    # 筛选出策略类型匹配的所有数据
    filtered_df = history_df[history_df['名称'] == strategy_type]
    if filtered_df.empty:
        return 0
    # 获取最早的昨日仓位
    first_yesterday_position = filtered_df.iloc[0]['昨日持仓']
    # 计算所有日涨跌幅的乘积
    total_return = 1
    for daily_return in filtered_df['日涨跌幅']:
        total_return *= (1 + daily_return)
    # 计算总盈亏
    total_profit = first_yesterday_position * (total_return - 1)
    return total_profit


def main():
    # 读取文件路径
    yesterday_path = r'c:\Users\Top\Desktop\FuYing\code\DailyAsset\持仓\昨日持仓.csv'
    today_path = r'c:\Users\Top\Desktop\FuYing\code\DailyAsset\持仓\今日持仓.xlsx'
    subscription_redemption_path = r'c:\Users\Top\Desktop\FuYing\code\DailyAsset\持仓\申购赎回记录.csv'
    history_path = r'c:\Users\Top\Desktop\FuYing\code\DailyAsset\持仓\每日持仓收益.csv'

    # 读取数据
    yesterday_df = pd.read_csv(yesterday_path, encoding=detect_encoding(yesterday_path))
    today_df = pd.read_excel(today_path)
    subscription_redemption_df = pd.read_csv(subscription_redemption_path, encoding=detect_encoding(subscription_redemption_path))
    try:
        history_df = pd.read_csv(history_path, encoding=detect_encoding(history_path))
    except FileNotFoundError:
        history_df = pd.DataFrame(columns=['时间', '名称', '资产总计', '仓位占比', '昨日持仓', '今日持仓', '申购或赎回', '手续费', '日涨跌幅', '日盈亏', '月涨跌幅', '月盈亏', '年涨跌幅', '年盈亏', '总涨跌幅', '总盈亏'])

    # 计算当前日期
    current_date = datetime.now().strftime('%Y-%m-%d')
    last_month_date = get_last_month_date()
    last_year_date = get_last_year_date()

    # 初始化一个空列表来存储新表格的数据
    new_table_data = []

    # 定义默认总资产
    total_assets_default = 100000

    # 按策略类型分组，这里假设昨日和今日的策略类型一致
    grouped_yesterday = yesterday_df.groupby('策略类型')
    grouped_today = today_df.groupby('策略类型')

    for (strategy_type_yesterday, group_yesterday), (strategy_type_today, group_today) in zip(grouped_yesterday, grouped_today):
        assert strategy_type_yesterday == strategy_type_today, "策略类型不匹配"
        # 计算昨日持仓市值
        yesterday_market_value = (group_yesterday['Close'] * group_yesterday['股票数量']).sum()
        # 计算今日持仓市值
        today_market_value = (group_today['Close'] * group_today['股票数量']).sum()
        # 计算资产总计
        total_assets = total_assets_default
        # 计算仓位占比
        position_ratio = today_market_value / total_assets if total_assets > 0 else 0

        # 初始化申购或赎回值
        subscription_redemption = 0
        # 匹配策略类型并更新申购或赎回值
        matched_records = subscription_redemption_df[subscription_redemption_df['策略类型'] == strategy_type_yesterday]
        for _, record in matched_records.iterrows():
            if record['操作类型'] == '申购':
                subscription_redemption += record['金额']
            elif record['操作类型'] == '赎回':
                subscription_redemption -= record['金额']

        # 计算日涨跌幅
        fee = 10
        if subscription_redemption >= 0:  # 申购
            daily_return = (today_market_value - abs(subscription_redemption) - yesterday_market_value - fee) / (yesterday_market_value + subscription_redemption) if yesterday_market_value + subscription_redemption != 0 else 0
        else:
            daily_return = (today_market_value + abs(subscription_redemption) - yesterday_market_value - fee) / yesterday_market_value if yesterday_market_value != 0 else 0

        # 计算月盈亏
        monthly_profit = calculate_monthly_profit(strategy_type_yesterday, last_month_date, history_df)
        monthly_return = monthly_profit / yesterday_market_value if yesterday_market_value != 0 else 0

        # 计算年盈亏
        yearly_profit = calculate_yearly_profit(strategy_type_yesterday, last_year_date, history_df)
        yearly_return = yearly_profit / yesterday_market_value if yesterday_market_value != 0 else 0

        # 计算总盈亏
        total_profit = calculate_total_profit(strategy_type_yesterday, history_df)
        total_return = total_profit / yesterday_market_value if yesterday_market_value != 0 else 0

        new_table_data.append({
            '时间': current_date,
            '名称': strategy_type_yesterday,
            '资产总计': total_assets,
            '仓位占比': f'{position_ratio * 100:.2f}%',
            '昨日持仓': yesterday_market_value,
            '今日持仓': today_market_value,
            '申购或赎回': subscription_redemption,
            '手续费': fee,
            '日涨跌幅': daily_return,
            '日盈亏': yesterday_market_value * daily_return,
            '月涨跌幅': monthly_return,
            '月盈亏': monthly_profit,
            '年涨跌幅': yearly_return,
            '年盈亏': yearly_profit,
            '总涨跌幅': total_return,
            '总盈亏': total_profit
        })

    # 创建新的 DataFrame
    new_yesterday_df = pd.DataFrame(new_table_data)

    # 保存为新的表格文件到指定绝对路径
    output_path = r'c:\Users\Top\Desktop\FuYing\code\DailyAsset\持仓\每日持仓收益.csv'
    # 合并数据时将新数据放在前面
    combined_df = pd.concat([new_yesterday_df, history_df], ignore_index=True)
    combined_df.to_csv(output_path, index=False)


if __name__ == "__main__":
    main()