from datetime import date
from lark_oapi import im
import handle_sql
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import tool
import send_as_bot
import numpy as np

def generate_netvalue_chart(product_name, save_path, feishu_group_name, start_date=None, end_date=None):
    """
    生成净值曲线图并保存，在标题下方添加多行关键数据
    
    参数:
        product_name: 产品名称
        start_date: 开始日期 (YYYY-MM-DD)，可选
        end_date: 结束日期 (YYYY-MM-DD)，可选
        title: 图表标题
        save_path: 图片保存路径
        feishu_group_name: 飞书群组名称
    """
    # 获取数据并按照时间排序
    data = handle_sql.select_net_value_by_range(product_name, start_date, end_date)
    data = data.sort_values('date')
    
    # 计算关键指标
    if len(data) > 0:
        # 转换为datetime格式
        data['date'] = pd.to_datetime(data['date'])
        
        # 计算各项指标
        y_values = data['netvalue'].fillna(data['netvalueest'])
        last_value = y_values.iloc[-1]
        last_date = data['date'].iloc[-1].strftime('%Y-%m-%d')
        
        # 计算涨跌幅
        change_rate_1d = 0.0
        change_rate_ytd = 0.0
        annualized_return = 0.0
        
        if len(data) > 1:
            prev_value = y_values.iloc[-2]
            change_rate_1d = (last_value / prev_value - 1) * 100
            
            # 计算年初至今收益
            year = int(last_date[:4])
            first_date_of_year = pd.to_datetime(f"{year-1}-12-31")  # 上一年最后一天
            ytd_data = data[data['date'] >= first_date_of_year]  # 大于上一年最后一天的数据
            if len(ytd_data) > 0:
                first_value_of_year = ytd_data.iloc[0]['netvalue']
                change_rate_ytd = (last_value / first_value_of_year - 1) * 100
            
            # 计算年化收益率
            if len(data) >= 2:
                days = (data['date'].iloc[-1] - data['date'].iloc[0]).days
                if days > 0:
                    total_return = (last_value / data['netvalue'].iloc[0] - 1) * 100
                    annualized_return = ((1 + total_return/100) ** (365/days) - 1) * 100
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 在图表上方添加标题和关键数据
    title=f'{product_name} {last_date} 净值走势图'
    plt.suptitle(title, fontsize=16, y=0.95)
    
    # 计算最大回撤
    max_dd_data = max_drawdown(data['date'].astype(str), y_values) if len(data) > 0 else None
    max_dd_text = f"{max_dd_data['max_drawdown']}% ({max_dd_data['start_date']}至{max_dd_data['end_date']})" if max_dd_data else "最大回撤: 无数据"
    
    # 在折线图上标注最大回撤区间
    if max_dd_data:
        start_date = pd.to_datetime(max_dd_data['start_date'])  
        end_date = pd.to_datetime(max_dd_data['end_date'])
        max_dd = max_dd_data['max_drawdown'] / 100
        
        # 绘制最大回撤区间
        ax.axvspan(start_date, end_date, color='red', alpha=0.1, label='最大回撤区间')
        ax.axhline(y=y_values[data['date'] == start_date].iloc[0], 
                  color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax.axhline(y=y_values[data['date'] == end_date].iloc[0], 
                  color='red', linestyle='--', linewidth=1, alpha=0.5)
        
        # 标注开始和结束时间
        ax.annotate(f'开始\n{start_date.strftime("%Y-%m-%d")}', 
                   xy=(start_date, y_values[data['date'] == start_date].iloc[0]),
                   xytext=(0, 10), textcoords='offset points',
                   ha='center', va='bottom', fontsize=8,
                   bbox=dict(boxstyle='round,pad=0.5', fc='red', alpha=0.2))
        ax.annotate(f'结束\n{end_date.strftime("%Y-%m-%d")}\n回撤:{max_dd*100:.2f}%', 
                   xy=(end_date, y_values[data['date'] == end_date].iloc[0]),
                   xytext=(0, -10), textcoords='offset points',
                   ha='center', va='top', fontsize=8,
                   bbox=dict(boxstyle='round,pad=0.5', fc='red', alpha=0.2))
    
    # 添加关键数据文本
    info_text = (
        f"最新净值: {last_value:.4f}\n"
        f"最新涨幅: {change_rate_1d:+.2f}%\n"
        f"年初至今: {change_rate_ytd:+.2f}%\n"
        f"年化收益: {annualized_return:+.2f}%\n"
        f"数据区间: {data['date'].iloc[0].strftime('%Y-%m-%d')} 至 {last_date}"
    )
    
    plt.gcf().text(0.02, 0.9, info_text, 
                  fontsize=12, 
                  ha='left', 
                  va='top',
                  bbox=dict(boxstyle='round', facecolor='whitesmoke', alpha=0))
    
    # 绘制折线图 
    ax.plot(data['date'], y_values, marker='o', markersize=1, linestyle='-', color='b')
    
    # 设置坐标轴标签
    ax.set_xlabel('时间', fontsize=12)
    ax.yaxis.set_label_position("right")
    ax.set_ylabel('净值', fontsize=12, rotation=0, labelpad=20)
    
    # 设置纵轴范围
    if len(data) > 0:
        min_val = y_values.min()
        max_val = y_values.max()
        range_val = max_val - min_val
        ax.set_ylim(min_val - 0.1 * range_val, max_val + 0.1 * range_val)
    
    # 设置x轴格式
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    # 在右侧显示y轴
    ax.yaxis.tick_right()
    
    # 标注最后一个净值点
    if len(data) > 0:
        # 根据涨跌幅决定颜色
        color = 'red' if change_rate_1d >= 0 else 'green'
        ax.annotate(f'净值:{last_value:.4f}\n涨跌幅:{change_rate_1d:+.2f}%',
                    xy=(data['date'].iloc[-1], last_value),
                    xytext=(-5, 15),
                    textcoords='offset points',
                    ha='center',
                    va='bottom',
                    bbox=dict(boxstyle='round,pad=0.5', fc=color, alpha=0.7),
                    fontsize=10,
                    color='white',
                    weight='bold')
    
    plt.tight_layout(rect=[0, 0, 1, 0.85])  # 调整布局留出标题空间
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'图表已保存到 {save_path}')
    send_as_bot.send_group_message(feishu_group_name, True, save_path)

# 计算最大回撤函数
def max_drawdown(date_line, capital_line, isDel2015=0):
    """
    :param date_line: 日期序列
    :param capital_line: 账户价值序列
    :return: 返回字典包含最大回撤百分比、开始日期和结束日期
    """
    # 将数据序列合并为一个dataframe并按日期排序
    df = pd.DataFrame({'date': date_line, 'capital': capital_line})
    df.reset_index(drop=True, inplace=True)
    tempDF=pd.DataFrame()
    if(isDel2015==1):
        tempDF=df[-(df.date<='2015-12-31')]

    if(tempDF.shape[0]>0):
        df=tempDF    
    
    df['max2here'] = df['capital'].expanding().max()
    df['dd2here'] = df['capital'] / df['max2here'] - 1

    # 计算最大回撤和结束时间
    temp = df.sort_values(by='dd2here').iloc[0][['date', 'dd2here', 'max2here']]
    max_dd = temp['dd2here']
    end_date = temp['date']    
    max2here = temp['max2here']

    # 计算开始时间
    df = df[df['date'] <= end_date]
    start_date=df[df.max2here==max2here].iloc[0]['date']

    print(f'最大回撤为：{max_dd*100:.2f}%, 开始日期：{start_date}, 结束日期：{end_date}')
    return {
        'max_drawdown': round(max_dd*100, 2),
        'start_date': start_date,
        'end_date': end_date
    }

def send_netvalue_chart():
    today = date.today().strftime('%Y-%m-%d')
    config_data = tool.read_ftp_config()
    if config_data:
        for product in config_data['products']:
            product_name = product['name']
            print(f'{product}')
            generate_netvalue_chart(
                product_name=product_name,
                start_date=product['start_date'] if 'start_date' in product and product['start_date'] else None,
                save_path=rf'{product['local_path']}{product_name}{today}.png',
                feishu_group_name=config_data['feishu_group_name']
            )

if __name__ == '__main__':
    send_netvalue_chart()