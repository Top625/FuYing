import pandas as pd


def process_excel(input_path, output_path):
    # 读取 Excel 文件
    df = pd.read_excel(input_path)

    # 提取对手方户名中'股份有限公司'前面的名称
    df['对手方户名'] = df['对手方户名'].apply(lambda x: x.split('股份有限公司')[0] if '股份有限公司' in x else x)

    # 根据摘要调整划款金额的正负
    def adjust_amount(row):
        if '证券转银行' in row['摘要']:
            return -abs(row['划款金额'])
        elif '银行转证券' in row['摘要']:
            return abs(row['划款金额'])
        else:
            return row['划款金额']

    df['划款金额'] = df.apply(adjust_amount, axis=1)

    # 保存处理后的 DataFrame 到新的 Excel 文件
    df.to_excel(output_path, index=False)

if __name__ == '__main__':
    # 请替换为实际的输入和输出路径
    input_file_path = 'C:\Users\Top\Desktop\九章\250619.xls'
    output_file_path = 'C:\Users\Top\Desktop\九章\2506191.xls'
    process_excel(input_file_path, output_file_path)