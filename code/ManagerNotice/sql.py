import model_configuration as mc
import pandas as pd

con = mc.con

def df_to_sql(df, table_name):
    if df.empty:
        print('DataFrame 为空，跳过插入操作。')
        return
    
    # 保留 None 值，仅对字符串进行清理
    df = df.apply(lambda col: col.map(lambda x: str(x).replace("'", "''") if isinstance(x, str) and x is not None else x))
    
    columns = ', '.join(df.columns)
    placeholders = ', '.join(['?' for _ in df.columns])
    insert_query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
    
    try:
        cursor = con.cursor()
        for row in df.itertuples(index=False):
            cursor.execute(insert_query, row)
        con.commit()
        print(f'数据已成功插入到 {table_name} 表中。')
    except Exception as e:
        print(f'插入数据时出错: {e}')
        print(f'出错的数据: {row}')  # 打印出错的具体数据行
        con.rollback()
    finally:
        if 'cursor' in locals(): 
            cursor.close()