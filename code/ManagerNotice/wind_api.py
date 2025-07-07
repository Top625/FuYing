import requests
import json
import pandas as pd 

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
    
    
    
if __name__ == "__main__":
    # 示例：调用Wind API的wsd函数
    # server_url = 'http://192.168.1.123:5888'
    #w.wsd(codes, fields, beginTime, endTime, options)
    # result = call_wind_api(server_url, 'wsd', {'codes': '000001.SZ', 'fields': 'open,high,low,close', 'beginTime': '2025-03-07', 'endTime': '2025-03-07', "options": "PriceAdj=F"})
    result = call_wind_api('wsd', ['603300.SH','holder_nature, shareholdernature', '2023-12-21','2023-12-21',"order=1"])
    print(result)
        # data = call_wind_api("wset", ['majorholderdealrecord',
    #  f"startdate={startdate};enddate={enddate};sectorid=a001010300000000;type=announcedate;field=wind_code,announcement_date,change_start_date,change_end_date,shareholder_name,shareholder_type,direction,change_number,number_after_change,average_price"])
    # print(data)

        # 初始化WindPy
    # w.start()
    # data = w.wset("majorholderdealrecord",
                # f"startdate={startdate};enddate={enddate};sectorid=a001010300000000;type=announcedate;field=wind_code,announcement_date,change_start_date,change_end_date,shareholder_name,shareholder_type,direction,change_number,number_after_change,average_price")
