import pandas as pd
from pathlib import Path
from datetime import datetime

def process_excel_file(input_path, output_path):
    """
    处理 Excel 文件，按照指定规则修改表头和列值，并保存为新文件。

    :param input_path: 输入 Excel 文件的绝对路径
    :param output_path: 输出 Excel 文件的绝对路径
    """
    # 读取 Excel 文件
    df = pd.read_excel(input_path)

    # 重命名表头
    rename_mapping = {
        'stock_code': 'Code',
        'organ_name': 'Institution',
        'current_create_date': 'Date',
        'stock_name': 'Name',
        'title': 'Title',
        'author': 'Author',
        'report_type': 'ReportType',
        'rating_adjust_mark': 'RatingChange',
        'current_gg_rating': 'Rating'
    }
    df.rename(columns=rename_mapping, inplace=True)

    # 删除指定表头
    columns_to_drop = [
        'organ_id', 'previous_create_date', 'entrytime',
        'updatetime', 'tmstamp', 'previous_gg_rating',
        'id', 'report_id'
    ]
    df.drop(columns=columns_to_drop, errors='ignore', inplace=True)

    # 调用 exchange_code 方法替换 Code 列的值
    if 'Code' in df.columns:
        df['Code'] = df['Code'].astype(str).apply(exchange_code)

    # 替换 RatingChange 列的值
    rating_change_mapping = {
        '': '首次',
        1: '维持',
        2: '调低',
        3: '调高'
    }
    if 'RatingChange' in df.columns:
        df['RatingChange'] = df['RatingChange'].map(rating_change_mapping)

    # 替换 Rating 列的值
    rating_mapping = {
        1: '卖出',
        2: '减持',
        3: '中性',
        5: '增持',
        7: '买入',
        0: '-'
    }
    if 'Rating' in df.columns:
        df['Rating'] = df['Rating'].map(rating_mapping)

    # 替换 ReporType 列的值
    report_type_mapping = {
        21: '非个股报告',
        22: '一般个股报告',
        23: '深度报告',
        24: '调研报告',
        25: '点评报告',
        26: '新股研究',
        27: '简评文章',
        28: '港股研究',
        98: '会议纪要'
    }
    if 'ReporType' in df.columns:
        df['ReporType'] = df['ReporType'].map(report_type_mapping)

    # 转换 Date 列的时间格式
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

    # 保存修改后的文件
    df.to_excel(output_path, index=False)
    print(f"已成功将修改后的内容保存到 {output_path}")

def exchange_code(input_str):
    index = input_str.find('.')
    if index != -1:
        v_tem_code = input_str[:index]
    else:
        v_tem_code = input_str

    # 根据股票代码开头判断交易所
    if v_tem_code.startswith(('60', '68')):
        exchange = 'SS'  # 上交所
    elif v_tem_code.startswith(('00', '30')):
        exchange = 'SZ'  # 深交所
    elif v_tem_code.startswith(('43', '83', '87', '92')):  # 修正此处的语法错误
        exchange = 'BJ'  # 北交所
    else:
        # 若无法判断，可根据实际情况处理，这里先默认返回原代码加未知交易所标识
        exchange = ''
    v_sql_code = (v_tem_code + "." + exchange).replace("'", "")
    return v_sql_code


if __name__ == "__main__":
    # 请根据实际情况修改输入文件路径
    current_date = datetime.now().strftime("%Y%m%d")
    # 拼接指定路径
    input_file_path = fr"E:\Data\ZYYX_BJ_{current_date}.xlsx"
    input_path = Path(input_file_path)
    # 生成输出文件路径
    output_file_path = input_path.parent / f"{input_path.stem}_changed{input_path.suffix}"

    process_excel_file(input_file_path, output_file_path)