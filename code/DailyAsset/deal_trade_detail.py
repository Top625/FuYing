# 真实成交明细记录 整理成 真实成交明细.csv

import csv
from collections import defaultdict
import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']

def get_value(row, index, default):
    """
    根据索引从行数据中获取值，如果索引不存在则返回默认值
    :param row: 行数据列表
    :param index: 索引
    :param default: 默认值
    :return: 对应的值或默认值
    """
    return row[index] if index is not None else default


def process_trade_data(input_file_path):
    result = defaultdict(lambda: {'操作': '', '成交量': 0, '成交额': 0, '手续费': 0})

    with open(input_file_path, 'r', encoding=detect_encoding(input_file_path)) as file:
        reader = csv.reader(file)
        headers = next(reader)

        # 查找各字段在表头中的索引
        field_names = ['市场代码', '证券代码', '证券名称', 'offsetFlag', '成交量', '成交额', '手续费']
        indices = [headers.index(name) if name in headers else None for name in field_names]

        for row in reader:
            market_code = get_value(row, indices[0], "")
            security_code = get_value(row, indices[1], "")
            security_name = get_value(row, indices[2], "")
            operation = int(get_value(row, indices[3], 0))
            volume = int(get_value(row, indices[4], 0))
            amount = float(get_value(row, indices[5], 0))
            fee = float(get_value(row, indices[6], 0))

            # 根据操作代码调整成交量的正负
            if operation == 48:
                signed_volume = volume
            elif operation == 49:
                signed_volume = -volume
            else:
                signed_volume = 0

            key = (market_code, security_code, security_name)

            # 累加临时成交量、成交额和手续费
            result[key]['_temp_volume'] = result[key].get('_temp_volume', 0) + signed_volume
            result[key]['成交额'] += amount
            result[key]['手续费'] += fee

    # 根据最终临时成交量确定操作类型，并设置成交量为绝对值
    for key in result:
        temp_volume = result[key]['_temp_volume']
        if temp_volume > 0:
            result[key]['操作'] = '买入'
        elif temp_volume < 0:
            result[key]['操作'] = '卖出'
        else:
            result[key]['操作'] = '未知'
        
        # 设置成交量为绝对值
        result[key]['成交量'] = abs(temp_volume)
        # 删除临时成交量字段
        del result[key]['_temp_volume']

    return result


def save_result_to_csv(result, output_file_path):
    """
    将处理后的交易数据结果保存到 CSV 文件中。

    :param result: 处理后的交易数据结果字典
    :param output_file_path: 输出 CSV 文件的路径
    """
    with open(output_file_path, 'w', newline='', encoding=detect_encoding(output_file_path)) as file:
        writer = csv.writer(file)
        writer.writerow(["市场代码", "证券代码", "证券名称", "操作", "成交量", "成交额", "手续费"])
        for (market_code, security_code, security_name), data in result.items():
            writer.writerow([market_code, security_code, security_name, data['操作'], data['成交量'], data['成交额'], data['手续费']])


def main():
    input_file_path = r'c:\Users\Top\Desktop\FuYing\code\DailyAsset\持仓\成交明细记录.csv'
    output_file_path = r'c:\Users\Top\Desktop\FuYing\code\DailyAsset\持仓\真实成交明细.csv'
    result = process_trade_data(input_file_path)
    save_result_to_csv(result, output_file_path)


if __name__ == "__main__":
    main()