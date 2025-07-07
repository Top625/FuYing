from datetime import datetime
from time import sleep

from lark_oapi import im
import handle_sql

import download_ftp
import deal_part_data
import get_email
import deal_all_account
import daily_result
import netvalue_chart
import check_email


if __name__ == '__main__':
    today = datetime.today().strftime("%Y%m%d")
    if handle_sql.check_isstockday(today):
        download_ftp.download_files()           # 3:35 下载ftp表格
        sleep(60*10)
        deal_part_data.main()                   # 3:45 将各个账号插入到数据库
        sleep(60*5) 
        get_email.download_email_exl()          # 3:50 获取邮箱中净值并插入到数据库
        sleep(60*5) 
        deal_all_account.deal(False)            # 3:55 将各个产品插入到数据库
        sleep(60*5)
        daily_result.export_daily_result()      # 4:00 发送每日持仓、净值表格
        netvalue_chart.send_netvalue_chart()    # 4:00 发送折线图
        sleep(60*60*5)
        check_email.main()                      # 9:00 检查邮件是否获取成功
        