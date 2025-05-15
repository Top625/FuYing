import os
import zipfile
from pathlib import Path
from datetime import datetime
import fuyi_log_xlsx as log_xlsx
import pandas as pd

def split_zip_file(file_path, zip_base_path, chunk_size=1024 * 1024):
    """
    对指定文件进行分卷压缩，直接将分卷文件保存到指定基础路径
    :param file_path: 要压缩的文件的绝对路径
    :param zip_base_path: 压缩分卷文件的基础路径，包含文件名前缀
    :param chunk_size: 每个分卷的大小，单位为字节
    :return: 压缩是否成功的布尔值, 压缩文件存储的目录路径
    """
    try:
        file_path = Path(file_path)
        zip_base_path = Path(zip_base_path)
        zip_base_path.parent.mkdir(parents=True, exist_ok=True)

        part_number = 1
        with open(file_path, 'rb') as src_file:
            while True:
                zip_file_name = zip_base_path.parent / f"{zip_base_path.name}.{part_number:03d}"
                with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    data = src_file.read(chunk_size)
                    if not data:
                        break
                    # 创建一个虚拟的文件名为原文件名
                    zipf.writestr(file_path.name, data)
                print(f"已生成分卷文件 {zip_file_name}")
                part_number += 1
        print(f"{file_path} 分卷压缩成功，压缩文件存储在 {zip_base_path.parent}")
        return True, str(zip_base_path.parent)
    except Exception as e:
        print(f"{file_path} 分卷压缩失败，错误信息: {e}")
        return False, ""

def extract_split_zip(zip_file_path, extract_dir):
    """
    解压分卷压缩的 zip 文件
    :param zip_file_path: 第一个分卷的 zip 文件的绝对路径
    :param extract_dir: 解压目标的绝对路径
    :return: 解压是否成功的布尔值, 解压后文件的路径
    """
    try:
        zip_file_path = Path(zip_file_path)
        extract_dir = Path(extract_dir)
        extract_dir.mkdir(exist_ok=True)
        part_number = 1
        # 修改此处，添加 .zip 以正确获取第一个分卷文件
        first_zip_path = zip_file_path.parent / f"{zip_file_path.stem}.zip.001"
        with zipfile.ZipFile(first_zip_path, 'r') as first_zip:
            original_file_name = first_zip.namelist()[0]
        output_file_path = extract_dir / original_file_name
        with open(output_file_path, 'wb') as out_file:
            while True:
                # 确保构建的分卷文件名包含 .zip
                zip_part_name = zip_file_path.parent / f"{zip_file_path.stem}.zip.{part_number:03d}"
                if not os.path.exists(zip_part_name):
                    break
                with zipfile.ZipFile(zip_part_name, 'r') as zipf:
                    for info in zipf.infolist():
                        with zipf.open(info) as src:
                            out_file.write(src.read())
                part_number += 1
        print(f"{zip_file_path} 解压成功到 {extract_dir}")

        # 删除分卷压缩文件
        part_number = 1
        while True:
            # 确保构建的分卷文件名包含 .zip
            zip_part_name = zip_file_path.parent / f"{zip_file_path.stem}.zip.{part_number:03d}"
            if not os.path.exists(zip_part_name):
                break
            try:
                zip_part_name.unlink()
                print(f"已删除分卷文件 {zip_part_name}")
            except Exception as e:
                print(f"删除文件 {zip_part_name} 时出错: {e}")
            part_number += 1

        return True, str(output_file_path)
    except Exception as e:
        print(f"{zip_file_path} 解压失败，错误信息: {e}")
        return False, ""

def retry_failed_copy(log_file_path, extract_path):
    status_list = log_xlsx.check_data_fetch_status(log_file_path, '复制到本地是否成功')
    for task_name, time, copy_success in status_list:
        if not copy_success:
            df = pd.read_excel(log_file_path, sheet_name='日志记录表格')
            mask = (df["任务名"] == task_name) & (df["时间"] == time)
            cloud_path = df.loc[mask, "云电脑数据保存路径"].values[0]
            print(cloud_path)
            zip_base_path = fr"{cloud_path}.zip"
            # 第一个分卷文件的绝对路径
            first_zip_part = Path(zip_base_path).parent / f"{Path(zip_base_path).name}"
            # 处理 split_zip_file 的返回值
            zip_success, _ = split_zip_file(cloud_path, first_zip_part)
            if zip_success:
                # 处理 extract_split_zip 的返回值
                extract_success, extracted_file_path = extract_split_zip(first_zip_part, extract_path)
                if extract_success:
                    log_xlsx.update_log_data(
                        file_path=log_file_path,
                        task_name=task_name,
                        time=time,
                        copy_success=True,
                        local_path=extracted_file_path
                    )

if __name__ == "__main__":
    log_file_path = r'C:\Users\Top\Desktop\FuYing\code\FuYi\FuYiData\日志记录表格.xlsx'
    extract_path = r"C:\Users\Top\Desktop\fuyiyun\new"
    retry_failed_copy(log_file_path, extract_path)