from datetime import datetime
from time import sleep
import handle_sql

import download_ftp
import deal_part_data
import get_email
import deal_all_account
import daily_result
import netvalue_chart


if __name__ == '__main__':
    today = datetime.today().strftime("%Y%m%d")
    if handle_sql.check_isstockday(today):
        download_ftp.download_files()           # 3:10 下载ftp表格
        sleep(60*10)
        deal_part_data.main()                   # 3:20 将各个账号插入到数据库
        sleep(60*10) 
        get_email.download_email_exl()          # 3:30 获取邮箱中净值并插入到数据库
        sleep(60*10) 
        deal_all_account.deal()                 # 3:40 将各个产品插入到数据库
        sleep(60*10)
        daily_result.export_daily_result()      # 3:45 发送每日持仓、净值表格
        netvalue_chart.send_netvalue_chart()    # 3:45 发送折线图
        