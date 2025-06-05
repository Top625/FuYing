import os
import zipfile
from pathlib import Path
from datetime import datetime

def split_zip_file(file_path, zip_base_path, chunk_size=1024 * 1024):
    """
    对指定文件进行分卷压缩，直接将分卷文件保存到指定基础路径
    :param file_path: 要压缩的文件的绝对路径
    :param zip_base_path: 压缩分卷文件的基础路径，包含文件名前缀
    :param chunk_size: 每个分卷的大小，单位为字节
    """
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

def extract_split_zip(zip_file_path, extract_dir):
    """
    解压分卷压缩的 zip 文件
    :param zip_file_path: 第一个分卷的 zip 文件的绝对路径
    :param extract_dir: 解压目标的绝对路径
    """
    zip_file_path = Path(zip_file_path)
    extract_dir = Path(extract_dir)
    extract_dir.mkdir(exist_ok=True)
    part_number = 1
    # 获取第一个分卷文件中的文件名（原文件名）
    with zipfile.ZipFile(zip_file_path.parent / f"{zip_file_path.stem}.001", 'r') as first_zip:
        original_file_name = first_zip.namelist()[0]
    output_file_path = extract_dir / original_file_name
    with open(output_file_path, 'wb') as out_file:
        while True:
            zip_part_name = zip_file_path.parent / f"{zip_file_path.stem}.{part_number:03d}"
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
        zip_part_name = zip_file_path.parent / f"{zip_file_path.stem}.{part_number:03d}"
        if not os.path.exists(zip_part_name):
            break
        try:
            zip_part_name.unlink()
            print(f"已删除分卷文件 {zip_part_name}")
        except Exception as e:
            print(f"删除文件 {zip_part_name} 时出错: {e}")
        part_number += 1

if __name__ == "__main__":
    # 请根据实际情况修改以下路径
    # 要压缩的文件路径
    # 获取当前日期
    current_date = datetime.now().strftime("%Y%m%d")
    # 拼接指定路径
    input_file_path = fr"C:\Users\VM-0000H\eclipse-workspace\Test\src\Data\ZYYX_BJ_{current_date}.xlsx"
    # 压缩到的文件基础路径，指定分卷文件存储的位置和前缀
    zip_base_path = fr"\\Client\E$\Data\ZYYX_BJ_{current_date}.zip"
    # 第一个分卷文件的绝对路径
    first_zip_part = Path(zip_base_path).parent / f"{Path(zip_base_path).name}.001"
    # 解压到的文件路径
    extract_path = r"\\Client\E$\Data"

    # 分卷压缩
    split_zip_file(input_file_path, zip_base_path)
    # 解压分卷文件
    extract_split_zip(first_zip_part, extract_path)