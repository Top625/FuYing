from WindPy import w

# USDCNY.EX	美元中间价
# JSHDBL	结算汇兑比率
# HKDCNY.EX	港币中间价
# CKHL	参考汇率

w.start()
# 命令如何写可以用命令生成器来辅助完成
# 定义打印输出函数，用来展示数据使用
def printpy(outdata):
    if outdata.ErrorCode!=0:
        print('error code:'+str(outdata.ErrorCode)+'\n')
        return()
    for i in range(0,len(outdata.Data[0])):
        strTemp=''
        if len(outdata.Times)>1:
            strTemp=str(outdata.Times[i])+' '
        for k in range(0, len(outdata.Fields)):
            strTemp=strTemp+str(outdata.Data[k][i])+' '
        print(strTemp)

# 通过wsd来提取时间序列数据，比如取开高低收成交量，成交额数据
# print('\n\n'+'-----通过wsd来提取时间序列数据，比如取开高低收成交量，成交额数据-----'+'\n')
# wsddata1=w.wsd("000001.SZ", "open,high,low,close,volume,amt", "2015-11-22", "2015-12-22", "Fill=Previous")
wsddata2 = w.wsd("JSHDBL", "pre_close,open,high,low,close,amt,turn,adjfactor", "2025-06-01", "2025-06-11", "unit=1;TradingCalendar=HKEX;Fill=Previous;Currency=HKD;PriceAdj=B")
# printpy(wsddata2)
data=w.edb("EMM00058124,EMM00058126", "IsLatest=0,StartDate=2023-12-20,EndDate=2023-12-21")
print(data)

# # 通过wsd来提取各个报告期财务数据
# print('\n\n'+'-----通过wsd来提取各个报告期财务数据-----'+'\n')
# wsddata2=w.wsd("600000.SH", "tot_oper_rev,tot_oper_cost,opprofit,net_profit_is", "2008-01-01", "2015-12-22", "rptType=1;Period=Q;Days=Alldays;Fill=Previous")
# printpy(wsddata2)

# # 通过wss来取截面数据
# print('\n\n'+'-----通过wss来取截面数据-----'+'\n')
# wssdata=w.wss("600000.SH,600007.SH,600016.SH", "ev,total_shares","tradeDate=20151222;industryType=1")
# printpy(wssdata)

# # 取从今天往前推10天的日历日
# import datetime
# today = datetime.date.today() 
# w_tdays_data = w.tdaysoffset(-10, today.isoformat(), "Period=D;Days=Alldays")

# # 通过wst来取日内成交数据，最新7日内数据
# print('\n\n'+'-----通过wst来取日内成交数据-----'+'\n')
# wstdata=w.wst("IF.CFE", "last,volume", w_tdays_data.Data[0][0], today)
# printpy(wstdata)

# # 通过wsi来取日内分钟数据，三年内数据
# print('\n\n'+'-----通过wsi来取日内分钟数据-----'+'\n')
# wsidata=w.wsi("IF.CFE", "open,high,low,close,volume,amt", w_tdays_data.Data[0][0], today)
# printpy(wsidata)

# # 通过wset来取数据集数据
# print('\n\n'+'-----通过wset来取数据集数据,获取沪深300指数权重-----'+'\n')
# wsetdata=w.wset("IndexConstituent","date=20151222;windcode=000300.SH;field=date,wind_code,i_weight")
# printpy(wsetdata)