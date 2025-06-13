import handle_sql
import pandas as pd

# 使用绝对路径读取 Excel 文件
file_path = r'C:\Users\Top\Desktop\九章历史净值.xls'
try:
    df = pd.read_excel(file_path)
    # 假设日期列名为 '日期'，资产份额净值(元) 列名为 '资产份额净值(元)'
    for index, row in df.iterrows():
        date = row['净值日期']
        net_value = row['单位净值']
        print(handle_sql.add_net_value(date, '九章量化', net_value, None))
except FileNotFoundError:
    print(f"未找到文件: {file_path}")
except KeyError:
    print("Excel 文件中未找到指定的列名，请检查列名是否正确。")


folder_path = r'C:\Users\Top\Desktop\email'
# 遍历文件夹中的所有文件
for file_name in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file_name)
    # 检查是否为文件且文件名符合格式
    if os.path.isfile(file_path) and '基金净值信息_富赢尊享2号私募证券投资基金_' in file_name and file_name.endswith('.xls'):
        # 提取日期
        match = re.search(r'\((.*?)\)', file_name)
        if match:
            date = match.group(1)
            # 调用 deal_zunxiang 函数
            net_value = deal_zunxiang(date)
            if net_value is not None:
                print(f"成功获取尊享2号基金在 {date} 的净值: {net_value}")
        else:
            print(f"未能从文件名 {file_name} 中提取到日期。")
    else:
        print(f"{file_name} 不是符合条件的文件。")

