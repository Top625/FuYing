import os
import zipfile
from pathlib import Path
import time
import fuyi_log_xlsx as log_xlsx
import pandas as pd

def compress_and_extract(input_file_path, zip_base_path, chunk_size=1024 * 1024):
    """
    对指定文件进行分卷压缩，暂停 30 秒后解压分卷文件。

    :param input_file_path: 要压缩的文件的绝对路径
    :param zip_base_path: 压缩分卷文件的基础路径，包含文件名前缀，同时也是解压目标路径
    :param chunk_size: 每个分卷的大小，单位为字节
    :return: 是否成功的布尔值, 解压后的文件路径
    """
    success = False
    try:
        file_path = Path(input_file_path)
        zip_base = Path(zip_base_path)
        zip_base.parent.mkdir(parents=True, exist_ok=True)

        # 分卷压缩
        part_number = 1
        with open(file_path, 'rb') as src_file:
            while True:
                zip_file_name = zip_base.parent / f"{zip_base.name}.{part_number:03d}"
                with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    data = src_file.read(chunk_size)
                    if not data:
                        break
                    zipf.writestr(file_path.name, data)
                print(f"已生成分卷文件 {zip_file_name}")
                part_number += 1
        print(f"{file_path} 分卷压缩成功，压缩文件存储在 {zip_base.parent}")

        time.sleep(30)

        # 解压
        extract_dir = zip_base.parent
        first_zip_part = zip_base.parent / f"{zip_base.name}.001"
        extract_dir.mkdir(exist_ok=True)
        with zipfile.ZipFile(first_zip_part, 'r') as first_zip:
            original_file_name = first_zip.namelist()[0]
        output_file_path = extract_dir / original_file_name
        with open(output_file_path, 'wb') as out_file:
            part_number = 1
            while True:
                zip_part_name = zip_base.parent / f"{zip_base.name}.{part_number:03d}"
                if not os.path.exists(zip_part_name):
                    break
                with zipfile.ZipFile(zip_part_name, 'r') as zipf:
                    for info in zipf.infolist():
                        with zipf.open(info) as src:
                            out_file.write(src.read())
                part_number += 1
        print(f"{first_zip_part} 解压成功到 {extract_dir}")

        # 删除分卷文件
        part_number = 1
        while True:
            zip_part_name = zip_base.parent / f"{zip_base.name}.{part_number:03d}"
            if not os.path.exists(zip_part_name):
                break
            try:
                zip_part_name.unlink()
                print(f"已删除分卷文件 {zip_part_name}")
            except Exception as e:
                print(f"删除文件 {zip_part_name} 时出错: {e}")
            part_number += 1

        success = True
        return success, str(output_file_path)
    except Exception as e:
        print(f"执行压缩和解压过程中出错: {e}")
        return success, ""


def retry_failed_copy(log_file_path):
    status_list = log_xlsx.check_data_fetch_status(log_file_path, '复制到本地是否成功')
    for task_name, time, copy_success in status_list:
        if not copy_success:
            df = pd.read_excel(log_file_path, sheet_name='日志记录表格')
            mask = (df["任务名"] == task_name) & (df["时间"] == time)
            cloud_path = df.loc[mask, "云电脑数据保存路径"].values[0]
            # 假设压缩到本地的路径和云路径文件名相同，目录为本地某个目录
            local_zip_base_path = r'C:\Users\Top\Desktop\fuyiyun\new'
            print(local_zip_base_path)  # 打印路径，检查是否正确，注意路径分隔符
            success, local_path = compress_and_extract(cloud_path, local_zip_base_path)
            if success:
                log_xlsx.update_log_data(
                    file_path=log_file_path,
                    task_name=task_name,
                    time=time,
                    copy_success=True,
                    local_path=local_path
                )


if __name__ == "__main__":
    log_file_path = r'C:\Users\Top\Desktop\FuYing\code\FuYi\FuYiData\日志记录表格.xlsx'
    retry_failed_copy(log_file_path)
    