import json
import requests
import pandas as pd
import os
import time
import random
import sql
import send_as_bot

# 基础 URL
base_url = 'https://www.szse.cn/api/report/ShowReport/data'

# 请求头
headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Cookie': 'JSESSIONID=911c4e56-db8d-4e88-953a-decf3c2ee644',
    'Host': 'www.szse.cn',
    'Referer': 'https://www.szse.cn/disclosure/supervision/change/index.html',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'X-Request-Type': 'ajax',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': 'Windows'
}

def fetch_data(begin_date, end_date, page_no=1, save_path=None):
    params = {
        'SHOWTYPE': 'JSON',
        'CATALOGID': '1801_cxda',
        'TABKEY': 'tab1',
        'txtStart': begin_date,
        'txtEnd': end_date,
        'random': random.random(),
        'page': str(page_no),
        'pageSize': '20'
    }

    try:
        # 发送请求
        response = requests.get(base_url, headers=headers, params=params)
        # 检查响应内容是否为空
        if response.status_code != 200 or not response.text:
            print('响应内容为空，无法解析')
            send_as_bot.send_group_message("浩", False, {page}, response.text)
            return
        # 解析JSON数据
        data = response.json()
        # 提取 data 字段的数据创建 DataFrame
        print(data[0]['data'])
        df = pd.DataFrame(data[0]['data']) 
        # 判断文件是否存在，决定是写入还是追加数据
        file_exists = os.path.exists(save_path)
        df.to_csv(save_path, mode='a' if file_exists else 'w', index=False, header=not file_exists)
        print(f'数据已成功保存到 {save_path}')
        
        # 重命名列名，需根据实际情况修改映射关系
        df = df.rename(columns={
            'zqdm': 'Code', 'zqjc': 'Name', 'ggxm': 'ManagerName', 'zw': 'Position',
            'jyrq': 'ChangeDate', 'bdgs': 'ChangeNum', 'cgzs': 'ChangedNum',
            'bdyy': 'ChangeReason', 'bdjj': 'AvgPrice'
        })
        df = df[['Code', 'Name', 'ManagerName', 'Position', 'ChangeDate', 'ChangeNum', 'ChangedNum', 'ChangeReason', 'AvgPrice']]
        df['Code'] = df['Code'].astype(str) + '.SZ'
        df['ChangeNum'] = (df['ChangeNum'].str.replace(',', '').astype(float) * 10000).round(2).astype(str)
        df['ChangedNum'] = (df['ChangedNum'].str.replace(',', '').astype(float) * 10000).round(2).astype(str)
        print(df)
        sql.df_to_sql(df, 'FinanceData..Share_Hold_Change')
    except json.JSONDecodeError as e:
        print(f'JSON解析错误: {e}')
    except Exception as e:
        print(f'处理数据时发生错误: {e}')

if __name__ == '__main__':
    save_path = 'C:/Users/Top/Desktop/高管公告/深圳.csv'
    # 分页获取数据，需根据实际情况修改页码范围
    for page in range(1, 221):
        # fetch_data(page_no=page, save_path=save_path)
        fetch_data(begin_date='2024-01-01', end_date='2024-12-31', page_no=page, save_path=save_path)
        # 随机暂停0-2秒
        time.sleep(random.uniform(0, 30))