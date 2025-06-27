from openpyxl.descriptors import Bool
import tool
import handle_sql
from datetime import datetime


def select(today, fund_accounts, is_first: Bool):
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
    sgsh_amount = 0
    
    if accounts:
        for account in accounts:
            total_totalassets += account['totalassets']
            total_marketvalue += account['marketvalue']
            total_cash += account['cash']

            total_daily += account['daily']
            print('total_daily', total_daily, account)

            # 获取申购赎回金额
            subscription_redemption = handle_sql.select_SGSH_amount(today, account['fundaccount'])
            if isinstance(subscription_redemption, (list, tuple)) and len(subscription_redemption) == 0:
                sgsh_amount += 0
            else:
                sgsh_amount = sum(float(item['amount']) for item in subscription_redemption)
                # sgsh_amount += float(subscription_redemption[0]['amount'])
            print('申购赎回', sgsh_amount)

        # 上一个交易日
        yesterday_date_str = handle_sql.get_previous_trading_day(today)

        product_history = handle_sql.select_product(yesterday_date_str, accounts[0]['product'])
        print('产品历史数据', product_history)
        cost = 0
        if isinstance(product_history, (list, tuple)) and len(product_history) == 0:
            net_yesterday_total_assets = 0
            yesterday_total_assets = 0
        else:
            yesterday_data = product_history[0]
            yesterday_total_assets = float(product_history[0]['totalassets'])

            if not all(yesterday_data.get(key) for key in ['totalassetse', 'netassetse', 'cost']):
                net_yesterday_total_assets = float(product_history[0]['totalassets'])
            else:
                net_yesterday_total_assets = float(product_history[0]['netassetse'])
                cost = yesterday_data['cost']

        print('上一个交易日产品总资产', accounts[0]['product'],net_yesterday_total_assets)

        # 计算日涨跌幅
        print(today, accounts[0]['product'], sgsh_amount) 
        if sgsh_amount >= 0:  # 申购
            net_daily_per = (total_totalassets - abs(sgsh_amount) - net_yesterday_total_assets - cost) / (net_yesterday_total_assets + sgsh_amount) if net_yesterday_total_assets + sgsh_amount != 0 else 0
            daily_per = (total_totalassets - abs(sgsh_amount) - yesterday_total_assets) / (yesterday_total_assets + sgsh_amount) if yesterday_total_assets + sgsh_amount != 0 else 0
        else:
            net_daily_per = (total_totalassets + abs(sgsh_amount) - net_yesterday_total_assets - cost) / net_yesterday_total_assets if net_yesterday_total_assets != 0 else 0
            daily_per = (total_totalassets + abs(sgsh_amount) - yesterday_total_assets) / yesterday_total_assets if yesterday_total_assets != 0 else 0


        today = datetime.strptime(today, '%Y%m%d')
        # 计算月起始日期
        last_month_date = today.replace(month=today.month, year=today.year, day=1)
        # 计算年起始日期
        last_year_date = today.replace(year=today.year, month=1, day=1)

        # 计算月涨跌幅和月盈亏
        monthly_data = handle_sql.select_product_by_range(last_month_date.strftime('%Y%m%d'), today.strftime('%Y%m%d'), accounts[0]['product'])
        if not monthly_data.empty:
            monthly_profit = monthly_data['daily'].sum()
            monthly_profit += total_daily
            monthly_return = 1
            for daily_per_item in monthly_data['dailyper']:
                daily_per_value = float(daily_per_item.strip('%')) / 100
                monthly_return *= (1 + daily_per_value)
            monthly_return *= (1 + daily_per)
            monthly_return -= 1
        else:
            monthly_return = 0
            monthly_profit = 0

        # 计算年涨跌幅和年盈亏
        annual_data = handle_sql.select_product_by_range(last_year_date.strftime('%Y%m%d'), today.strftime('%Y%m%d'), accounts[0]['product'])
        if not annual_data.empty:
            annual_profit = annual_data['daily'].sum()
            annual_profit += total_daily
            annual_return = 1
            for daily_per_item in annual_data['dailyper']:
                daily_per_value = float(daily_per_item.strip('%')) / 100
                annual_return *= (1 + daily_per_value)
            annual_return *= (1 + daily_per)
            annual_return -= 1
        else:
            annual_return = 0
            annual_profit = 0

        # 计算总涨跌幅和总盈亏
        start_date = '19000101'
        total_data = handle_sql.select_product_by_range(start_date, today.strftime('%Y%m%d'), accounts[0]['product'])
        if not total_data.empty:
            total_profit = total_data['daily'].sum()
            total_profit += total_daily
            total_return = 1
            for daily_per_item in total_data['dailyper']:
                daily_per_value = float(daily_per_item.strip('%')) / 100
                total_return *= (1 + daily_per_value)
            total_return *= (1 + daily_per)
            total_return -= 1
        else:
            total_return = 0
            total_profit = 0

        # 计算净值
        net_value_dic = handle_sql.select_net_value(yesterday_date_str, accounts[0]['product'])
        print('昨日净值', net_value_dic)
        if net_value_dic[0]['netvalue'] is None:
            yesterday_net_value = net_value_dic[0]['netvalueest']
        else:
            yesterday_net_value = net_value_dic[0]['netvalue']
        net_value_est = yesterday_net_value * (1 + net_daily_per)
        print('净值', net_value_est)

        # 生成结果
        result = {
            'Date': today.strftime('%Y%m%d'),
            'Product': accounts[0]['product'],
            'TotalAssets': total_totalassets,
            'MarketValue': total_marketvalue,
            'Cash': total_cash,
            'Position': f"{(total_marketvalue/total_totalassets) * 100:.2f}%",
            'DailyPer': f"{daily_per * 100:.2f}%",
            'Daily': round(total_daily, 2),
            'MonthlyPer': f"{monthly_return * 100:.2f}%",
            'Monthly': round(monthly_profit, 2),
            'YearlyPer': f"{annual_return * 100:.2f}%",
            'Yearly': round(annual_profit, 2),
            'TotalPer': f"{total_return * 100:.2f}%",
            'Total': round(total_profit, 2),
            'NetValueEst': round(net_value_est, 4),
            'NetDailyPer': f"{net_daily_per * 100:.2f}%"
        }
        print('结果', result)
        if is_first == True:
            handle_sql.add_product(result)
            handle_sql.add_net_value(today.strftime('%Y%m%d'), accounts[0]['product'], None, round(net_value_est, 4))
        else:
            removed_date = result.pop("Date")
            removed_product = result.pop("Product")
            handle_sql.update_product(removed_date, removed_product, result)
            handle_sql.update_net_value(today.strftime('%Y%m%d'), accounts[0]['product'], None, round(net_value_est, 4))
    

def deal(is_first: Bool):
    today = datetime.today().strftime("%Y%m%d")
    # today = '20250625'
    config_data = tool.read_ftp_config()

    if config_data:
        for product in config_data['products']:
            fund_accounts = []
            for code in product['codes']:
                fund_accounts += code['fund_account']
            select(today, fund_accounts, is_first)


if __name__ == "__main__":
    deal(False)