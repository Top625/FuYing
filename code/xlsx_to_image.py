# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np

def xlsx_to_image(xlsx_path, output_image_path):
    """
    将 Excel 文件中的数据转换为图片。

    :param xlsx_path: Excel 文件的路径
    :param output_image_path: 输出图片的路径
    :return: 操作是否成功的布尔值
    """
    is_success = False
    try:
        # 读取 Excel 文件
        df = pd.read_excel(xlsx_path)

        # 设置图片清晰度
        plt.rcParams['figure.dpi'] = 300

        # 设置 matplotlib 支持中文
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体字体，Windows 系统常用
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示为方块的问题

        # 创建一个图形和坐标轴
        fig, ax = plt.subplots(figsize=(10, 5))

        # 隐藏坐标轴
        ax.axis('tight')
        ax.axis('off')

        # 绘制表格
        table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')

        # 设置表格样式
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1.2, 1.2)

        # 保存为图片
        canvas = FigureCanvas(fig)
        canvas.print_figure(output_image_path, bbox_inches='tight')

        # 关闭图形
        plt.close(fig)
        is_success = True
    except FileNotFoundError:
        print(f"未找到指定的 Excel 文件: {xlsx_path}，请检查文件路径。")
    return is_success


if __name__ == "__main__":
    xlsx_path = r'C:\Users\Top\Desktop\FuYing\code\FuYi\FuYiData\日志记录表格.xlsx'
    output_image_path = r'C:\Users\Top\Desktop\FuYing\code\FuYi\FuYiData日志记录表格.png'
    result = xlsx_to_image(xlsx_path, output_image_path)
    print(f"操作是否成功: {result}")