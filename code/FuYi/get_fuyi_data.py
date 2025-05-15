import dolphindb as ddb
import pandas as pd
from datetime import datetime
import os
import fuyi_log_xlsx as log_xlsx

def get_fuyi_data(task_name, save_directory, time=None):
    """
    从 DolphinDB 服务器获取数据，并将结果保存为 Excel 文件。

    :param task_name: 任务名称
    :param save_directory: 保存数据的绝对路径
    :param time: 可选参数，指定查询的时间。如果为 None，则查询全部数据。
    :return: 包含任务名、时间、保存文件绝对路径、是否成功的元组
    """
    success = False
    # 数据库连接信息
    user = 'fuying'
    password = 'Fygqc@gtja'
    server_ip = '100.125.11.222'
    server_port = 8848

    # 连接到 DolphinDB 服务器
    s = ddb.session()
    s.connect(server_ip, server_port, user, password)

    try:
        # 确保保存目录存在
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # 根据时间动态生成查询语句
        if time:
            # 假设表中有一个时间字段为 create_date，这里需要根据实际表结构修改
            db_operation = f'''
            dbName = "dfs://ZYYX"
            tbName = "rpt_rating_adjust"
            t = loadTable(dbName, tbName)
            select * from t 
            where create_date = {time}
            and (stock_code like '4%' or stock_code like '8%' or stock_code like '9%')
            order by current_create_date   
            '''
        else:
            db_operation = '''
            dbName = "dfs://ZYYX"
            tbName = "rpt_rating_adjust"
            t = loadTable(dbName, tbName)
            select * from t 
            where stock_code like '4%'
            or stock_code like '8%'
            or stock_code like '9%'
            order by current_create_date   
            '''

        # 执行查询
        result = s.run(db_operation)

        # 将结果转换为 DataFrame
        df = pd.DataFrame(result)

        # 生成日期字符串
        today_str = datetime.now().strftime('%Y%m%d')

        # 生成文件名
        file_name = f'{task_name}_{today_str}.xlsx'
        full_file_path = os.path.join(save_directory, file_name)

        # 保存结果到 Excel 文件
        df.to_excel(full_file_path, index=False)
        print(f"数据已保存到 {full_file_path}")
        success = True

    except Exception as e:
        print(f"获取数据时出错: {e}")
    finally:
        # 关闭连接
        s.close()

    return task_name, today_str, full_file_path, success

def update_log_with_result(log_file_path, result):
    """
    使用 get_fuyi_data 的返回值更新日志表格数据。

    :param log_file_path: 日志文件的路径
    :param result: get_fuyi_data 函数的返回值，格式为 (task_name, today_str, full_file_path, success)
    """
    task_name, time, full_file_path, success = result
    # 检查是否已有记录
    status_list = log_xlsx.check_data_fetch_status(log_file_path, '数据获取是否成功')
    existing_record = [(name, t) for name, t, _ in status_list if name == task_name and t == time]
    if existing_record:
        # 更新现有记录
        log_xlsx.update_log_data(
            file_path=log_file_path,
            task_name=task_name,
            time=time,
            data_fetch_success=success,
            cloud_path=full_file_path,
            copy_success=False,
            local_path="",
            table_change_success=False,
            db_insert_success=False
        )
    else:
        # 插入新记录
        log_xlsx.insert_log_data(
            file_path=log_file_path,
            task_name=task_name,
            time=time,
            data_fetch_success=success,
            cloud_path=full_file_path,
            copy_success=False,
            local_path="",
            table_change_success=False,
            db_insert_success=False
        )

if __name__ == "__main__":
    task_name = "ZYYX"
    # 将 task_name 拼接到 save_path
    save_path = os.path.join(r'C:\Users\VM-0000H\eclipse-workspace\Test\src\Data', task_name)
    log_file_path = r'C:\Users\Top\Desktop\FuYing\code\FuYi\FuYiData\日志记录表格.xlsx'

    today = datetime.now().strftime("'%Y-%m-%d'")
    log_xlsx.insert_log_data(
        file_path=log_file_path,
        task_name=task_name,
        time=today,
        data_fetch_success=False,
        cloud_path=None,
        copy_success=False,
        local_path=None,
        table_change_success=False,
        db_insert_success=False
    )

    # 检查日志文件中数据获取失败的天数
    status_list = log_xlsx.check_data_fetch_status(log_file_path, '数据获取是否成功')
    failed_days = [time for _, time, success in status_list if not success]

    # 重新获取失败天数的数据
    for day in failed_days:
        print(f"尝试重新获取 {day} 的数据")
        result = get_fuyi_data(task_name, save_path, time=f"'{day}'")
        update_log_with_result(log_file_path, result)