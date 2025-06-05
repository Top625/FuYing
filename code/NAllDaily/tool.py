import json
import codecs

def read_ftp_config():
    try:
        with open(r'c:\Users\Top\Desktop\FuYing\code\NAllDaily\ftp_config.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print("未找到 ftp_config.json 文件，请检查文件路径。")
    except json.JSONDecodeError:
        print("解析 ftp_config.json 文件时出错，请检查文件格式。")

def detect_encoding(file_path):
    bmgs = codecs.open(file_path, "r").encoding
    return bmgs

# 调用示例
if __name__ == "__main__":

    config_data = read_ftp_config()
    if config_data:
        print(config_data['products'])
        for product in config_data['products']:
            name = product['name']
            local_file_path = product['local_file_path']+f'-{today}.csv'
            for code in product['codes']:
                position_path = code['position_path']+f'-{today}.csv'
                account_path = code['account_path']+f'-{today}.csv'
                deal_path = code['deal_path']+f'-{today}.csv'
                print(position_path, account_path, deal_path)
                flag = ftpDownloadAFile(AFtp, position_path, local_file_path)
                flag = ftpDownloadAFile(AFtp, account_path, local_file_path)
                flag = ftpDownloadAFile(AFtp, deal_path, local_file_path)