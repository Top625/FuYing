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

def download_email_exl():
    # 配置邮箱信息
    EMAIL = "zhanghao@egicleasing.com"
    PASSWORD = "vVorEBOM3tSdzTcG"
    IMAP_SERVER = "imap.qiye.aliyun.com"
    IMAP_PORT = 993

    # 定义保存附件的绝对路径目录，可根据实际情况修改
    attachment_dir = r'C:\Users\Top\Desktop\email'
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
        # 修改判断逻辑，使用 in 关键字
        if '尊享2号' in file_path:
            match = re.search(r'\((.*?)\)', file_path)
            if match:
                date = match.group(1)
                df = pd.read_excel(file_path)
                row_index, col_index = np.where(df.applymap(lambda x: '单位净值：' in str(x) if pd.notna(x) else False))
                if len(row_index) > 0 and len(col_index) > 0:
                    row_index = row_index[0]
                    col_index = col_index[0]
                    next_col_index = col_index + 1
                    if next_col_index < df.shape[1]:
                        net_value = df.iloc[row_index, next_col_index]
                        handle_sql.add_net_value(date, '尊享2号', net_value, None, None)
                        handle_sql.add_net_value(date, '山西证券', 1, None, None)

        elif '九章量化' in file_path:
            # 修改正则表达式以匹配日期
            match = re.search(r'_(\d{4}-\d{2}-\d{2})\.', file_path)
            print('九章量化', match)
            if match:
                date = match.group(1)
                column_name='资产份额净值(元)'
                df = pd.read_excel(file_path)
                if column_name in df.columns:
                    column_data = df[column_name]
                    if not column_data.empty:
                        handle_sql.add_net_value(date, '九章量化', column_data.iloc[0], None, None)
                else:
                    print(f"文件 {file_path} 中 {column_name} 列数据为空，请检查文件内容。")

    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")



def deal_zunxiang(date):
    try:
        file_path = fr'C:\Users\Top\Desktop\email\基金净值信息_富赢尊享2号私募证券投资基金_({date}).xls'
        # file_path = r'C:\Users\Top\Desktop\FuYing\code\NAllDaily\基金净值信息_富赢尊享2号私募证券投资基金_(2025-06-03).xls'
        df = pd.read_excel(file_path)
        row_index, col_index = np.where(df.applymap(lambda x: '单位净值：' in str(x) if pd.notna(x) else False))
        if len(row_index) > 0 and len(col_index) > 0:
            row_index = row_index[0]
            col_index = col_index[0]
            next_col_index = col_index + 1
            if next_col_index < df.shape[1]:
                net_value = df.iloc[row_index, next_col_index]
                return net_value

        print(f"文件 {file_path} 中未找到 '单位净值：'，请检查文件结构。")
        return None
    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")
        return None

def read_jiuzhang(date):
    try:
        column_name='资产份额净值(元)'
        file_path = fr'C:\Users\Top\Desktop\email\基金净值信息_富赢尊享2号私募证券投资基金_({date}).xls'
        # file_path = r'C:\Users\Top\Desktop\FuYing\code\NAllDaily\富赢九章量化1号私募证券投资基金_SXA689_基金每日净值表_2025-06-03.xls'
        df = pd.read_excel(file_path)
        if column_name in df.columns:
            column_data = df[column_name]
            # 只返回 Series 的第一个值
            if not column_data.empty:
                return column_data.iloc[0]
            else:
                print(f"文件 {file_path} 中 {column_name} 列数据为空，请检查文件内容。")
                return None
        else:
            print(f"文件 {file_path} 中未找到名为 {column_name} 的列，请检查文件结构。")
            return None
    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")
        return None

# def main():
#     result = download_email_exl()
    # if result:
    #     today = datetime.today().strftime("%Y%m%d")
    #     date = handle_sql.select_nearest_date('Daily_NetValue', today)
    #     handle_sql.add_net_value(date, '山西证券', 1.0, None, None)

    #     zunxiang_net_value = deal_zunxiang(date)
    #     if zunxiang_net_value is not None:
    #         print(f"尊享2号 单位净值为: {zunxiang_net_value}")
    #         handle_sql.add_net_value(date, '尊享2号', zunxiang_net_value, None, None)
    #     else:
    #         print("未找到 尊享2号 单位净值信息。")
        
    #     jiuzhang_net_value = read_jiuzhang(date)
    #     if jiuzhang_net_value is not None:
    #         print(f"九章量化 单位净值为: {jiuzhang_net_value}")
    #         handle_sql.add_net_value(date, '九章量化', jiuzhang_net_value, None, None)
    #     else:
    #         print("未找到 九章量化 单位净值信息。")
    # else:
    #     print("操作失败。")


if __name__ == "__main__":
    download_email_exl()
