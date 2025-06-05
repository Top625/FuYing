# 1、读取账号数据
# 2、读取产品数据

from datetime import datetime
import pandas as pd
import handle_sql
import tool
import os

def export_daily_result():
    today = datetime.today().strftime("%Y%m%d")
    today_str = '20250604'
    config_data = tool.read_ftp_config()

    product_data = []
    account_data = []

    if config_data:
        for product in config_data['products']:
            product_name = product['name']
            product_sql = handle_sql.select_product(today_str, product_name)
            print('产品', product_sql)
            product_data.extend(product_sql)

            fund_accounts = []
            for code in product['codes']:
                fund_accounts += code['fund_account']

            accounts = []
            for fund_account in fund_accounts:
                accounts += handle_sql.select_account(today_str, fund_account)

            print('账号', accounts)
            print('\n')
            account_data.extend(accounts)

    # 将产品和账号数据转换为 DataFrame
    product_df = pd.DataFrame(product_data)
    account_df = pd.DataFrame(account_data)

    # 合并产品和账号 DataFrame
    combined_df = pd.concat([product_df, account_df], ignore_index=True)

    # 定义保存文件的绝对路径和文件名
    output_dir = r'C:\Users\Top\Desktop\FuYing\code\NAllDaily\output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    excel_file_name = f'{today}.xlsx'
    excel_file_path = os.path.join(output_dir, excel_file_name)

    # 将数据保存到 Excel 文件中
    combined_df.to_excel(excel_file_path, index=False)
    print(f"数据已成功保存到 {excel_file_path} 文件中。")

if __name__ == "__main__":
    export_daily_result()
