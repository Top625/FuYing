import pandas as pd

DEFAULT_SAVE_PATH = r'C:\Users\Top\Desktop\FuYing\code\FuYi\FuYiData\日志记录表格.xlsx'

def create_log_excel(file_path=DEFAULT_SAVE_PATH):
    """
    创建一个名为“日志记录表格”的 Excel 文件，并设置表头。

    参数:
        file_path (str): 保存 Excel 文件的绝对路径。
    """
    # 定义表头
    headers = [
        "任务名", "时间", "数据获取是否成功", "云电脑数据保存路径",
        "复制到本地是否成功", "本地数据保存路径", "更改数据表格是否成功",
        "插入数据库是否成功"
    ]

    # 创建一个空的 DataFrame
    df = pd.DataFrame(columns=headers)

    # 将 DataFrame 保存到 Excel 文件
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='日志记录表格', index=False)

def insert_log_data(file_path=DEFAULT_SAVE_PATH, task_name=None, time=None, data_fetch_success=None, cloud_path=None, copy_success=None, local_path=None, table_change_success=None, db_insert_success=None):
    """
    向日志 Excel 文件中插入一条新的日志记录。

    参数:
        file_path (str): 日志 Excel 文件的绝对路径。
        task_name (str): 任务的名称。
        time (str): 任务执行的时间。
        data_fetch_success (bool): 数据获取是否成功。
        cloud_path (str): 云电脑数据保存路径。
        copy_success (bool): 复制到本地是否成功。
        local_path (str): 本地数据保存路径。
        table_change_success (bool): 更改数据表格是否成功。
        db_insert_success (bool): 插入数据库是否成功。
    """
    try:
        # 读取现有的 Excel 文件
        df = pd.read_excel(file_path, sheet_name='日志记录表格')
    except FileNotFoundError:
        # 如果文件不存在，先创建文件
        create_log_excel(file_path)
        df = pd.DataFrame(columns=[
            "任务名", "时间", "数据获取是否成功", "云电脑数据保存路径",
            "复制到本地是否成功", "本地数据保存路径", "更改数据表格是否成功",
            "插入数据库是否成功"
        ])

    # 创建新的日志记录
    new_row = {
        "任务名": task_name,
        "时间": time,
        "数据获取是否成功": data_fetch_success,
        "云电脑数据保存路径": cloud_path,
        "复制到本地是否成功": copy_success,
        "本地数据保存路径": local_path,
        "更改数据表格是否成功": table_change_success,
        "插入数据库是否成功": db_insert_success
    }

    # 将新记录添加到 DataFrame
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # 将更新后的 DataFrame 保存回 Excel 文件
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
        df.to_excel(writer, sheet_name='日志记录表格', index=False)

def check_data_fetch_status(file_path=DEFAULT_SAVE_PATH, row_name=None):
    """
    判断日志表中所有日期的数据获取是否成功。

    参数:
        file_path (str): 日志 Excel 文件的绝对路径。

    返回:
        list: 包含元组的列表，每个元组格式为 (任务名, 时间, 数据是否获取成功)
    """
    try:
        # 读取日志文件
        df = pd.read_excel(file_path, sheet_name='日志记录表格')
        result = []
        for index, row in df.iterrows():
            task_name = row["任务名"]
            time = row["时间"]
            data_fetch_success = row[row_name]
            result.append((task_name, time, data_fetch_success))
        return result
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到，请检查路径。")
        return []

def update_log_data(file_path=DEFAULT_SAVE_PATH, task_name=None, time=None, data_fetch_success=None, cloud_path=None, copy_success=None, local_path=None, table_change_success=None, db_insert_success=None):
    """
    根据任务的名称、任务执行的时间，来更新日志 Excel 文件中的其他数据。

    参数:
        file_path (str): 日志 Excel 文件的绝对路径。
        task_name (str): 任务的名称。
        time (str): 任务执行的时间。
        data_fetch_success (bool, 可选): 数据获取是否成功，默认为 None。
        cloud_path (str, 可选): 云电脑数据保存路径，默认为 None。
        copy_success (bool, 可选): 复制到本地是否成功，默认为 None。
        local_path (str, 可选): 本地数据保存路径，默认为 None。
        table_change_success (bool, 可选): 更改数据表格是否成功，默认为 None。
        db_insert_success (bool, 可选): 插入数据库是否成功，默认为 None。
    """
    try:
        # 读取现有的 Excel 文件
        df = pd.read_excel(file_path, sheet_name='日志记录表格')
        # 找到需要更新的行
        mask = (df["任务名"] == task_name) & (df["时间"] == time)
        rows_to_update = df[mask]

        if not rows_to_update.empty:
            if data_fetch_success is not None:
                df.loc[mask, "数据获取是否成功"] = data_fetch_success
            if cloud_path is not None:
                df.loc[mask, "云电脑数据保存路径"] = cloud_path
            if copy_success is not None:
                df.loc[mask, "复制到本地是否成功"] = copy_success
            if local_path is not None:
                df.loc[mask, "本地数据保存路径"] = local_path
            if table_change_success is not None:
                df.loc[mask, "更改数据表格是否成功"] = table_change_success
            if db_insert_success is not None:
                df.loc[mask, "插入数据库是否成功"] = db_insert_success

            # 将更新后的 DataFrame 保存回 Excel 文件
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
                df.to_excel(writer, sheet_name='日志记录表格', index=False)
            print("日志数据更新成功")
        else:
            print("未找到符合条件的日志记录")
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到，请检查路径。")


if __name__ == "__main__":
    # 示例：插入一条日志记录
    insert_log_data(
        task_name="示例任务",
        time="2025-04-30",
        data_fetch_success=True,
        cloud_path="cloud/path/data",
        copy_success=True,
        local_path="local/path/data", 
        table_change_success=True,
        db_insert_success=True
    )

    # 示例：检查数据获取状态
    status_list = check_data_fetch_status(row_name='复制到本地是否成功')
    print(status_list)

    # 示例：更新日志数据
    update_log_data(
        task_name="示例任务",
        time="2025-04-30",
        data_fetch_success=False,
        cloud_path="new_cloud======/path/data")
