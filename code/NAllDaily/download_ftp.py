from ast import main
from ftplib import FTP
from datetime import datetime
from tkinter import N
import tool

def ftpDownloadAFile(AFtp, remote_file_path, local_file_path):
    result=0
    
    try:
        # 打开本地文件准备写入        
        with open(local_file_path, 'wb') as local_file:
        
            # 定义一个回调函数，用于处理下载的数据块
        
            def callback(data):
        
                local_file.write(data)  # 写入数据块到文件
            
            # 下载文件，使用RETR命令
        
            AFtp.retrbinary('RETR ' + remote_file_path, callback)
            result=1
    except Exception as E:
        print(remote_file_path + ',  ftpDownloadAFile发生错误')
        print(local_file_path)
        print(E)
        result=-1               

    return result

ip_server = 'jy.nexvivagroup.com'
AFtp=FTP()                                        
AFtp.connect(ip_server, 21212)          
print(AFtp.login("download", "Quant6688"))    
AFtp.encoding='gbk'                  
AFtp.set_pasv(True)

# FOF国君 PositionStatics
# today = datetime.today().strftime("%Y%m%d")
# today = '20250527'
# name = '九章量化'
# # 尊享2号 PositionStatics
# remote_file_path = f'/{name}/成交/Stock/PositionStatics-{today}.csv'
# local_file_path = rf'C:\Users\Top\Desktop\{name}\{name}-PositionStatics-{today}.csv'
# flag = ftpDownloadAFile(AFtp, remote_file_path, local_file_path)

# # 尊享2号 Account
# remote_file_path = f'/{name}/成交/Stock/Account-{today}.csv'
# local_file_path = rf'C:\Users\Top\Desktop\{name}\{name}-Account-{today}.csv'
# flag = ftpDownloadAFile(AFtp, remote_file_path, local_file_path)

# remote_file_path = f'/FOF国君/成交/Stock/PositionStatics-{today}.csv'
# local_file_path = rf'C:\Users\Top\Desktop\ftp\FOF国君-PositionStatics-{today}.csv'
# flag = ftpDownloadAFile(AFtp, remote_file_path, local_file_path)

# # FOF国君 Account
# remote_file_path = f'/FOF国君/成交/Stock/Account-{today}.csv'
# local_file_path = rf'C:\Users\Top\Desktop\ftp\FOF国君-Account-{today}.csv'
# flag = ftpDownloadAFile(AFtp, remote_file_path, local_file_path)

# # 九章国信 PositionStatics
# remote_file_path = f'/九章国信/成交/Stock/PositionStatics-{today}.csv'
# local_file_path = rf'C:\Users\Top\Desktop\ftp\九章国信-PositionStatics-{today}.csv'
# flag = ftpDownloadAFile(AFtp, remote_file_path, local_file_path)

# # 九章国信 Account
# remote_file_path = f'/九章国信/成交/Stock/Account-{today}.csv'
# local_file_path = rf'C:\Users\Top\Desktop\ftp\九章国信-Account-{today}.csv'
# flag = ftpDownloadAFile(AFtp, remote_file_path, local_file_path)


today = datetime.today().strftime("%Y%m%d")
# today = '20250529'
config_data = tool.read_ftp_config()
if config_data:
    for product in config_data['products']:
        product_name = product['name']
        for code in product['codes']:
            name = code['name']
            position_path = code['position_path']+f'{today}.csv'
            account_path = code['account_path']+f'{today}.csv'
            deal_path = code['deal_path']+f'{today}.csv'

            position_local_path = product['local_path']+f'{name}-PositionStatics-{today}.csv'
            account_local_path = product['local_path']+f'{name}-Account-{today}.csv'
            deal_local_path = product['local_path']+f'{name}-Deal-{today}.csv'

            print(name, position_path, position_local_path)
            print(name, account_path, account_local_path)
            print(name, deal_path, deal_local_path)
            print("\\n")
            flag = ftpDownloadAFile(AFtp, position_path, position_local_path)
            flag = ftpDownloadAFile(AFtp, account_path, account_local_path)
            flag = ftpDownloadAFile(AFtp, deal_path, deal_local_path)
