from ftplib import FTP
from datetime import datetime
import tool

def ftpDownloadAFile(AFtp, remote_file_path, local_file_path):
    result = 0
    try:
        with open(local_file_path, 'wb') as local_file:
            def callback(data):
                local_file.write(data)
            AFtp.retrbinary('RETR ' + remote_file_path, callback)
            result = 1
    except Exception as E:
        print(f"{remote_file_path}, ftpDownloadAFile发生错误")
        print(local_file_path)
        print(E)
        result = -1
    return result

def download_files():
    ip_server = 'jy.nexvivagroup.com'
    AFtp = FTP()
    AFtp.connect(ip_server, 21212)
    print(AFtp.login("download", "Quant6688"))
    AFtp.encoding = 'gbk'
    AFtp.set_pasv(True)

    today = datetime.today().strftime("%Y%m%d")
    config_data = tool.read_ftp_config()
    
    if config_data:
        for product in config_data['products']:
            for code in product['codes']:
                name = code['name']
                paths = [
                    (code['position_path'], f"{name}-PositionStatics"),
                    (code['account_path'], f"{name}-Account"),
                    (code['deal_path'], f"{name}-Deal")
                ]
                
                for remote_path, local_prefix in paths:
                    remote_file = remote_path + f'{today}.csv'
                    local_file = product['local_path'] + f'{local_prefix}-{today}.csv'
                    
                    print(f"{name}, {remote_file}, {local_file}")
                    ftpDownloadAFile(AFtp, remote_file, local_file)
                print("\n")

from datetime import datetime, timedelta

# 新增方法，从开始时间到结束时间遍历下载文件
def download_files_between_dates(start_date_str, end_date_str):
    ip_server = 'jy.nexvivagroup.com'
    AFtp = FTP()
    AFtp.connect(ip_server, 21212)
    print(AFtp.login("download", "Quant6688"))
    AFtp.encoding = 'gbk'
    AFtp.set_pasv(True)

    start_date = datetime.strptime(start_date_str, "%Y%m%d")
    end_date = datetime.strptime(end_date_str, "%Y%m%d")
    current_date = start_date

    config_data = tool.read_ftp_config()
    if config_data:
        while current_date <= end_date:
            today = current_date.strftime("%Y%m%d")
            for product in config_data['products']:
                for code in product['codes']:
                    name = code['name']
                    paths = [
                        (code['position_path'], f"{name}-PositionStatics"),
                        (code['account_path'], f"{name}-Account"),
                        (code['deal_path'], f"{name}-Deal")
                    ]

                    for remote_path, local_prefix in paths:
                        remote_file = remote_path + f'{today}.csv'
                        local_file = product['local_path'] + f'{local_prefix}-{today}.csv'

                        print(f"{name}, {remote_file}, {local_file}")
                        ftpDownloadAFile(AFtp, remote_file, local_file)
                    print("\n")
            current_date += timedelta(days=1)

if __name__ == "__main__":
    download_files()
    # download_files_between_dates("20250513", "20250619")
