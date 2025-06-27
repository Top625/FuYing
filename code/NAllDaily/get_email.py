import imaplib
import email
from email.header import decode_header
import socket
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import handle_sql
import re
import tool

def download_email_exl():
    # 配置邮箱信息
    EMAIL = "zhanghao@egicleasing.com"
    PASSWORD = "vVorEBOM3tSdzTcG"
    IMAP_SERVER = "imap.qiye.aliyun.com"
    IMAP_PORT = 993

    # 定义保存附件的绝对路径目录，可根据实际情况修改
    config_data = tool. read_ftp_config()
    attachment_dir = config_data['email_path']
    if not os.path.exists(attachment_dir):
        os.makedirs(attachment_dir)

    today = datetime.today().strftime("%d-%b-%Y")
    tomorrow = (datetime.today() - timedelta(days=-1)).strftime("%d-%b-%Y")

    try:
        # 连接 IMAP 服务器，设置超时时间为 10 秒，并指定端口
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, port=IMAP_PORT, timeout=10)
        # 尝试登录邮箱
        mail.login(EMAIL, PASSWORD)
        mail.select("INBOX")  # 选择收件箱

        status, messages = mail.search(None, f'(SINCE "{today}" BEFORE "{tomorrow}")')
        if status == "OK":
            for msg_id in messages[0].split():
                status, data = mail.fetch(msg_id, "(RFC822)")  # 获取原始邮件
                if status == "OK":
                    raw_email = data[0][1]
                    email_message = email.message_from_bytes(raw_email)

                    for part in email_message.walk():
                        if part.get_content_maintype() == 'multipart':
                            continue
                        if part.get('Content-Disposition') is None:
                            continue

                        filename = part.get_filename()
                        if filename:
                            # 处理文件名编码
                            filename_parts = decode_header(filename)
                            decoded_filename = ""
                            for part_name, encoding in filename_parts:
                                if isinstance(part_name, bytes):
                                    try:
                                        if encoding:
                                            decoded_filename += part_name.decode(encoding)
                                        else:
                                            decoded_filename += part_name.decode('utf-8', errors='replace')
                                    except UnicodeDecodeError:
                                        decoded_filename += str(part_name)
                                else:
                                    decoded_filename += part_name

                            # 检查是否为 Excel 文件
                            if decoded_filename.lower().endswith(('.xlsx', '.xls')):
                                save_path = os.path.join(attachment_dir, decoded_filename)
                                with open(save_path, 'wb') as f:
                                    f.write(part.get_payload(decode=True))
                                print(f"已保存附件: {save_path}")

                                deal_net_value(save_path)
        return True
    except imaplib.IMAP4.error as e:
        print(f"登录失败: {e}，请检查邮箱账号、密码、IMAP 服务设置。")
        return False
    except socket.timeout:
        print("连接 IMAP 服务器超时，请检查服务器地址和网络连接。")
        return False
    except TimeoutError:
        print("连接 IMAP 服务器超时，请检查服务器地址和网络连接。")
        return False
    finally:
        if 'mail' in locals():
            mail.logout()

def deal_net_value(file_path):
    try:
        if '尊享2号' in file_path:
            match = re.search(r'\((.*?)\)', file_path)
            if match:
                date = match.group(1)
                df = pd.read_excel(file_path)

                def find_value(df, keyword):
                    row_index, col_index = np.where(df.applymap(lambda x: keyword in str(x) if pd.notna(x) else False))
                    if len(row_index) > 0 and len(col_index) > 0:
                        row_index = row_index[0]
                        col_index = col_index[0]
                        next_col_index = col_index + 1
                        if next_col_index < df.shape[1]:
                            value = df.iloc[row_index, next_col_index]
                            return value
                    return None

                total = find_value(df, '资产总值（元）：')
                net_total = find_value(df, '资产净值（元）：')
                cost = round((float(total) - float(net_total)), 2)
                net_value = find_value(df, '单位净值：')
                result = {
                    'NetAssetsE': net_total,
                    'TotalAssetsE': total,
                    'Cost': cost
                }
                print('尊享2号', date, total, net_total, cost, net_value)
                handle_sql.update_product(date, '尊享2号', result)
                handle_sql.update_net_value(date, '尊享2号', net_value, None)

        elif '九章量化' in file_path:
            # 修改正则表达式以匹配日期
            match = re.search(r'_(\d{4}-\d{2}-\d{2})\.', file_path)
            print('九章量化', match)
            if match:
                date = match.group(1)
                df = pd.read_excel(file_path)

                net_total = float(df['资产净值(元)'].iloc[0].replace(',', ''))
                total = float(df['资产总值(元)'].iloc[0].replace(',', ''))
                cost = round((float(total) - float(net_total)), 2)
                net_value = df['资产份额净值(元)'].iloc[0]
                result = {
                    'NetAssetsE': net_total,
                    'TotalAssetsE': total,
                    'Cost': cost
                }
                print('九章量化', date, net_total, total, cost, net_value)
                handle_sql.update_product(date, '九章量化', result)  
                handle_sql.update_net_value(date, '九章量化', net_value, None)

    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")

if __name__ == "__main__":
    download_email_exl()
    # path = "C:/Users/Top/Desktop/email/富赢九章量化1号私募证券投资基金_SXA689_基金每日净值表_2025-06-24.xls"  
    # path = "C:/Users/Top/Desktop/email/基金净值信息_富赢尊享2号私募证券投资基金_(2025-06-24).xls"  
    # deal_net_value(path)