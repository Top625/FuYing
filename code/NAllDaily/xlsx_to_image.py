import win32com.client as win32
import os


def xlsx_to_image(xlsx_file_path, output_image_path, sheet_index=1):
    """
    将指定 WPS Excel 文件中的工作表转换为图片。

    :param xlsx_file_path: Excel 文件的完整路径
    :param output_image_path: 输出图片的完整路径
    :param sheet_index: 要转换的工作表索引，从 1 开始，默认为 1
    """
    # 检查输入的文件路径是否存在
    if not os.path.isfile(xlsx_file_path):
        print(f"指定的 Excel 文件 {xlsx_file_path} 不存在，请检查路径。")
        return

    try:
        # 创建 WPS 电子表格应用程序对象
        wps = win32.gencache.EnsureDispatch('ket.Application')
        # 打开 Excel 文件
        workbook = wps.Workbooks.Open(xlsx_file_path)
        # 获取指定工作表
        worksheet = workbook.Sheets(sheet_index)

        # 激活工作表
        worksheet.Activate()

        # 选择整个工作表
        worksheet.Cells.Select()

        # 创建一个临时图表对象
        chart = workbook.Charts.Add()
        chart.SetSourceData(worksheet.UsedRange)
        chart.ChartType = 4  # 4 代表柱形图，这里只是临时设置，不影响最终图片

        # 导出图表为图片
        chart.Export(output_image_path)

        # 删除临时图表
        chart.Delete()

        # 关闭工作簿和应用程序
        workbook.Close(SaveChanges=0)
        wps.Quit()

        print(f"图片已成功保存到 {output_image_path}")
    except Exception as e:
        print(f"转换过程中出现错误: {e}")
    finally:
        # 释放 COM 对象
        if 'wps' in locals():
            del wps


if __name__ == "__main__":
    # 请将下面的路径替换为你实际的绝对路径
    xlsx_file = r"C:\Users\Top\Desktop\每日收益 1.xlsx"
    output_image = r"C:\Users\Top\Desktop\output_image.png"
    xlsx_to_image(xlsx_file, output_image)