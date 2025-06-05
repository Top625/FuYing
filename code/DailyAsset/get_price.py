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
    
    Code_line=['300237.SZ', '002084.SZ', '002494.SZ', '002072.SZ', '600533.SH', '000545.SZ', '002652.SZ', '000826.SZ', '002634.SZ', '603183.SH', '603616.SH', '002622.SZ', '000637.SZ', '000692.SZ', '002133.SZ', '600408.SH', '000890.SZ', '601996.SH', '002247.SZ', '002486.SZ', '603778.SH', '002798.SZ', '600159.SH', '000632.SZ', '002775.SZ', '835857.BJ', '871970.BJ', '836942.BJ', '870508.BJ', '836414.BJ', '839719.BJ', '873527.BJ', '831768.BJ', '838030.BJ', '873679.BJ', '430090.BJ', '830832.BJ', '836504.BJ', '839946.BJ', '837174.BJ', '833580.BJ', '833266.BJ', '831641.BJ', '833873.BJ', '836149.BJ', '831768.BJ', '831370.BJ', '871970.BJ', '832471.BJ', '836942.BJ', '838030.BJ', '839946.BJ', '830974.BJ', '873679.BJ', '837174.BJ', '836414.BJ', '870508.BJ', '836422.BJ', '871857.BJ', '833580.BJ', '430685.BJ', '836149.BJ', '836260.BJ', '836871.BJ', '836504.BJ', '831856.BJ', '834062.BJ', '836149.BJ', '833781.BJ', '838275.BJ', '430017.BJ', '833914.BJ', '836826.BJ', '871634.BJ', '836414.BJ', '836871.BJ', '871245.BJ', '836263.BJ', '920445.BJ', '430564.BJ', '831278.BJ', '831152.BJ', '834475.BJ', '831832.BJ', '835184.BJ', '920016.BJ', '873152.BJ', '834407.BJ', '871245.BJ', '836414.BJ', '831175.BJ', '873132.BJ', '839946.BJ', '832175.BJ', '836149.BJ', '836422.BJ', '832651.BJ', '833873.BJ', '831641.BJ', '837174.BJ', '832802.BJ', '837046.BJ', '871553.BJ', '831906.BJ', '873679.BJ', '000607.SZ', '600791.SH', '600052.SH', '002671.SZ', '002109.SZ', '300385.SZ', '300639.SZ', '603778.SH', '000068.SZ', '601996.SH', '000509.SZ', '600231.SH', '300305.SZ', '600533.SH', '000548.SZ', '603797.SH', '000790.SZ', '300190.SZ', '688148.SH', '600561.SH', '600665.SH', '300289.SZ', '603878.SH', '603017.SH', '300422.SZ', '600802.SH', '600512.SH', '002333.SZ', '300187.SZ', '600683.SH', '002687.SZ', '000838.SZ', '000407.SZ', '688098.SH', '688189.SH', '000952.SZ', '002638.SZ', '000593.SZ', '603909.SH', '600815.SH', '688528.SH', '300234.SZ', '600235.SH', '002360.SZ', '600408.SH', '002883.SZ', '001373.SZ', '300103.SZ', '001336.SZ', '002205.SZ', '600778.SH', '603183.SH', '605178.SH', '002207.SZ', '002910.SZ', '001259.SZ', '688156.SH', '002800.SZ', '300970.SZ', '605287.SH', '002193.SZ', '000632.SZ', '603709.SH', '002963.SZ', '600697.SH', '688618.SH', '688229.SH', '003008.SZ', '688045.SH', '688026.SH', '301227.SZ', '605189.SH', '600697.SH', '002858.SZ', '600444.SH', '300966.SZ', '603028.SH', '688272.SH', '605003.SH', '605155.SH', '603183.SH', '688156.SH', '603908.SH', '301257.SZ', '301272.SZ', '603269.SH', '688013.SH', '603519.SH', '688616.SH', '603115.SH', '605259.SH', '603080.SH', '003016.SZ', '603309.SH', '001299.SZ', '002871.SZ', '003008.SZ', '003018.SZ', '002228.SZ', '603506.SH', '002772.SZ', '002391.SZ', '002107.SZ', '603326.SH', '603682.SH', '603706.SH', '002836.SZ', '002404.SZ', '300743.SZ', '603788.SH', '301027.SZ', '688156.SH', '688260.SH', '688216.SH', '688272.SH', '301429.SZ', '300935.SZ', '300970.SZ', '688058.SH', '688455.SH', '002795.SZ', '301198.SZ', '688355.SH', '300838.SZ', '688265.SH', '301126.SZ', '300668.SZ', '688118.SH', '002629.SZ', '301105.SZ', '688216.SH', '688310.SH', '300437.SZ', '688060.SH', '002319.SZ', '605177.SH', '300966.SZ', '300410.SZ', '300878.SZ', '300645.SZ', '300668.SZ', '603335.SH', '002360.SZ', '301126.SZ', '300305.SZ', '002524.SZ', '002873.SZ', '603778.SH', '000952.SZ', '300837.SZ', '301198.SZ', '688156.SH', '688260.SH', '605178.SH', '001336.SZ', '603729.SH', '002193.SZ', '600697.SH', '002800.SZ', '600302.SH', '301010.SZ', '002963.SZ', '003023.SZ', '688573.SH', '002910.SZ', '603183.SH', '600778.SH', '600202.SH', '300971.SZ', '688272.SH']
    
    PriceDF=getLatestPriceByRedisCache(Code_line)
    
    # 保存结果到 CSV 文件
    output_csv_path = r'c:\Users\Top\Desktop\FuYing\code\DailyAsset\持仓\price_result.csv'
    PriceDF.to_csv(output_csv_path, index=False)
    print(f"结果已保存到 {output_csv_path}")

    # 如果你想保存为 Excel 文件，可以使用以下代码
    # output_excel_path = r'c:\Users\Top\Desktop\FuYing\code\DailyAsset\price_result.xlsx'
    # PriceDF.to_excel(output_excel_path, index=False)
    # print(f"结果已保存到 {output_excel_path}")
    
