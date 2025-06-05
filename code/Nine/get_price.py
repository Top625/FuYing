# 获取价格

import pyodbc
import pandas as pd
import numpy as np
from numpy.lib.stride_tricks import as_strided as stride
import redis
import json


ServerIP='192.168.1.111' 
User = "sa" 
Password = "Quant6688"

redisPool = redis.ConnectionPool(host='192.168.1.123', port=6379, password='HJQuant888888', db=0) #6379
redisPool2 = redis.ConnectionPool(host='192.168.1.123', port=6379, password='HJQuant888888', db=1) #6379
MSCONN=pyodbc.connect('DRIVER={SQL Server};SERVER=' + ServerIP + ';DATABASE=HQData;UID=' + User +';PWD=' + Password)



#建立跟Server数据库的连接，需要手动关闭释放
def GetMSSQLConn(server=ServerIP, user=User, password=Password):
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';DATABASE=HQData;UID=' + user +';PWD=' + password)
    return conn  


#建立跟Server数据库的连接，需要手动关闭释放
def GetRedisConn(db=1):
    if(db==1):
        conn = redis.Redis(connection_pool=redisPool)
    else:
        conn = redis.Redis(connection_pool=redisPool2)
    return conn  


def getLatestSecurityHQDataByRedisCache(Code_line, channel=2):
    redisConn=GetRedisConn(channel)
    

    Code_line=list(dict.fromkeys(Code_line))
    result=pd.DataFrame()
    
    if(channel==1):
        CodeArray=np.array(Code_line)
                                     
        results = redisConn.mget(CodeArray)
            
        templist=[]
        
        for key, value in zip(CodeArray, results):
            if(value is None):
                continue        
            templist.append(json.loads(value.decode('utf-8')))
            
        result = pd.json_normalize(np.array(templist)) 
    elif(channel==2):
        hash_data_list = []
        for Code in Code_line:
        
            hash_data = redisConn.hgetall(Code)
     
            hash_data_json = {field.decode(): value.decode() for field, value in hash_data.items()}
        
            hash_data_list.append(hash_data_json)        
        result=pd.DataFrame(hash_data_list)
    
    return result



def GetXTStockStatusByMS(Code_line):
    codes="'" + ("','").join(list(Code_line)) + "'"
    print(codes)
    
    sql=(" select * from HQData..[XTStockBaseInfo] where Code in (" + codes + ") and Date=(select max(Date) from HQData..[XTStockBaseInfo])")
    result=pd.read_sql(sql, MSCONN)
        
    return result



def getLatestPriceByRedisCache(Code_line, channel=2):
            
    result=getLatestSecurityHQDataByRedisCache(Code_line, channel)
    
    if(result.shape[0]==0):
        return pd.DataFrame(columns=['Code', 'Name', 'BUYPRICE1', 'SELLPRICE1', 'PRECLOSE', 'HIGHLIMIT', 'LOWLIMIT', 'OPEN', 'HIGH', 'LOW', 'VOLUME', 'NOW', 'TradeStatus'])
    
    if(channel==1):    
        result['SELLPRICE1']=result['Ask0']
        result['BUYPRICE1']=result['Bid0']
        result['PRECLOSE']=result['PreClose']
        result['HIGHLIMIT']=result['HighLimit']
        result['LOWLIMIT']=result['LowLimit']
        result['OPEN']=result['Open']
        result['HIGH']=result['High']
        result['LOW']=result['Low']
        result['VOLUME']=result['Volume']
        result['NOW']=result['Latest']
        result['TradeStatus']=result['Volume'].apply(lambda x: 1 if(x>0)  else 98)                    
    else:
        result=result.dropna(subset=['Code'])
        result['askPrice']=result['askPrice'].apply(lambda x: json.loads(x)) 
        result['bidPrice']=result['bidPrice'].apply(lambda x: json.loads(x)) 
        result['bidVol']=result['bidVol'].apply(lambda x: json.loads(x)) 
        result['askVol']=result['askVol'].apply(lambda x: json.loads(x)) 
#         
        
        result['SELLPRICE1']=result['askPrice'].apply(lambda x: x[0]) 
        result['BUYPRICE1']=result['bidPrice'].apply(lambda x: x[0]) 
        result['PRECLOSE']=result['lastClose'].astype(float)
#         result['HIGHLIMIT']=result['HighLimit'].astype(float)
#         result['LOWLIMIT']=result['LowLimit'].astype(float)
        result['OPEN']=result['open'].astype(float)
        result['HIGH']=result['high'].astype(float)
        result['LOW']=result['low'].astype(float)        
        result['VOLUME']=result['volume'].astype(float)
        result['NOW']=result['lastPrice'].astype(float)
        
        
        
        StockInfoDF=GetXTStockStatusByMS(Code_line)
        result=pd.merge(result, StockInfoDF[['Code', 'Name', 'InstrumentStatus', 'HighLimit', 'LowLimit']], how='left', left_on=['Code'], right_on=['Code'])
        result['InstrumentStatus']=result['InstrumentStatus'].fillna(98)
        result['TradeStatus']=result['InstrumentStatus'].apply(lambda x: 1 if(int(x)<=0)  else 98)              
        
        result['HIGHLIMIT']=result['HighLimit'].astype(float)
        result['LOWLIMIT']=result['LowLimit'].astype(float)        
        
        
    return result[['Code', 'Name', 'BUYPRICE1', 'SELLPRICE1', 'PRECLOSE', 'HIGHLIMIT', 'LOWLIMIT', 'OPEN', 'HIGH', 'LOW', 'VOLUME', 'NOW', 'TradeStatus']]

#channel: 0, 本地SQLServcer; 1, redis数据库
def getLatestPriceByCache(Code_line, channel=1):
    result=pd.DataFrame()
    
    
    if(channel==0):
        conn=GetMSSQLConn()
        
        try:
            Code_line=list(dict.fromkeys(Code_line))
            codes=''             
            for code in Code_line:
                if(code=='888888'):
                    continue
                if(codes==''):
                    codes="'" + code + "' "
                else:
                    if(codes.find(code)<0):
                        codes=codes + ", '" + code + "' " 
                        
                             
            sql=("select * from HQData..RealTimeStockPriceBuffer where Code in ( " + codes + ")")
            result=pd.read_sql(sql, conn)
            
            result['BUYPRICE1']=result['BuyPrice1']
            result['SELLPRICE1']=result['SellPrice1']
            result['PRECLOSE']=result['PreClose']
            result['HIGHLIMIT']=result['HighLimit']
            result['LOWLIMIT']=result['LowLimit']
            result['OPEN']=result['Open']
            result['VOLUME']=result['Volume']
            result['NOW']=result['Now']
            result['TURNOVER']=result['Turnover']
        
            
            
        finally:
            conn.close()
    
    elif(channel==1):
        result=getLatestPriceByRedisCache(Code_line, channel)
    elif(channel==2):
        result=getLatestPriceByRedisCache(Code_line, channel)        
        
    return result



def getStockShares(Code_line):
    result=pd.DataFrame()  
    


    try: 
        conn = GetMSSQLConn()                              

        
        codes=''             
        for code in Code_line:
            if(codes==''):
                codes="'" + code + "'"
            else:
                codes=codes + "," + "'" + code + "'"            
           
               
        sql=" select Code, case when Code='689009.SH' then 10*cast(TOTALSHARE as float) else  cast(TOTALSHARE as float) end as TOTALSHARE, cast(LIQSHARE as float) as LIQSHARE from HQData..StockShareInfo a where  Date=(select max(Date) from HQData..StockShareInfo) and Code in (" + codes + ") "      

        result=pd.read_sql(sql, conn)
        return result

    except Exception as e:
        print('getStockShares, 获取股本信息，发生错误 ', e, ',data:', result)                                                                                
    finally:         
        conn.close()
                         
if __name__ == "__main__":
    pd.options.display.max_columns= 50
    pd.options.display.max_rows= 200
    
    Code_line=['204001.SH', '002084.SZ']
    
    PriceDF=getLatestPriceByRedisCache(Code_line)
    print(PriceDF)
    
    # 保存结果到 CSV 文件
    output_csv_path = r'c:\Users\Top\Desktop\FuYing\code\DailyAsset\持仓\price_result.csv'
    PriceDF.to_csv(output_csv_path, index=False)
    print(f"结果已保存到 {output_csv_path}")

    # 如果你想保存为 Excel 文件，可以使用以下代码
    # output_excel_path = r'c:\Users\Top\Desktop\FuYing\code\DailyAsset\price_result.xlsx'
    # PriceDF.to_excel(output_excel_path, index=False)
    # print(f"结果已保存到 {output_excel_path}")