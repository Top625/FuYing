import pandas as pd
import model_function as mf
import model_configuration as mc

con = mc.con
channel = mc.channel
chrome_driver = mc.chrome_driver

sql_table_name = "Event_GSYJ_Pool"


def add_data_to_db(file_path):
    """
    从指定路径的 Excel 文件读取数据，将数据中的 Code、Institution、Date 与数据库对比，
    若不同则将数据添加到数据库中，同时打印添加、未添加和错误的数据。

    :param file_path: Excel 文件的绝对路径
    """
    try:
        # 读取 Excel 文件
        df = pd.read_excel(file_path)

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
    except Exception as e:
        print(f"读取文件或执行事务时出错: {e}")
        con.rollback()
    finally:
        # 关闭游标
        if cursor:
            cursor.close()


if __name__ == "__main__":
    # 替换为实际的 Excel 文件绝对路径
    excel_file_path = r'E:\New\ZYYX_BJ1_changed.xlsx'
    add_data_to_db(excel_file_path)
    # 关闭数据库连接
    con.close()