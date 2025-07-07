import json
import requests
import pandas as pd
import os
import time
import random
import sql

# 请求 URL
base_url = 'https://www.bse.cn/djgCgbdController/getDjgCgbdList.do'

# 请求头
headers = {
    'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': 'Hm_lvt_ef6193a308904a92936b38108b93bd7f=1751364678; HMACCOUNT=F028D30F8E71B857; Hm_lpvt_ef6193a308904a92936b38108b93bd7f=1751437751',
    'Host': 'www.bse.cn',
    'Origin': 'https://www.bse.cn',
    'Referer': 'https://www.bse.cn/disclosure/djg_sharehold_change.html',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}

def fetch_data(page_no=0, save_path=None):
    # 构建参数
    data = {
        'page': str(page_no),
        'stockCode': '',
        'djgName': '',
        'startTime': '2022-01-01',
        'endTime': '2025-06-30',
        'sortfield': 'bean.change_date desc, bean.stock_code asc, bean.change_amount desc, bean.price',
        'sorttype': 'desc',
        'ssgs': '1'
    }
    
    try:
        # 发送 POST 请求
        response = requests.post(base_url, headers=headers, data=data)
        # 移除 JSONP 回调函数（根据示例请求推测）
        text = response.text
        # 移除 null( 前缀和末尾的 )
        if text.startswith('null('):
            text = text[5:].rstrip(')')
        # 检查响应内容是否为空
        if not text:
            print('响应内容为空，无法解析')
            return
        # 解析 JSON 数据
        data = json.loads(text)
        print('data', data)
        # 只获取 result.content 字段里的数据
        if 'result' in data[0] and 'content' in data[0]['result']:
            df = pd.DataFrame(data[0]['result']['content'])
            
            # 判断文件是否存在，决定是写入还是追加数据
            file_exists = os.path.exists(save_path)
            df.to_csv(save_path, mode='a' if file_exists else 'w', index=False, header=not file_exists)
            print(f'数据已成功保存到 {save_path}')
            
            # 重命名列名，根据实际响应数据修改列名映射
            df = df.rename(columns={
                'stockCode': 'Code', 'stockName': 'Name', 'djgName': 'ManagerName', 'duty': 'Position',
                'changeDate': 'ChangeDate', 'createTime': 'NoticeDate', 'changeAmount': 'ChangeNum', 
                'newAmount': 'ChangedNum', 'reason': 'ChangeReason', 'price': 'AvgPrice'
            })
            df = df[['Code', 'Name', 'ManagerName', 'Position', 'ChangeDate', 'NoticeDate', 'ChangeNum', 'ChangedNum', 'ChangeReason', 'AvgPrice']]
            # 将 ChangeNum 和 ChangedNum 从万单位转换为 1 单位
            df['ChangeNum'] = df['ChangeNum'] * 10000
            df['ChangedNum'] = df['ChangedNum'] * 10000
            df['Code'] = df['Code'].astype(str) + '.BJ'
            # 将数值列格式化为字符串，避免科学计数法
            df['ChangeNum'] = df['ChangeNum'].map('{:.0f}'.format)
            df['ChangedNum'] = df['ChangedNum'].map('{:.0f}'.format)
            print(df)
            sql.df_to_sql(df, 'FinanceData..Share_Hold_Change')
        else:
            print('响应中未找到 result 或 content 字段')
    except json.JSONDecodeError as e:
        print(f'JSON 解析错误: {e}')
    except Exception as e:
        print(f'处理数据时发生错误: {e}')

if __name__ == '__main__':
    save_path = 'C:/Users/Top/Desktop/高管公告/北京.csv'
    for page in range(52):
        print('page', page)
        fetch_data(page_no=page, save_path=save_path)
        # 随机暂停 0 - 2 秒
        time.sleep(random.uniform(0, 5))