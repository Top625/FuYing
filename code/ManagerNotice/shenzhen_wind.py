from WindPy import w
import pandas as pd
import sql
import os
import json
import requests

def call_wind_api(function, params, server_url='http://192.168.1.123:5888'):
    if params is None:
        params = {}
    
    # 构造请求数据
    data = {
        'function': function,
        'params': params
    }
    
    # 发送POST请求
    response = requests.post(f'{server_url}/wind_api', json=data)
    
    if response.status_code == 200:
        # 解析返回的JSON数据
        result = pd.read_json(response.text)
        return result
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return json.loads(response.text)
    

def fetch_and_save_data(startdate, enddate, save_path):

    data = call_wind_api("wset", ['majorholderdealrecord',
     f"startdate={startdate};enddate={enddate};sectorid=a001010300000000;type=announcedate;field=wind_code,announcement_date,change_start_date,change_end_date,shareholder_name,shareholder_type,direction,change_number,number_after_change,average_price"])
    print(data)

    df = pd.read_json(json.dumps(data)) if isinstance(data, dict) else pd.DataFrame(data)
    date_columns = ['announcement_date', 'change_start_date', 'change_end_date']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], unit='ms').dt.strftime('%Y-%m-%d')

    df = df.drop(columns=['Code'])
    print(df)

    # 保存到CSV文件
    file_exists = os.path.exists(save_path)
    df.to_csv(save_path, mode='a' if file_exists else 'w', index=False, header=not file_exists, encoding='utf_8_sig')
    print(f'数据已成功保存到 {save_path}')
    
    # df = pd.read_csv(save_path)
    df = df.copy()
    # 根据 direction 字段设置 change_number 的正负
    if 'direction' in df.columns and 'change_number' in df.columns:
        df.loc[df['direction'] == '减持', 'change_number'] = -df.loc[df['direction'] == '减持', 'change_number'].abs()
        df.loc[df['direction'] == '增持', 'change_number'] = df.loc[df['direction'] == '增持', 'change_number'].abs()

    df = df.rename(columns={ 
        'wind_code': 'Code', 'shareholder_name': 'ManagerName', 'announcement_date': 'NoticeDate', 
        'change_start_date': 'ChangeDate', 'change_number': 'ChangeNum', 'number_after_change': 'ChangedNum', 
        'average_price': 'AvgPrice', 'shareholder_type': 'ShareholderType'
    })

    df = df[['Code', 'ManagerName', 'ChangeDate', 'NoticeDate', 'ChangeNum', 'ChangedNum', 'AvgPrice', 'ShareholderType']]
    
    date_columns = ['ChangeDate', 'NoticeDate']
    for col in date_columns: 
        if col in df.columns: 
            df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d') 
    df['ChangeNum'] = df['ChangeNum'].astype(float) * 10000
    df['ChangedNum'] = df['ChangedNum'].astype(float) * 10000
    
    # 对数值列进行四舍五入，保留 2 位小数
    numeric_columns = ['ChangeNum', 'ChangedNum', 'AvgPrice']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: '{:.2f}'.format(x) if pd.notna(x) and isinstance(x, (int, float)) else x)
    
    df = df.where(pd.notna(df), '')
    print(df)
    sql.df_to_sql(df, 'FinanceData..Share_Hold_Change')


if __name__ == '__main__':
    startdate = '2000-01-01'
    enddate = '2000-12-31'
    save_path = 'C:/Users/Top/Desktop/高管公告/深圳_wind_17.csv'  
    fetch_and_save_data(startdate, enddate, save_path)

    # data = call_wind_api("wset", ['majorholderdealrecord',
    #  f"startdate={startdate};enddate={enddate};sectorid=a001010300000000;type=announcedate;field=wind_code,announcement_date,change_start_date,change_end_date,shareholder_name,shareholder_type,direction,change_number,number_after_change,average_price"])
    # print(data)
