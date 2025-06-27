import pandas as pd
from datetime import datetime
import handle_sql

# 日期、总资产、市值、现金、仓位、日涨跌幅、日盈亏

def calculate_net_value(input_file, output_file):
    # 读取数据
    df = pd.read_excel(input_file)
    
    # 按日期从早到晚排序
    df = df.sort_values(by='日期')
    
    # 初始化净值列 (假设第一天的净值为1)
    # 新增初始化现金、仓位和日盈亏列
    initial_values = { '净值': 1.0, '现金': 0.0, '仓位': 0.0, '日盈亏': 0.0 }
    for col, val in initial_values.items():
        df[col] = val
    
    # 计算日涨跌幅、净值、现金、仓位和日盈亏
    for i in range(1, len(df)):
        prev_total = df.at[i-1, '总资产']
        current_total = df.at[i, '总资产']
        inflow = df.at[i, '净流入']
        market_value = df.at[i, '市值']
    
        # 计算日涨跌幅
        daily_return = (current_total - inflow - prev_total) / (prev_total + inflow)
        df.at[i, '日涨跌幅'] = daily_return
    
        # 计算净值
        df.at[i, '净值'] = df.at[i-1, '净值'] * (1 + daily_return)
    
        # 新增计算现金、仓位和日盈亏
        df.at[i, '现金'] = current_total - market_value
        df.at[i, '仓位'] = market_value / current_total if current_total != 0 else 0
        df.at[i, '日盈亏'] = current_total - inflow - prev_total
    
    # 保存结果
    df.to_excel(output_file, index=False)

    # 调用新封装的方法
    insert_data_to_db(df)

def insert_data_to_db(df):
    for index, row in df.iterrows():
        today = row['日期']
        # 假设这些变量可以从表格中获取，若不能需要额外处理
        fund_account = '50186688'
        other_name = '山西证券'
        product_name = '山西证券'
        total_assets = row['总资产']
        market_value = row['市值']
        cash = row['现金']
        position_ratio_sum = row['仓位']
        daily_return = row['日涨跌幅']
        daily_profit_sum = row['日盈亏']
        # 假设月度、年度和总收益相关数据暂时未知，设置为 0
        monthly_return = None
        monthly_profit = None
        annual_return = None
        annual_profit = None
        total_return = None
        total_profit = None

        result = {
            'Date': today.strftime('%Y%m%d'), 
            'FundAccount': fund_account, 
            'Account': other_name, 
            'Product': product_name, 
            'TotalAssets': round(total_assets, 2), 
            'MarketValue': round(market_value, 2), 
            'Cash': round(cash, 2), 
            'Position': f"{position_ratio_sum * 100:.2f}%", 
            'DailyPer': f"{daily_return * 100:.2f}%", 
            'Daily': round(daily_profit_sum, 2), 
            'MonthlyPer': monthly_return,
            'Monthly': monthly_profit,
            'YearlyPer': annual_return,
            'Yearly': annual_profit,
            'TotalPer': total_return,
            'Total': total_profit
        }
        print("结果----", result)
        handle_sql.add_account(result)

def insert_data_to_db_product(df):
    for index, row in df.iterrows():
        today = row['日期']
        # 假设这些变量可以从表格中获取，若不能需要额外处理
        # fund_account = '50186688'
        product_name = '山西证券'
        total_assets = row['总资产']
        market_value = row['市值']
        cash = row['现金']
        position_ratio_sum = row['仓位']
        daily_return = row['日涨跌幅']
        daily_profit_sum = row['日盈亏']
        # 假设月度、年度和总收益相关数据暂时未知，设置为 0
        monthly_return = None
        monthly_profit = None
        annual_return = None
        annual_profit = None
        total_return = None
        total_profit = None
        net_value_est = row['净值']

        result = {
            'Date': today.strftime('%Y%m%d'), 
            'Product': product_name, 
            'TotalAssets': round(total_assets, 2), 
            'MarketValue': round(market_value, 2), 
            'Cash': round(cash, 2), 
            'Position': f"{position_ratio_sum * 100:.2f}%", 
            'DailyPer': f"{daily_return * 100:.2f}%", 
            'Daily': round(daily_profit_sum, 2), 
            'MonthlyPer': monthly_return,
            'Monthly': monthly_profit,
            'YearlyPer': annual_return,
            'Yearly': annual_profit,
            'TotalPer': total_return,
            'Total': total_profit,
            'NetValueEst': round(net_value_est, 4)
        }
        print("结果----", result)
        handle_sql.add_product(result)

if __name__ == "__main__":
    # input_path = "c:\\Users\\Top\\Desktop\\山西证券资产.xlsx"  # 修改为你的输入文件路径
    output_path = "c:\\Users\\Top\\Desktop\\山西证券资产 新结果.xlsx"  # 修改为你的输出文件路径
    # calculate_net_value(input_path, output_path)

    df = pd.read_excel(output_path)
    insert_data_to_db_product(df)