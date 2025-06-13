import pandas as pd
import handle_sql

def calculate_net_value(input_file, output_file):
    # 读取数据
    df = pd.read_excel(input_file)
    
    # 按日期从早到晚排序
    df = df.sort_values(by='日期')
    
    # 初始化净值列 (假设第一天的净值为1)
    df['净值'] = 1.0
    
    # 计算日涨跌幅和净值
    for i in range(1, len(df)):
        prev_total = df.at[i-1, '总资产']
        current_total = df.at[i, '总资产']
        inflow = df.at[i, '净流入']
        
        # 计算日涨跌幅
        daily_return = (current_total - inflow - prev_total) / (prev_total + inflow)
        df.at[i, '日涨跌幅'] = daily_return
        
        # 计算净值
        df.at[i, '净值'] = df.at[i-1, '净值'] * (1 + daily_return)
    
    # 保存结果
    df.to_excel(output_file, index=False)

if __name__ == "__main__":
    input_path = "c:\\Users\\Top\\Desktop\\山西证券资产.xlsx"  # 修改为你的输入文件路径
    output_path = "c:\\Users\\Top\\Desktop\\山西证券资产 结果.xlsx"  # 修改为你的输出文件路径
    calculate_net_value(input_path, output_path)