# 核实委托交易与真实交易
# 暂时没用

import csv
import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']

def main():
    # 定义文件路径
    new_trade_path = r'c:\Users\Top\Desktop\FuYing\code\DailyAsset\持仓\真实成交明细.csv'
    adjustment_path = r'c:\Users\Top\Desktop\FuYing\code\DailyAsset\持仓\委托成交明细.csv'

    # 读取新成交明细数据
    with open(new_trade_path, 'r', encoding= detect_encoding(new_trade_path)) as f:
        new_trades = {
            (row['市场代码'], row['证券代码'], row['证券名称']): {
                '操作': row['操作'],
                '成交量': int(row['成交量'])
            } for row in csv.DictReader(f)
        }

    # 读取调仓明细并对比数据
    with open(adjustment_path, 'r', encoding=detect_encoding(adjustment_path)) as f:
        for row in csv.DictReader(f):
            code_parts = row['股票代码'].split('.')
            market_code = code_parts[1] if len(code_parts) == 2 else ''
            security_code = code_parts[0] if len(code_parts) == 2 else row['股票代码']
            key = (market_code, security_code, row['股票名称'])

            if key in new_trades:
                new_trade = new_trades[key]
                if row['买卖方向'] != new_trade['操作'] or int(row['股票数量']) != new_trade['成交量']:
                    print(f"市场代码: {market_code}, 证券代码: {security_code}, 证券名称: {row['股票名称']}")
                    if row['买卖方向'] != new_trade['操作']:
                        print(f"买卖方向不一致 - 调仓明细: {row['买卖方向']}, 新成交明细: {new_trade['操作']}")
                    if int(row['股票数量']) != new_trade['成交量']:
                        print(f"股票数量不一致 - 调仓明细: {row['股票数量']}, 新成交明细: {new_trade['成交量']}")
                    print("-" * 50)


if __name__ == "__main__":
    main()