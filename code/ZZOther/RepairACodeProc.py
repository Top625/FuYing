

import pypyodbc
import model_configuration as mc

def RepairACodeProc(ACode):
    # 检查 ACode 是否以 . 结尾，如果是则去掉
    if ACode.endswith('.'):
        ACode = ACode[:-1]
    # 检查 ACode 是否以 .BJ 或者 .SH 结尾，如果是则前面补充 0 到九位
    if ACode.endswith(('.BJ', '.SH', '.SZ')):
        ACode = ACode.zfill(9)
    Result = ACode

    if(len(ACode)==9):
        return Result
    elif(len(ACode)==6):
        if(Result.find('0')==0 or Result.find('3')==0 or Result.find('127')==0 or Result.find('128')==0 or Result.find('123')==0 or Result.find('159')==0):
            Result = Result + '.SZ'
        elif(Result.find('4')==0 or Result.find('8')==0 or Result.find('9')==0):
            Result = Result + '.BJ'                        
        else:            
            Result = Result + '.SH'
    else:
        Result=Result.zfill(6) + '.SZ'         
    return Result

def update_codes_in_db():
    try:
        # 建立数据库连接
        con = mc.con
        cursor = con.cursor()

        # 修改查询语句，根据 date 排序并只取前 1000 条数据
        select_query = "SELECT TOP 1000 Code FROM FinanceData..Event_GSYJ_Pool24 ORDER BY date desc"
        cursor.execute(select_query)
        rows = cursor.fetchall()

        # 遍历查询结果，调用 RepairACodeProc 函数生成新的 code 并更新数据库
        for row in rows:
            old_code = row[0]
            new_code = RepairACodeProc(old_code)
            if old_code != new_code:
                update_query = "UPDATE FinanceData..Event_GSYJ_Pool24 SET Code = ? WHERE Code = ?"
                cursor.execute(update_query, (new_code, old_code))

        # 提交事务
        con.commit()
        print("数据库中的 code 列更新完成")
    except Exception as e:
        print(f"执行数据库操作时出错: {e}")
        con.rollback()
    finally:
        # 关闭游标和连接
        if cursor:
            cursor.close()
        if con:
            con.close()

if __name__ == "__main__":
    update_codes_in_db()