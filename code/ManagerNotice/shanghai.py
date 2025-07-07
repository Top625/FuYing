import json
import requests
import pandas as pd
import os
import time
import random
import sql

# 基础 URL
base_url = 'https://query.sse.com.cn/commonQuery.do'

# 请求头
headers = { 
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Cookie': 'gdp_user_id=gioenc-bea7d76a%2C163a%2C578d%2Cc5cc%2C813476293da8; ba17301551dcbaf9_gdp_session_id=0e1cf863-e97a-40e6-a465-2d9b72cebf13; ba17301551dcbaf9_gdp_session_id_sent=0e1cf863-e97a-40e6-a465-2d9b72cebf13; JSESSIONID=45FB1185D7F550F3D774DE465251CCE1; ba17301551dcbaf9_gdp_sequence_ids={%22globalKey%22:181%2C%22VISIT%22:5%2C%22PAGE%22:7%2C%22VIEW_CLICK%22:170%2C%22VIEW_CHANGE%22:2}',
    'Host': 'query.sse.com.cn',
    'Referer': 'https://www.sse.com.cn/',
    'Sec-Fetch-Dest': 'script',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': 'Windows'
}

def fetch_data(begin_date, end_date, page_no=1, begin_page=1, end_page=1, save_path=None):
    # 构建参数
    params = {
        'jsonCallBack': 'jsonpCallback98519956',
        'isPagination': 'true',
        'pageHelp.pageSize': '100',
        'pageHelp.pageNo': str(page_no),
        'pageHelp.beginPage': str(begin_page),
        'pageHelp.cacheSize': '1',
        'pageHelp.endPage': str(end_page),
        'sqlId': 'COMMON_SSE_XXPL_CXJL_SSGSGFBDQK_S',
        'COMPANY_CODE': '',
        'NAME': '',
        'BEGIN_DATE': begin_date,
        'END_DATE': end_date,
        'BOARDTYPE': '',
        '_': '1751420111940'
    }

    try:
        # 发送请求
        response = requests.get(base_url, headers=headers, params=params)
        # 移除JSONP回调函数
        text = response.text
        start_index = text.find('(')
        if start_index != -1:
            text = text[start_index + 1:].rstrip(')')
        # 检查响应内容是否为空
        if not text:
            print('响应内容为空，无法解析')
            return
        # 解析JSON数据
        data = json.loads(text)
        # 只获取data字段里的数据
        if 'pageHelp' in data and 'data' in data['pageHelp']:
            df = pd.DataFrame(data['pageHelp']['data'])
            # 判断文件是否存在，决定是写入还是追加数据
            file_exists = os.path.exists(save_path)
            df.to_csv(save_path, mode='a' if file_exists else 'w', index=False, header=not file_exists)
            print(f'数据已成功保存到 {save_path}')
            # 重命名列名，需根据实际情况修改映射关系
            df = df.rename(columns={
                'COMPANY_CODE': 'Code', 'COMPANY_ABBR': 'Name', 'NAME': 'ManagerName', 'DUTY': 'Position',
                'CHANGE_DATE': 'ChangeDate', 'FORM_DATE': 'NoticeDate', 'CHANGE_NUM': 'ChangeNum', 'HOLDSTOCK_NUM': 'ChangedNum',
                'CHANGE_REASON': 'ChangeReason', 'CURRENT_AVG_PRICE': 'AvgPrice'})
            df = df[['Code', 'Name', 'ManagerName', 'Position', 'ChangeDate', 'NoticeDate', 'ChangeNum', 'ChangedNum', 'ChangeReason', 'AvgPrice']]
            df['Code'] = df['Code'].astype(str) + '.SH'
            print(df)
            sql.df_to_sql(df, 'FinanceData..Share_Hold_Change')
                
        else:
            print('响应中未找到 pageHelp 或 data 字段')
    except json.JSONDecodeError as e:
        print(f'JSON解析错误: {e}')
    except Exception as e:
        print(f'处理数据时发生错误: {e}')

if __name__ == '__main__':
    save_path = 'C:/Users/Top/Desktop/高管公告/上海.csv'
    # 包括前面，不包括后面
    # 7.3 2023.1.1
    # 7.3 2022.1.1  73
    # 7.3 2020.1.1  113
    # 7.3 2015.1.1  146
    # 7.3 2005.1.1  92
    for page in range(1, 93):
        fetch_data(begin_date='2005-01-01', end_date='2014-12-31', page_no=page, begin_page=page, end_page=page, save_path=save_path)
        time.sleep(random.uniform(0, 30))