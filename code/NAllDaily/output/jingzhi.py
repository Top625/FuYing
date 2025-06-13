import handle_sql
import pandas as pd

def import_from_excel(file_path):
    """
    从Excel文件读取数据并插入到数据库
    :param file_path: Excel文件路径
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 检查必要的列是否存在
        if '日期' not in df.columns or '净值' not in df.columns:
            raise ValueError("Excel文件中必须包含'日期'、'基金名称'和'净值'列")
            
        # 遍历每一行数据并插入数据库
        for _, row in df.iterrows():
            handle_sql.add_net_value(
                str(row['日期']),  # 日期
                '山西证券',  # 基金名称
                round(float(row['净值']), 4),  # 净值保留4位小数
                None,  # 其他参数1
                None   # 其他参数2
            )
        
        print(f"成功导入 {len(df)} 条记录")
        
    except Exception as e:
        print(f"导入失败: {str(e)}")

# 使用示例
if __name__ == '__main__':
    excel_path = "c:\\Users\\Top\\Desktop\\山西证券资产 结果.xlsx"  # 修改为你的输出文件路径

    import_from_excel(excel_path)