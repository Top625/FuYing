import os
import pandas as pd
import re

# 指定路径
path = r'c:\Users\Top\Desktop\remote_Strategy_Daily'
excel_path = r'C:\Users\Top\Desktop\FuYing\code\Test\task_scheduler_info.xlsx'

# 读取 Excel 文件
df = pd.read_excel(excel_path)

# 假设 Excel 中有一列存储执行的脚本数据，这里先模拟一个列名，你需要根据实际情况修改
script_column = '执行的脚本/命令'  # 请替换为实际的列名

# 提取 bat 文件名（不包含 .bat 后缀）
bat_names = []
for script in df[script_column]:
    if isinstance(script, str):
        match = re.search(r'(\w+)\.bat', script)
        if match:
            bat_names.append(match.group(1))

# 查找指定路径下的所有 py 文件
py_files = []
for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith('.py'):
            py_files.append(os.path.join(root, file))

# 定义数据库名的匹配模式
db_pattern = re.compile(r'sql_table_name\s*=\s*["\'](\w+)["\']')

# 遍历每个 bat 对应的 py 文件，查找操作的数据库名
db_names_dict = {}
for bat_name in bat_names:
    for py_file in py_files:
        if bat_name in py_file:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                matches = db_pattern.findall(content)
                if matches:
                    db_names_dict[bat_name] = ', '.join(set(matches))

# 将匹配到的数据库名字添加到 xlsx 表格中
df['操作的数据库'] = ''
for index, row in df.iterrows():
    if isinstance(row[script_column], str):
        match = re.search(r'(\w+)\.bat', row[script_column])
        if match:
            bat_name = match.group(1)
            if bat_name in db_names_dict:
                df.at[index, '操作的数据库'] = db_names_dict[bat_name]

# 保存修改后的 Excel 文件
df.to_excel(excel_path, index=False)