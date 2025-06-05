import model_configuration as mc

# 从 add_fuyi_sql.py 复用数据库连接逻辑
con = mc.con

# 检查数据库连接是否成功
if con is None:
    print("数据库连接失败，请检查配置。")
else:
    print("数据库连接成功。")

def change_bj_codes(database_array):
    try:
        for db in database_array:
            # 读取 HQData..BJStockChange 数据库中 status=1 的 OldCode 和 NewCode
            select_query = f"""
            SELECT OldCode, NewCode
            FROM {db}..BJStockChange
            WHERE status = 1
            """
            cursor = con.cursor()
            cursor.execute(select_query)
            code_mapping = cursor.fetchall()
            print(f"从 {db} 获取到的代码映射数量: {len(code_mapping)}")

            # 获取 FinanceData..AShare_StockInfo 表中 Code 以 %BJ 结尾的记录
            get_codes_query = f"""
            SELECT Code
            FROM {db}..AShare_StockInfo
            WHERE Code LIKE '%BJ'
            """
            cursor.execute(get_codes_query)
            target_codes = cursor.fetchall()
            # 将查询结果转换为一维列表，方便后续检查
            target_code_list = [code[0] for code in target_codes]
            print(f"从 {db} 获取到的目标代码: {target_code_list}")

            # 遍历映射关系并更新目标表
            update_count = 0
            for old_code, new_code in code_mapping:
                # 检查旧代码是否在目标代码列表中
                if old_code in target_code_list:
                    update_query = f"""
                    UPDATE {db}..AShare_Account
                    SET Code = '{new_code}'
                    WHERE Code = '{old_code}' 
                    """
                    print(f"尝试更新 {db}: 旧代码 {old_code}, 新代码 {new_code}")
                    print(f"执行的 SQL 语句: {update_query}")
                    cursor.execute(update_query)
                    update_count += cursor.rowcount  # 记录更新的行数
                else:
                    print(f"旧代码 {old_code} 不在 {db} 的目标代码列表中，跳过更新。")

            # 提交事务
            con.commit()
            print(f"{db} 北交所代码更新完成，共更新 {update_count} 条记录。")
    except Exception as e:
        print(f"执行代码更新时出错: {e}")
        con.rollback()
    finally:
        # 关闭游标
        if cursor:
            cursor.close()

if __name__ == "__main__":
    # 定义要更新的数据库数组
    databases = [
        "FinanceData..AShare_StockInfo",
        "FinanceData..AShare_Account",
        "FinanceData..AShare_PriceDaily",
        "FinanceData..Web_AnnounceIndex",
        "FinanceData..Wind_GQJL_Pool",
        "FinanceData..Event_GSYJ_Pool",
        "FinanceData..Wind_DXZF_Pool",
        "FinanceData..Event_LHB_Pool",
        "FinanceData..Event_DZJY_Pool",
        "FinanceData..Event_JGDYTJ_Pool",
        "FinanceData..Event_DailyNews_Pool",
        "FinanceData..Event_YJYG_Pool",
        "FinanceData..Event_YYPLSJ_Pool",
        "HQData..HisStockShareInfo"
    ]
    change_bj_codes(databases)
    # 关闭数据库连接
    con.close()