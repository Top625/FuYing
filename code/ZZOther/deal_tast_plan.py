import sched
import subprocess
import pandas as pd
import getpass
import os

# 定义英文星期缩写到中文星期的映射
weekday_mapping = {
    "SUN": "星期日",
    "MON": "星期一",
    "TUE": "星期二",
    "WED": "星期三",
    "THU": "星期四",
    "FRI": "星期五",
    "SAT": "星期六"
}

def get_task_scheduler_info():
    current_user = getpass.getuser()
    try:
        result = subprocess.run(['schtasks', '/query', '/fo', 'csv', '/v'], capture_output=True, text=True, check=True)
        output = result.stdout
        lines = output.strip().split('\n')
        headers = [header.strip('"') for header in lines[0].split(',')]

        try:
            name_index = headers.index('任务名')
            creator_index = headers.index('创建者')
            schedule_type_index = headers.index('计划类型')
            schedule_day_index = headers.index('天')
            start_time_index = headers.index('开始时间')
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
                schedule_type = data[schedule_type_index]
                schedule_day = data[schedule_day_index]
                # 处理可能包含多个星期缩写的情况
                days = []
                # 替换中英文逗号和空格，再分割
                split_days = schedule_day.replace('，', ',').replace(' ', '').split(',')
                for day in split_days:
                    cleaned_day = day.strip().upper()
                    if cleaned_day in weekday_mapping:
                        days.append(weekday_mapping[cleaned_day])
                    else:
                        if cleaned_day:  # 避免添加空字符串
                            days.append(day.strip())

                converted_day = ', '.join(days)
                start_time = data[start_time_index]
                command = data[command_index]

                tasks.append([task_name, schedule_type, converted_day, start_time, command])

        return tasks

    except subprocess.CalledProcessError as e:
        print(f"执行命令时出错: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    tasks = get_task_scheduler_info()
    if tasks:
        table_headers = ["任务名称", "计划类型", "天", "开始时间", "执行的脚本/命令"]
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