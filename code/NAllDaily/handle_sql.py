from unittest import result
from numpy import add
import model_configuration as mc
from datetime import datetime

con = mc.con

# 产品数据库 操作
def select_product(date, product):
    try:
        # 构建查询语句
        query = f"SELECT * FROM {'Daily_Product'} WHERE date = '{date}' AND product = '{product}'"
        # 执行查询
        cursor = con.cursor()
        cursor.execute(query)
        # 获取列名
        column_names = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        # 将结果转换为字典列表
        dict_results = []
        for row in results:
            row_dict = dict(zip(column_names, row))
            dict_results.append(row_dict)
        return dict_results
    except Exception as e:
        print(f"执行查询时出错: {e}")
        return []

def get_previous_trading_day(date):
    try:
        # 使用当前日期动态生成查询语句
        query  = f"select FinanceData.dbo.func_dateaddstockday('{date}', -1, 'D')"
        cursor = con.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        if results:
            # 获取日期值
            previous_date = results[0][0]
            if isinstance(previous_date, datetime):
                return previous_date.strftime('%Y%m%d')
            else:
                return str(previous_date).replace('-', '').replace('/', '')[:8]
        else:
            return None
    except Exception as e:
        print(f"查询最近日期时出错: {e}")
        return None

# 查询离指定日期最近的一个日期
def select_nearest_date(table_name, target_date_str):
    try:
        # 将输入的日期字符串转换为 datetime 对象
        target_date = datetime.strptime(target_date_str, '%Y%m%d')
        # 构建查询语句，获取所有日期
        query = f"SELECT DISTINCT date FROM {table_name}"
        cursor = con.cursor()
        cursor.execute(query)
        dates = cursor.fetchall()
        # 转换日期格式并计算与目标日期的差值
        date_diffs = []
        for date in dates:
            try:
                # 修改日期解析格式为 '%Y-%m-%d'
                db_date = datetime.strptime(date[0], '%Y-%m-%d')
                diff = abs((target_date - db_date).days)
                date_diffs.append((date[0], diff))
            except ValueError:
                print(f"日期格式错误: {date[0]}")
        # 找出差值最小的日期
        if date_diffs:
            nearest_date = min(date_diffs, key=lambda x: x[1])[0]
            return nearest_date
        else:
            return None
    except Exception as e:
        print(f"查询最近日期时出错: {e}")
        return None

# add_account 操作
def add_product(param_mapping):
    columns = []
    values = []

    for col, val in param_mapping.items():
        if val is not None:
            columns.append(col)
            if isinstance(val, str):
                values.append(f"'{val}'")
            else:
                values.append(str(val))

    if not columns or not values:
        print("至少需要提供一个有效的插入值")
        return False

    try:
        query = f"INSERT INTO Daily_Product ({', '.join(columns)}) VALUES ({', '.join(values)})"
        cursor = con.cursor()
        cursor.execute(query)
        con.commit()
        return True
    except Exception as e:
        print(f"添加账号数据时出错: {e}")
        return False

# 账号数据库 操作
def select_account(date, fund_account):
    try:
        # 构建查询语句
        query = f"SELECT * FROM {'Daily_Account'} WHERE date = '{date}' AND FundAccount = '{fund_account}'"
        # 执行查询
        cursor = con.cursor()
        cursor.execute(query)
        # 获取列名
        column_names = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        # 将结果转换为字典列表
        dict_results = []
        for row in results:
            row_dict = dict(zip(column_names, row))
            dict_results.append(row_dict)
        return dict_results
    except Exception as e:
        print(f"执行查询时出错: {e}")
        return []

# add_account 操作
def add_account(param_mapping):
    columns = []
    values = []

    for col, val in param_mapping.items():
        if val is not None:
            columns.append(col)
            if isinstance(val, str):
                values.append(f"'{val}'")
            else:
                values.append(str(val))

    if not columns or not values:
        print("至少需要提供一个有效的插入值")
        return False

    try:
        query = f"INSERT INTO Daily_Account ({', '.join(columns)}) VALUES ({', '.join(values)})"
        cursor = con.cursor()
        cursor.execute(query)
        con.commit()
        return True
    except Exception as e:
        print(f"添加账号数据时出错: {e}")
        return False

# 净值表格 操作
def select_net_value(date, product):
    try:
        # 构建查询语句
        query = f"SELECT * FROM {'Daily_NetValue'} WHERE date = '{date}' AND product = '{product}'"
        # 执行查询
        cursor = con.cursor()
        cursor.execute(query)
        # 获取列名
        column_names = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        # 将结果转换为字典列表
        dict_results = []
        for row in results:
            row_dict = dict(zip(column_names, row))
            dict_results.append(row_dict)
        return dict_results
    except Exception as e:
        print(f"执行查询时出错: {e}")
        return []

def add_net_value(date, product, net_value=None, net_value_sum=None, net_value_est=None):
    param_mapping = {
        'Date': date,
        'Product': product,
        'NetValue': net_value,
        'NetValueSum': net_value_sum,
        'NetValueEst': net_value_est
    }
    columns = []
    values = []

    for col, val in param_mapping.items():
        if val is not None:
            columns.append(col)
            if isinstance(val, str):
                values.append(f"'{val}'")
            else:
                values.append(str(val))

    if not columns or not values:
        print("至少需要提供一个有效的插入值")
        return False

    try:
        query = f"INSERT INTO Daily_NetValue ({', '.join(columns)}) VALUES ({', '.join(values)})"
        cursor = con.cursor()
        cursor.execute(query)
        con.commit()
        return True
    except Exception as e:
        print(f"添加净值数据时出错: {e}")
        return False

def update_net_value(date, product, new_net_value=None, net_value_sum=None, net_value_est=None):
    update_clauses = []
    if new_net_value is not None:
        update_clauses.append(f"NetValue = {new_net_value}")
    if net_value_sum is not None:
        update_clauses.append(f"NetValueSum = {net_value_sum}")
    if net_value_est is not None:
        update_clauses.append(f"NetValueEst = {net_value_est}")

    if not update_clauses:
        print("至少需要提供一个有效的更新值")
        return False

    try:
        query = f"UPDATE Daily_NetValue SET {', '.join(update_clauses)} WHERE date = '{date}' AND product = '{product}'"
        cursor = con.cursor()
        cursor.execute(query)
        con.commit()
        return True
    except Exception as e:
        print(f"修改净值数据时出错: {e}")
        return False

# 申购赎回 操作
def select_SGSH_amount(date, fund_account):
    try:
        # 构建查询语句
        query = f"SELECT * FROM {'Daily_SGSH'} WHERE date = '{date}' AND fundaccount = '{fund_account}'"
        # 执行查询
        cursor = con.cursor()
        cursor.execute(query)
        # 获取列名
        column_names = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        # 将结果转换为字典列表
        dict_results = []
        for row in results:
            row_dict = dict(zip(column_names, row))
            dict_results.append(row_dict)
        return dict_results
    except Exception as e:
        print(f"执行查询时出错: {e}")
        return []

if __name__ == "__main__":
    date = '20250605'
    print(get_previous_trading_day(date))

    # print(select_nearest_date('Daily_Product', date)) 
    # product = '尊享2号'
    # account = '国信'
    # fund_account = '109157019055'
    # print(select_account(date, fund_account))
    # print(add_net_value(date, '九章量化', 1.0415, None, 1.042))
    # print(add_net_value(date, '山西证券', 1, None, 1))
    # print(add_net_value(date, '量化九章', 1.0415, None, 1.042))

    # print(update_net_value(date, product, 1.1, 1.2, 1.3))
    # print(select_SGSH_amount(date, product, account))

    result = {
        'Date': '20250603', 
        'FundAccount': '109157019055', 
        'Account': '中泰', 
        'Product': '尊享2号', 
        'TotalAssets':  43847334.29, 
        'MarketValue': 0, 
        'Cash': 0, 
        'Position': '0%', 
        'DailyPer': '0%', 
        'Daily': 0,
        'MonthlyPer': '0%', 
        'Monthly': 0,
        'YearlyPer':'0%', 
        'Yearly': 0,
        'TotalPer': '0%', 
        'Total': 0
        }
    # add_account(result)

    date = '2025-06-03'
    fund_account = '190900011119'
    # print(select_account(date, fund_account))
    # print(select_account(date, fund_account))

    
    # result = {
    #     'Date': '20250603', 
    #     'Product': '九章量化', 
    #     'TotalAssets':  44818677.90, 
    #     'MarketValue':  44818407.61, 
    #     'Cash':   270.29, 
    #     'Position': '100.00%', 
    #     'DailyPer': '0.94%', 
    #     'Daily': 100,
    #     'MonthlyPer': '0%', 
    #     'Monthly': 100,
    #     'YearlyPer':'0%', 
    #     'Yearly': 100,
    #     'TotalPer': '0%', 
    #     'Total': 100,
    #     'NetValueEst': 0,
    #     }
    # add_product(result)

    # date = '20250603'
    # product = '九章量化'
    # # account = '国信'
    # fund_account = '109157019055'
    # print(select_product(date, product))