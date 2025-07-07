import pandas as pd

# 处理成交明细，读取成交明细文件，对数据进行清洗和分组求和操作
# input_path: 成交明细文件路径
# output_path: 处理结果保存路径
# 返回分组求和后的 DataFrame
def deal_real_detail(input_path, output_path):
    # 读取成交明细文件，使用 gbk 编码
    df = pd.read_csv(input_path, encoding='gbk')
    # 根据操作类型（买入或卖出）调整成交数量的正负
    df['成交数量'] = df.apply(lambda row: -row['成交数量'] if row['操作'] == '卖出' else row['成交数量'], axis=1)
    # 将证券代码转换为字符串并补零至 6 位
    df['证券代码'] = df['证券代码'].astype(str).str.zfill(6)
    # 组合证券代码和证券市场生成股票代码
    df['股票代码'] = df['证券代码'] + '.' + df['证券市场'].astype(str)
    # 按股票代码和证券名称分组，对成交数量、成交金额和手续费进行求和
    grouped = df.groupby(['股票代码', '证券名称'])[['成交数量', '成交金额', '手续费']].sum().reset_index()
    grouped.to_csv(output_path, index=False)
    return grouped

# 处理委托明细，读取委托明细文件，对数据进行清洗和分组求和操作
# input_path: 委托明细文件路径
# output_path: 处理结果保存路径
# 返回分组求和后的 DataFrame
def deal_entrust_detail(input_path, output_path):
    # 读取委托明细文件，使用 gbk 编码
    df = pd.read_csv(input_path, encoding='gbk')
    # 根据买卖方向（买入或卖出）调整委托数量的正负
    df['委托数量'] = df.apply(lambda row: -row['股票数量'] if row['买卖方向'] == '卖出' else row['股票数量'], axis=1)
    # 按股票代码和股票名称分组，对委托数量进行求和
    grouped = df.groupby(['股票代码', '股票名称'])[['委托数量']].sum().reset_index()
    grouped.to_csv(output_path, index=False)
    return grouped

# 读取委托明细文件，返回原始 DataFrame
# input_path: 委托明细文件路径
# 返回原始委托明细 DataFrame
def read_entrust_csv(input_path):
    df = pd.read_csv(input_path, encoding='gbk')
    return df

if __name__ == '__main__':
    # 示例调用，需替换为实际路径
    input_file = 'C:/Users/Top/Desktop/子策略测试/国君成交明细.csv'
    output_file = 'C:/Users/Top/Desktop/子策略测试/成交 明细结果.csv'
    # 调用 deal_real_detail 函数处理成交明细
    deal_real_df = deal_real_detail(input_file, output_file)

    input_file = 'C:/Users/Top/Desktop/子策略测试/国君收盘调仓明细.csv'
    output_file = 'C:/Users/Top/Desktop/子策略测试/委托 明细结果.csv'
    # 调用 deal_entrust_detail 函数处理委托明细
    deal_entrust_df = deal_entrust_detail(input_file, output_file)

    # 读取原始委托明细文件
    entrust_df = read_entrust_csv(input_file)
    # 打印处理后的成交明细、委托明细和原始委托明细
    print('处理后的成交明细:', deal_real_df)
    print('处理后的委托明细:', deal_entrust_df)
    print('原始委托明细:', entrust_df)

    # 合并成交明细和委托明细数据，计算成交数量差值
    merged_df = pd.merge(deal_real_df, deal_entrust_df, on='股票代码', how='left')
    # 计算每个股票的成交数量与委托数量的差值
    merged_df['数量差值'] = merged_df['成交数量'] - merged_df['委托数量'].fillna(0)
    print('合并后的成交明细和委托明细:', merged_df)

    # 初始化分配结果列表，用于存储每个股票的分配信息
    allocation_results = []

    # 遍历每个股票代码，进行成交数量的策略分配
    for _, stock_row in merged_df.iterrows(): 
        # 获取当前股票代码
        stock_code = stock_row['股票代码']
        # 获取当前股票的成交数量差值
        quantity_diff = stock_row['数量差值']
        # 判断交易方向，正为买入，负为卖出
        direction = '买入' if quantity_diff > 0 else '卖出' 
        # 从原始委托明细中筛选出当前股票的委托记录
        stock_entrusts = entrust_df[entrust_df['股票代码'] == stock_code]

        # 筛选出与差值方向相同的委托记录
        if direction == '买入':
            filtered_entrusts = stock_entrusts[stock_entrusts['买卖方向'] == '买入']
        else:
            filtered_entrusts = stock_entrusts[stock_entrusts['买卖方向'] == '卖出']

        # 记录当前股票的所有策略
        all_strategies = set(filtered_entrusts['策略类型'].tolist())
        # 记录当前股票已分配的策略
        allocated_strategies = set()

        # 按股票数量升序排序，优先分配数量少的委托
        filtered_entrusts = filtered_entrusts.sort_values('股票数量')
        # 剩余待分配的数量，取绝对值
        remaining_quantity = abs(deal_real_df[deal_real_df['股票代码'] == stock_code]['成交数量'].values[0])

        # 分配成交数量给符合条件的委托记录
        for _, entrust_row in filtered_entrusts.iterrows(): 
            # 获取当前委托的策略类型
            strategy = entrust_row['策略类型']
            # 获取当前委托的股票数量，取绝对值
            entrust_quantity = abs(entrust_row['股票数量'])
            # 计算本次分配的数量，取剩余待分配数量和委托数量的最小值
            allocated_quantity = min(remaining_quantity, entrust_quantity)
            if allocated_quantity > 0: 
                # 将分配信息添加到结果列表中
                allocation_results.append((stock_code, strategy, allocated_quantity, direction))
                # 记录已分配的策略
                allocated_strategies.add(strategy)
                # 更新剩余待分配数量
                remaining_quantity -= allocated_quantity
            if remaining_quantity == 0: 
                # 若剩余待分配数量为 0，停止分配
                break

        # 若循环结束后还有剩余数量未分配，则将其分配给最后一个策略
        if remaining_quantity > 0 and not filtered_entrusts.empty:
            last_entrust_row = filtered_entrusts.iloc[-1]
            last_strategy = last_entrust_row['策略类型']
            allocation_results.append((stock_code, last_strategy, remaining_quantity, direction))
            allocated_strategies.add(last_strategy)

        # 找出未分配到的策略
        unallocated_strategies = all_strategies - allocated_strategies
        if unallocated_strategies:
            print(f'股票代码 {stock_code} 未分配到的策略: {unallocated_strategies}')

    # 打印每个股票的分配结果
    print('股票分配结果：')
    for result in allocation_results:
        print(f'股票代码: {result[0]}, 策略: {result[1]}, 分配数量: {result[2]}, 方向: {result[3]}')

