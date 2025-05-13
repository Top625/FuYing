import pandas as pd
import numpy as np
import model_function as mf
import model_configuration as mc
from datetime import datetime
import fuyi_log_xlsx as log_xlsx

# 从 tong_hua_shun.py 复制过来的数据库连接逻辑
con = mc.con
channel = mc.channel
chrome_driver = mc.chrome_driver

sql_table_name = "Event_GSYJ_Pool_Top_test"


def add_data_to_db(file_path):
    """
    从指定路径的 Excel 文件读取数据，将数据中的 Code、Institution、Date 与数据库对比，
    若不同则将数据添加到数据库中，同时打印添加、未添加和错误的数据。

    :param file_path: Excel 文件的绝对路径
    """
    try:
        # 读取 Excel 文件
        df = pd.read_excel(file_path)
        
        # 数据预处理：将 Code 列转换为字符串类型
        df['Code'] = df['Code'].astype(str)
        
        # 转换 Date 列为 datetime 类型
        df['Date'] = pd.to_datetime(df['Date'])
        # 将 Date 列转换为 'YYYY-MM-DD' 格式的字符串
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

        # 检查是否有 Link 列，如果有则填充默认值
        if 'Link' in df.columns:
            df['Link'] = df['Link'].fillna('-')
        else:
            # 如果没有 Link 列，添加并填充默认值
            df['Link'] = None

        # 处理 RatingChange 列的 nan 值
        if 'RatingChange' in df.columns:
            df['RatingChange'] = df['RatingChange'].fillna('')

        cursor = con.cursor()
        for index, row in df.iterrows():
            try:
                # 检查数据库中是否存在相同记录
                check_query = f"""
                SELECT COUNT(*) FROM {sql_table_name}
                WHERE Code = ? AND Institution = ? AND Date = ?
                """
                cursor.execute(check_query, (row['Code'], row['Institution'], row['Date']))
                result = cursor.fetchone()

                if result[0] == 0:
                    # 如果不存在相同记录，则插入数据
                    columns = ', '.join(df.columns)
                    placeholders = ', '.join(['?'] * len(df.columns))
                    insert_query = f"INSERT INTO {sql_table_name} ({columns}) VALUES ({placeholders})"
                    cursor.execute(insert_query, tuple(row))
                    print(f"添加的数据: {dict(row)}")
                else:
                    print(f"未添加的数据（已存在）: {dict(row)}")
            except Exception as e:
                print(f"处理数据 {dict(row)} 时出错: {e}")

        # 提交事务
        con.commit()
        print("数据添加完成")
        return True
    except Exception as e:
        print(f"读取文件或执行事务时出错: {e}")
        con.rollback()
        return False
    finally:
        # 关闭游标
        if cursor:
            cursor.close()


def retry_failed_db_insert(log_file_path):
    status_list = log_xlsx.check_data_fetch_status(log_file_path, '插入数据库是否成功')
    df = pd.read_excel(log_file_path, sheet_name='日志记录表格')
    for task_name, time, db_insert_success in status_list:
        if not db_insert_success:
            mask = (df["任务名"] == task_name) & (df["时间"] == time)
            local_path = df.loc[mask, "本地数据保存路径"].values[0]
            success = add_data_to_db(local_path)
            if success:
                log_xlsx.update_log_data(
                    file_path=log_file_path,
                    task_name=task_name,
                    time=time,
                    db_insert_success=True
                )


if __name__ == "__main__":
    # 替换为实际的 Excel 文件绝对路径
    current_date = datetime.now().strftime("%Y%m%d")
    # 拼接指定路径
    input_file_path = fr"E:\Data\ZYYX_BJ_{current_date}_changed.xlsx"
    print(input_file_path)
    add_data_to_db(input_file_path)

    log_file_path = r'C:\Users\Top\Desktop\FuYing\code\FuYi\FuYiData\日志记录表格.xlsx'
    retry_failed_db_insert(log_file_path)

    # 关闭数据库连接
    con.close()