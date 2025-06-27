import pyautogui
import time
from pynput.mouse import Listener

# 标记是否是第一次点击
first_click = True

# 定义鼠标点击时的回调函数
def on_click(x, y, button, pressed):
    global first_click
    if pressed:
        print(f"鼠标 {button} 键在位置 X={x}, Y={y} 处被点击")
        # if first_click:
        #     # 第一次点击后执行操作
        #     pyautogui.click(1750, 980)
        #     time.sleep(1)
        #     pyautogui.typewrite('MR')
        #     time.sleep(1)
        #     pyautogui.click(1630, 650)
        #     first_click = False  # 标记第一次点击已完成

# 启动鼠标监听器
listener = Listener(on_click=on_click)
listener.start()

try:
    while True:
        x, y = pyautogui.position()
        print(f"\r鼠标位置: X={x}, Y={y}", end="")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n程序结束")
    listener.stop()  # 停止监听器