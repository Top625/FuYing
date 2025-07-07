import handle_sql
import get_email
import deal_all_account
from time import sleep

def main():
    net_value_dic = handle_sql.select_net_value(yesterday_date_str, accounts[0]['product'])
    print('昨日净值', net_value_dic)
    if net_value_dic[0]['netvalue'] is None:
        get_email.download_email_exl()
        sleep(60*5)
        deal_all_account.deal(False)

if __name__ == '__main__':
    mian()