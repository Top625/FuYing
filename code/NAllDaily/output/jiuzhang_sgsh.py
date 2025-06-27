from lark_oapi import im
import pandas as pd
import handle_sql
import tool

def process_xlsx(input_path, output_path):
    # 读取xlsx文件
    df = pd.read_excel(input_path)

    # 筛选对手方户名以‘股份有限公司（客户）’结尾的数据
    filtered_df = df[df['对手方户名'].astype(str).str.endswith('股份有限公司（客户）')].copy()

    # 使用 .loc 避免 SettingWithCopyWarning
    filtered_df.loc[:, '公司名称'] = filtered_df['对手方户名'].str.replace('股份有限公司（客户）', '')

    # 检查列名是否存在
    required_columns = ['公司名称', '划款金额(元)', '划款日期', '摘要']
    for col in required_columns:
        if col not in filtered_df.columns:
            print(f'列 {col} 不存在于数据中，请检查列名。')
            return

    # 使用 .loc 选择所需列并创建新的 DataFrame
    result_df = filtered_df.loc[:, required_columns].copy()

    # 移除划款金额(元)列中的逗号，并使用 .loc 赋值
    result_df.loc[:, '划款金额(元)'] = result_df['划款金额(元)'].astype(str).str.replace(',', '')

    # 将划款金额(元)列转换为数值类型，并使用 .loc 赋值
    result_df.loc[:, '划款金额(元)'] = pd.to_numeric(result_df['划款金额(元)'], errors='coerce')

    # 根据摘要修改划款金额的符号
    result_df.loc[result_df['摘要'] == '证券转银行', '划款金额(元)'] = -result_df['划款金额(元)']

    # 保存结果到新的xlsx文件
    result_df.to_csv(output_path.replace('.xlsx', '.csv'), index=False)

def deal_data():
    input_file_path = 'C:/Users/Top/Desktop/九章量化申购赎回.xls'
    output_file_path = 'C:/Users/Top/Desktop/九章量化申购赎回结果.csv'
    process_xlsx(input_file_path, output_file_path)

def add_sgsh(output_file_path):
    try:
        # 指定编码格式为 UTF-8
        df = pd.read_csv(output_file_path, encoding=tool.detect_encoding(output_file_path))
        for index, row in df.iterrows():
            # 将 Series 转换为字典
            row_dict = row.to_dict()
            # 假设 ftp_config.json 中的映射关系已加载到 account_mapping 字典中
            account_mapping = {
                "国信证券": "190900011119",
                "国泰海通": "9220717",
                "中泰证券": "109157018941",
                "国泰君安": "9220717",
            }
            account = row.get('Account', '')
            account = account[:4]
            fund_account = account_mapping.get(account, '')
            row_dict['Product'] = "九章量化"
            row_dict['Account'] = account
            row_dict['FundAccount'] = fund_account
            print(row_dict) 
            # 调用 add_SGSH 函数插入数据
            success = add_SGSH(row_dict)
            if success:
                print(f"成功插入数据: {row_dict}")
            else:
                print(f"插入数据失败: {row_dict}")
    except FileNotFoundError:
        print(f"未找到文件: {output_file_path}")
    except Exception as e:
        print(f"处理文件时出错: {e}")


def deal_daily(file_path):
    try:
        # 读取 xls 文件
        # 读取文件时设置 thousands 参数处理千位分隔符
        df = pd.read_excel(file_path, thousands=',')
        
        # 确保存在资产总值列
        if '资产总值' in df.columns:
            # 计算日涨跌幅
            if '累计净值' in df.columns:
                df['日涨跌幅'] = (df['累计净值'] / df['累计净值'].shift(-1)) - 1
                df.loc[df.index[-1], '日涨跌幅'] = pd.NA

            # 计算盈亏
            if '日涨跌幅' in df.columns:
                df['盈亏'] = df['资产总值'].shift(-1) * df['日涨跌幅']
                df.loc[df.index[-1], '盈亏'] = pd.NA

            # 保存修改后的数据到新文件，可根据需求调整保存路径
            new_file_path = file_path.replace('.xlsx', '_结果.xlsx')
            df.to_excel(new_file_path, index=False)
            print(f'处理完成，结果已保存到 {new_file_path}')
        else:
            print('文件中不存在“资产总值”列，请检查。')
    except FileNotFoundError:
        print(f'未找到指定文件: {file_path}')
    except Exception as e:
        print(f'处理文件时发生错误: {e}')

def insert_data_to_db(df):
    for index, row in df.iterrows():
        today = row['净值日期']
        # 假设这些变量可以从表格中获取，若不能需要额外处理
        fund_account = '190900011119'
        other_name = '国信证券'
        product_name = '九章量化'
        total_assets = None
        market_value = None
        cash = None
        position_ratio_sum = None
        daily_profit_sum = row['国信盈亏']
        daily_return = row['国信日盈亏率']
        monthly_return = None
        monthly_profit = None
        annual_return = None
        annual_profit = None
        total_return = None
        total_profit = None

        result = {
            'Date': today, 
            'FundAccount': fund_account, 
            'Account': other_name, 
            'Product': product_name, 
            'TotalAssets': total_assets, 
            'MarketValue': market_value, 
            'Cash': cash, 
            'Position': position_ratio_sum, 
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
        today = row['Date']
        # 假设这些变量可以从表格中获取，若不能需要额外处理
        # fund_account = '50186688'
        product_name = '九章量化'
        total_assets = None
        market_value = None
        cash = None
        position_ratio_sum = None
        daily_return = row['DailyPer']
        daily_profit_sum = row['Daily']
        # 假设月度、年度和总收益相关数据暂时未知，设置为 0
        monthly_return = None
        monthly_profit = None
        annual_return = None
        annual_profit = None
        total_return = None
        total_profit = None
        net_value_est = row['NetValueEst']

        result = {
            'Date': today, 
            'Product': product_name, 
            'TotalAssets': total_assets, 
            'MarketValue': market_value, 
            'Cash': cash, 
            'Position': position_ratio_sum, 
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
        # handle_sql.add_product(result)

if __name__ == '__main__':
    pass 
    # output_file_path = 'C:/Users/Top/Desktop/九章量化申购赎回结果.csv'
    # add_sgsh(output_file_path)

    # deal_data()

    # 处理日涨跌幅
    # file_path = 'C:/Users/Top/Desktop/九章历史净值.xlsx'
    # deal_daily(file_path)

    # output_path = "C:/Users/Top/Desktop/九章历史净值_结果.xlsx"  
    # df = pd.read_excel(output_path)
    # insert_data_to_db_product(df)

    output_path = "C:/Users/Top/Desktop/5.16-6.3.xlsx"  
    df = pd.read_excel(output_path)
    insert_data_to_db(df)
