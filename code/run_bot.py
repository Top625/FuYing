# 从 send_as_bot 模块导入 send_group_message 函数
from send_as_bot import send_group_message

if __name__ == "__main__":
    # 发送文本消息示例
    text_result = send_group_message("张浩", False, "这是从 run_bot.py 发送的文本消息。")
    if text_result:
        print("文本消息发送成功")
    else:
        print("文本消息发送失败")

    # 发送图片消息示例
    image_result = send_group_message("张浩", True, "C:\\Users\\Top\\Desktop\\295.jpg")
    if image_result:
        print("图片消息发送成功")
    else:
        print("图片消息发送失败")