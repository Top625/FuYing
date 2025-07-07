from ftplib import FTP

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

AFtp=FTP()                                        
ip_server = 'jy.nexvivagroup.com'
AFtp.connect(ip_server, 21212)          
print(AFtp.login("download", "Quant6688"))    
AFtp.encoding='gbk'                  
AFtp.set_pasv(True)

remote_file_path='/梅/成交/Stock/Account-20250704.csv'
local_file_path='C:/Users/Top/Desktop/张总专户/Account-20250704.csv'                                        
flag=ftpDownloadAFile(AFtp, remote_file_path, local_file_path)