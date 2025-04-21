import subprocess
import os
import psutil
import win32gui  
import win32con 
import time

# 打开程序，关闭程序
# 程序名称可以是可执行文件的名称，例如 "notepad.exe"。

def is_program_running(program_name):
    """
    检查指定名称的程序是否正在运行。

    :param program_name: 要检查的程序的名称，例如 "notepad.exe"
    :return: 如果程序正在运行返回 True，否则返回 False
    """
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] == program_name:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False


def open_program(program_path):
    """
    若指定程序未运行，则通过程序完整路径打开 Windows 程序。

    :param program_path: 要打开的程序的完整路径，例如 "C:\\Program Files\\SomeApp\\app.exe"
    """
    # 从路径中提取程序名
    program_name = os.path.basename(program_path)
    if is_program_running(program_name):
        print(f"{program_name} 已经在运行，无需再次打开。")
        return
    if not os.path.exists(program_path):
        print(f"指定的程序路径 {program_path} 不存在，请检查。")
        return
    try:
        # 直接使用程序路径打开程序
        subprocess.Popen(program_path)
        print(f"{program_name} 已成功打开")
    except Exception as e:
        print(f"打开 {program_path} 时出错: {e}")


def kill_program(program_name):
    """
    若指定程序正在运行，尝试优雅地结束该程序，若失败则使用 taskkill 强制终止。

    :param program_name: 要结束的程序的名称，例如 "notepad.exe"
    """
    if not is_program_running(program_name):
        print(f"{program_name} 未在运行，无需关闭。")
        return
    killed = False
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] == program_name:
                # 尝试正常关闭进程
                proc.terminate()
                gone, alive = psutil.wait_procs([proc], timeout=5)
                if alive:
                    # 如果正常关闭失败，则强制终止进程
                    proc.kill()
                    print(f"{program_name} 已被 psutil 强制终止")
                else:
                    print(f"{program_name} 已被 psutil 正常关闭")
                killed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    if not killed:
        try:
            # 使用 taskkill 强制终止进程
            subprocess.run(["taskkill", "/f", "/im", program_name], check=True)
            print(f"{program_name} 已被 taskkill 强制终止")
        except subprocess.CalledProcessError as e:
            print(f"使用 taskkill 结束 {program_name} 时出错: {e}")

def kill_program_by_title(window_title):
    """
    根据窗口标题关闭指定的窗口。

    :param window_title: 要关闭的窗口的标题
    """
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            if window_title in win32gui.GetWindowText(hwnd):
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    win32gui.EnumWindows(callback, None)

def open_cmd_and_run_py(py_file_path, window_title="新命令提示符窗口"):
    """
    打开 cmd 窗口并执行指定的 Python 文件。
    若传入的是相对路径，会自动转换为绝对路径。

    :param py_file_path: 要执行的 Python 文件的路径，可以是相对路径或绝对路径
    :param window_title: 要设置的 cmd 窗口标题，默认为 "新命令提示符窗口"
    """
    # 将相对路径转换为绝对路径
    if not os.path.isabs(py_file_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        py_file_path = os.path.join(base_dir, py_file_path)

    if not os.path.exists(py_file_path):
        print(f"文件 {py_file_path} 不存在，请检查路径。")
        return
    try:
        # 分开设置标题和执行 Python 脚本
        command = f"start cmd /k \"title {window_title} & python {py_file_path}\""
        subprocess.Popen(command, shell=True)
        print(f"已打开标题为 {window_title} 的 cmd 窗口并执行 {py_file_path}")
    except Exception as e:
        print(f"打开标题为 {window_title} 的 cmd 窗口执行 {py_file_path} 时出错: {e}")

if __name__ == "__main__":

    program_name = "wmain.exe"
    program_path = r"C:\\Wind\\Wind.NET.Client\\WindNET\\bin\\wmain.exe"
    open_program(program_path)
    time.sleep(5)

    # 关闭wind程序
    kill_program(program_name)
    time.sleep(5)

    # 关闭指定标题的 cmd 窗口，需要替换为实际的窗口标题
    kill_program_by_title("命令提示符")
    time.sleep(5)

    # 打开wind程序
    open_program(program_path)
    time.sleep(5)

    # 使用相对路径调用 test.py 并设置 cmd 窗口标题
    open_cmd_and_run_py("C:\\Users\\Top\\Desktop\\FuYing\\code\\test.py", "运行 test.py 的窗口")