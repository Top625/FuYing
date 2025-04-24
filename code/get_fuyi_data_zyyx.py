import dolphindb as ddb
import pandas as pd
from datetime import datetime, timedelta
import os

# 数据库连接信息
user = 'fuying'
password = 'Fygqc@gtja'
server_ip = '100.125.11.222'
server_port = 8848

# 定义保存路径，这里复用函数中的保存路径参数逻辑
def get_flag_file_path(save_directory):
    return os.path.join(save_directory, 'first_run_flag.txt')

def get_fuyi_data(save_directory):
    """
    从 DolphinDB 服务器获取数据，第一次获取全部数据，后续获取近三天数据，
    并将结果保存为 Excel 文件，文件名包含日期信息。

    :param save_directory: 保存数据的绝对路径
    """
    FLAG_FILE = get_flag_file_path(save_directory)
    # 连接到 DolphinDB 服务器
    s = ddb.session()
    s.connect(server_ip, server_port, user, password)

    try:
        # 判断是否是第一次运行
        if not os.path.exists(FLAG_FILE):
            # 第一次运行，获取全部数据
            query = '''
            dbName = "dfs://ZYYX"
            tbName = "rpt_rating_adjust"
            t = loadTable(dbName, tbName)
            select * from t 
            where stock_code like '4%'
            or stock_code like '8%'
            or stock_code like '9%'
            order by current_create_date   
            '''
            # 确保保存目录存在
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)
            # 创建标志文件，表示已经运行过一次
            with open(FLAG_FILE, 'w') as f:
                f.write('First run completed')
        else:
            # 非第一次运行，获取近三天数据
            three_days_ago = datetime.now() - timedelta(days=3)
            # 调整日期格式为 YYYY.MM.dd
            three_days_ago_str = three_days_ago.strftime('%Y.%m.%d')
            query = f'''
            dbName = "dfs://ZYYX"
            tbName = "rpt_rating_adjust"
            t = loadTable(dbName, tbName)
            select * from t 
            where (stock_code like '4%'
            or stock_code like '8%'
            or stock_code like '9%')
            and current_create_date >= date('{three_days_ago_str}')
            order by current_create_date   
            '''

        # 执行查询
        result = s.run(query)

        # 将结果转换为 DataFrame
        df = pd.DataFrame(result)

        # 生成文件名
        today_str = datetime.now().strftime('%Y%m%d')
        file_name = f'ZYYX_BJ_{today_str}.xlsx'
        full_file_path = os.path.join(save_directory, file_name)

        # 保存结果到 Excel 文件
        df.to_excel(full_file_path, index=False)
        print(f"数据已保存到 {full_file_path}")

    except Exception as e:
        print(f"获取数据时出错: {e}")
    finally:
        # 关闭连接
        s.close()


if __name__ == "__main__":
    # 请根据实际情况修改保存路径
    save_path = r'C:\Users\VM-0000H\eclipse-workspace\Test\src\Data'
    get_fuyi_data(save_path)