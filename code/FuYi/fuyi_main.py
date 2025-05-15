import configparser
import os

# 根据任务名 获取数据库 操作
# 1、一个文件放在本地电脑上  读取  日志文件路径、云电脑保存路径、本地电脑路径
# 2、参数 任务名，根据任务名做相应操作
# 3、任务名 到 swl语句  每天时间
# 4、 任务名  处理表格 
# 5、任务名 处理sql

def read_config():
    config = configparser.ConfigParser()
    config_file_path = r'C:\Users\Top\Desktop\FuYing\code\FuYi\config.ini'
    config.read(config_file_path)
    if 'Paths' in config:
        log_file_path = config['Paths'].get('log_file_path')
        cloud_data_path = config['Paths'].get('cloud_data_path')
        local_data_path = config['Paths'].get('local_data_path')
        print(log_file_path, cloud_data_path, local_data_path)  

# 示例使用
if __name__ == "__main__":
    read_config()