import subprocess
import pandas as pd
import getpass
import os


def get_task_scheduler_info():
    current_user = getpass.getuser()
    try:
        result = subprocess.run(['schtasks', '/query', '/fo', 'csv', '/v'], capture_output=True, text=True, check=True)
        output = result.stdout
        lines = output.strip().split('\n')
        headers = [header.strip('"') for header in lines[0].split(',')]
        print("表头信息:", headers)

        try:
            name_index = headers.index('任务名')
            creator_index = headers.index('创建者')
            schedule_type_index = headers.index('计划类型')  # 保留计划类型索引
            start_time_index = headers.index('开始时间')  # 新增开始时间索引
            command_index = headers.index('要运行的任务')
        except ValueError as e:
            print(f"找不到所需的表头字段: {e}")
            return []

        tasks = []
        for line in lines[1:]:
            data = [item.strip('"') for item in line.split('",')]
            creator = data[creator_index]
            if current_user in creator:
                task_name = data[name_index]
                schedule_type = data[schedule_type_index]  # 计划类型
                start_time = data[start_time_index]  # 开始时间

                command = data[command_index]
                # 确保数据按表头顺序添加
                tasks.append([task_name, schedule_type, start_time, command])

        return tasks

    except subprocess.CalledProcessError as e:
        print(f"执行命令时出错: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    tasks = get_task_scheduler_info()
    if tasks:
        # 修改表头信息
        table_headers = ["任务名称", "计划类型", "开始时间", "执行的脚本/命令"]
        df = pd.DataFrame(tasks, columns=table_headers)
        save_path = r'C:\Users\Top\Desktop\FuYing\code\task_scheduler_info.xlsx'
        save_dir = os.path.dirname(save_path)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        try:
            df.to_excel(save_path, index=False)
            print(f"表格已保存到 {save_path}")
        except PermissionError:
            print(f"没有权限写入文件 {save_path}，请检查文件是否被其他程序占用或者文件夹权限设置。")