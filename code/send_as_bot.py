import requests
import json
import lark_oapi as lark
from lark_oapi.api.im.v1 import *

# 替换为你的 App ID 和 App Secret
APP_ID = "cli_a88b075ce993900b"
APP_SECRET = "bZn1pyDn7mnBjoTCrBS4vc1MAN5vjVy1"

def get_tenant_access_token(app_id, app_secret):
    """
    通过 App ID 和 App Secret 获取租户访问令牌
    :param app_id: 应用的 App ID
    :param app_secret: 应用的 App Secret
    :return: 租户访问令牌，如果获取失败则返回 None
    """
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    data = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            return result.get("tenant_access_token")
    print(f"获取 tenant_access_token 失败，错误码: {response.status_code}, 错误信息: {response.text}")
    return None


def get_chat_list(access_token):
    """
    获取群聊列表
    :param access_token: 租户访问令牌
    :return: 群聊列表，如果获取失败则返回 None
    """
    url = "https://open.feishu.cn/open-apis/im/v1/chats"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "page_size": 100
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            return result.get("data", {}).get("items", [])
    print(f"获取群聊列表失败，错误码: {response.status_code}, 错误信息: {response.text}")
    return None


def get_chat_id_by_name(access_token, chat_name):
    """
    通过群名获取群聊的 open_chat_id
    :param access_token: 租户访问令牌
    :param chat_name: 群聊名称
    :return: 群聊的 open_chat_id，如果未找到则返回 None
    """
    chat_list = get_chat_list(access_token)
    if chat_list:
        for chat in chat_list:
            if chat.get('name') == chat_name:
                return chat.get('chat_id')
    print(f"未找到名为 {chat_name} 的群聊")
    return None


def upload_image(image_path):
    """
    使用 lark SDK 上传图片
    :param image_path: 图片的绝对路径
    :return: 图片的 image_key，如果上传失败则返回 None
    """
    # 创建client
    client = lark.Client.builder() \
        .app_id(APP_ID) \
        .app_secret(APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    # 使用绝对路径打开文件，这里需要你将路径替换为实际的图片路径
    try:
        file = open(image_path, "rb")
    except Exception as e:
        print(f"打开图片文件时出错: {e}")
        return None

    # 构造请求对象
    request: CreateImageRequest = CreateImageRequest.builder() \
        .request_body(CreateImageRequestBody.builder()
                      .image_type("message")
                      .image(file)
                      .build()) \
        .build()

    # 发起请求
    response: CreateImageResponse = client.im.v1.image.create(request)

    # 关闭文件
    file.close()

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.im.v1.image.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return None

    # 处理业务结果
    return response.data.image_key


def send_message(access_token, open_chat_id, message_data):
    """
    发送消息到指定的群聊
    :param access_token: 租户访问令牌
    :param open_chat_id: 目标群聊的 open_chat_id
    :param message_data: 消息内容
    :return: 发送结果，如果发送失败则返回 None
    """
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    # 复制消息数据，避免修改原始数据
    data_to_send = message_data.copy()
    # 确保 content 是字符串
    if isinstance(data_to_send.get("content"), dict):
        data_to_send["content"] = json.dumps(data_to_send["content"])

    response = requests.post(url, headers=headers, json={
        "receive_id": open_chat_id,
        "content": data_to_send["content"],
        "msg_type": data_to_send["msg_type"]
    })
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            return result
    print(f"消息发送失败，错误码: {response.status_code}, 错误信息: {response.text}")
    return None


def send_group_message(chat_name, is_image, content):
    """
    通过群名、是否发送图片标志和内容发送群消息
    :param chat_name: 群聊名称
    :param is_image: 是否发送图片，True 表示发送图片，False 表示发送文本
    :param content: 若 is_image 为 True，则为图片的绝对路径；若为 False，则为文本内容
    :return: 发送结果，如果发送失败则返回 None
    """
    access_token = get_tenant_access_token(APP_ID, APP_SECRET)
    if not access_token:
        print("无法获取访问令牌，程序终止。")
        return None

    open_chat_id = get_chat_id_by_name(access_token, chat_name)
    if not open_chat_id:
        return None

    if is_image:
        image_key = upload_image(content)
        if image_key:
            message_data = {
                "msg_type": "image",
                "content": {
                    "image_key": image_key
                }
            }
        else:
            print("未获取到图片 key，无法发送图片消息。")
            return None
    else:
        message_data = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }

    return send_message(access_token, open_chat_id, message_data)


if __name__ == "__main__":
    # 示例调用
    # 发送文本消息
    send_group_message("富赢", False, "这是一条文本消息")
    # 发送图片消息
    send_group_message("富赢", True, "C:\\Users\\Top\\Desktop\\295.jpg")