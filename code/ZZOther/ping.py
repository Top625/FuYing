import shutil
import os
from datetime import datetime
import time

# 源文件的绝对路径
source_file = r'C:\Users\Top\Desktop\ping\ping.txt'
# 目标文件夹的绝对路径
destination_folder = r'C:\Users\Top\Desktop\ping'

def copy_file():
    global source_file, destination_folder
    try:
        # 检查源文件是否存在
        if not os.path.isfile(source_file):
            print(f"源文件 {source_file} 不存在。")
            return
        
        # 检查目标文件夹是否存在，如果不存在则创建
        if not os.path.isdir(destination_folder):
            os.makedirs(destination_folder)
        
        # 获取当前时间并格式化为年月日时分
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 构建目标文件的完整路径
        file_name, file_ext = os.path.splitext(os.path.basename(source_file))
        destination_file = os.path.join(destination_folder, f"{current_time}{file_ext}")
        
        # 复制文件
        shutil.copy2(source_file, destination_file)
        print(f"文件已成功复制到 {destination_file}")
    except Exception as e:
        print(f"复制文件时出错: {e}")

if __name__ == "__main__":
    while True:
        copy_file()
        # 每隔 10 分钟执行一次，10 分钟 = 600 秒
        time.sleep(60)