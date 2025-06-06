import tool
import handle_sql
from datetime import datetime


def select(today, fund_accounts):
    print('today', today, 'fund_account', fund_accounts)
    accounts = []
    for fund_account in fund_accounts:
        accounts += handle_sql.select_account(today, fund_account)

    print(accounts)
    # 初始化累加变量
    total_totalassets = 0
    total_marketvalue = 0
    total_cash = 0
    total_daily = 0
    total_monthly = 0
    total_yearly = 0
    total_total = 0
    sgsh_amount = 0
    
    if accounts:
        for account in accounts:
            total_totalassets += account['totalassets']
            total_marketvalue += account['marketvalue']
            total_cash += account['cash']

            total_daily += account['daily']
            total_monthly += account['monthly']
            total_yearly += account['yearly']
            total_total += account['total']

            # 获取申购赎回金额
            subscription_redemption = handle_sql.select_SGSH_amount(today, account['fundaccount'])
            if isinstance(subscription_redemption, (list, tuple)) and len(subscription_redemption) == 0:
                sgsh_amount += 0
            else:
                sgsh_amount += float(subscription_redemption[0]['amount'])
                print('申购赎回', subscription_redemption[0])
            print('申购赎回', sgsh_amount)

        # 上一个交易日
        yesterday_date_str = handle_sql.get_previous_trading_day(today)

        product_history = handle_sql.select_product(yesterday_date_str, accounts[0]['product'])
        print('产品历史数据', product_history)
        if isinstance(product_history, (list, tuple)) and len(product_history) == 0:
            yesterday_total_assets = 0
        else:
            yesterday_total_assets = float(product_history[0]['totalassets'])
        print('产品历史数据', product_history[0])
        print('上一个交易日产品总资产', yesterday_total_assets)

        # 计算日涨跌幅
        print(today, accounts[0]['product'], sgsh_amount) 
        if sgsh_amount >= 0:  # 申购
            daily_return = (total_totalassets - abs(sgsh_amount) - yesterday_total_assets) / (yesterday_total_assets + sgsh_amount) if yesterday_total_assets + sgsh_amount != 0 else 0
        else:
            daily_return = (total_totalassets + abs(sgsh_amount) - yesterday_total_assets) / yesterday_total_assets if yesterday_total_assets != 0 else 0

        # # 计算月起始日期
        # last_month_date = current_date - timedelta(days=30)
        # # 计算年起始日期
        # last_year_date = current_date - timedelta(days=365)

        # TODO 计算月涨跌幅和月盈亏
        # monthly_return, monthly_profit = calculate_period_stats(historical_data, last_month_date, current_date,
        #                                                         today, account_name, daily_return)
        monthly_return = None
        if monthly_return is None:
            monthly_return = daily_return

        # # 计算年涨跌幅和年盈亏
        # annual_return, annual_profit = calculate_period_stats(historical_data, last_year_date, current_date,
        #                                                       today, account_name, daily_return)
        annual_return = None
        if annual_return is None:
            annual_return = daily_return

        # # 计算总涨跌幅和总盈亏
        # total_return, total_profit = calculate_period_stats(historical_data, datetime.min, current_date,
        #                                                      today, account_name, daily_return)
        total_return = None
        if total_return is None:
            total_return = daily_return

        # 计算净值
        net_value_dic = handle_sql.select_net_value(yesterday_date_str, accounts[0]['product'])
        print('昨日净值', net_value_dic)
        if net_value_dic[0]['netvalue'] is None:
            yesterday_net_value = net_value_dic[0]['netvalueest']
        else:
            yesterday_net_value = net_value_dic[0]['netvalue']
        net_value_est = yesterday_net_value * (1 + daily_return)
        print('净值', net_value_est)

        # 生成结果
        result = {
            'Date': today,
            'Product': accounts[0]['product'],
            'TotalAssets': total_totalassets,
            'MarketValue': total_marketvalue,
            'Cash': total_cash,
            'Position': f"{(total_marketvalue/total_totalassets) * 100:.2f}%",
            'DailyPer': f"{daily_return * 100:.2f}%",
            'Daily': round(total_daily, 2),
            'MonthlyPer': f"{monthly_return * 100:.2f}%",
            'Monthly': round(total_monthly, 2),
            'YearlyPer': f"{annual_return * 100:.2f}%",
            'Yearly': round(total_yearly, 2),
            'TotalPer': f"{total_return * 100:.2f}%",
            'Total': round(total_total, 2),
            'NetValueEst': round(net_value_est, 4)
        }
        print('结果-----------', result)
        handle_sql.add_product(result)
        handle_sql.add_net_value(today, accounts[0]['product'], None, None, round(net_value_est, 4))


def deal():
    today = datetime.today().strftime("%Y%m%d")
    # today = '20250604'
    config_data = tool.read_ftp_config()

    if config_data:
        for product in config_data['products']:
            fund_accounts = []
            for code in product['codes']:
                fund_accounts += code['fund_account']
            select(today, fund_accounts)


if __name__ == "__main__":
    deal()