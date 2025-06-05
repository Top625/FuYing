import pandas as pd
import tool
import codecs

def process_csv_file(csv_file_path):
    """
    处理 CSV 文件，根据 reverse 数组匹配证券代码列，累加成交金额并打印匹配数据。
    :param csv_file_path: CSV 文件的绝对路径
    :return: 成交金额的累加量
    """
    config_data = tool.read_ftp_config()
    reverse_codes  = config_data['reverse']
    # 提取代码中的数字部分
    simplified_codes = [code.split('.')[0] for code in reverse_codes]
    if not simplified_codes:
        return 0

    try:
        bmgs = codecs.open(csv_file_path, "r").encoding  # 获取 文件的编码格式
        df = pd.read_csv(csv_file_path, encoding=bmgs)
        # 修改匹配逻辑，使用简化后的代码进行匹配
        matched_df = df[df['证券代码'].astype(str).str.contains('|'.join(simplified_codes))]
        total_amount = matched_df['成交金额'].sum()
        print("匹配到的数据:")
        print(matched_df[['证券代码', '成交金额']])

        return total_amount
    except FileNotFoundError:
        print(f"未找到 {csv_file_path} 文件，请检查文件路径。")
        return 0
    except KeyError:
        print("CSV 文件中未找到指定的列名，请检查列名是否正确。")
        return 0


if __name__ == "__main__":
    # 请将此路径替换为实际的 CSV 文件绝对路径
    today = '20250604'
    csv_file_path = rf'C:\Users\Top\Desktop\山西证券\山西证券-Deal-{today}.csv'
    result = process_csv_file(csv_file_path)
    print(f"山西证券: {result}")

    csv_file_path = rf'C:\Users\Top\Desktop\尊享2号\中泰XTP实盘_26节点-Deal-{today}.csv'
    result = process_csv_file(csv_file_path)
    print(f"中泰XTP实盘_26节点: {result}")

    csv_file_path = rf'C:\Users\Top\Desktop\九章量化\北京德外大街-Deal-{today}.csv'
    result = process_csv_file(csv_file_path)
    print(f"北京德外大街: {result}")

    csv_file_path = rf'C:\Users\Top\Desktop\九章量化\国信证券-Deal-{today}.csv'
    result = process_csv_file(csv_file_path)
    print(f"国信证券: {result}")

    # + 9000

