import requests
import json
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
import os

def send_group_message(chat_name, is_image, content):
    """
    通过群名、是否发送图片标志和内容发送群消息
    :param chat_name: 群聊名称
    :param is_image: 是否发送图片，True 表示发送图片，False 表示发送文本
    :param content: 若 is_image 为 True，则为图片的绝对路径；若为 False，则为文本内容
    :return: 发送结果，如果发送失败则返回 None
    """
    # 获取租户访问令牌
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    APP_ID = "cli_a88b075ce993900b"
    APP_SECRET = "bZn1pyDn7mnBjoTCrBS4vc1MAN5vjVy1"
    data = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            access_token = result.get("tenant_access_token")
        else:
            print(f"获取 tenant_access_token 失败，错误码: {response.status_code}, 错误信息: {response.text}")
            return None
    else:
        print(f"获取 tenant_access_token 失败，错误码: {response.status_code}, 错误信息: {response.text}")
        return None

    # 获取群聊列表
    chat_list_url = "https://open.feishu.cn/open-apis/im/v1/chats"
    chat_list_headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "page_size": 100
    }
    chat_list_response = requests.get(chat_list_url, headers=chat_list_headers, params=params)
    if chat_list_response.status_code == 200:
        chat_list_result = chat_list_response.json()
        if chat_list_result.get("code") == 0:
            chat_list = chat_list_result.get("data", {}).get("items", [])
        else:
            print(f"获取群聊列表失败，错误码: {chat_list_response.status_code}, 错误信息: {chat_list_response.text}")
            return None
    else:
        print(f"获取群聊列表失败，错误码: {chat_list_response.status_code}, 错误信息: {chat_list_response.text}")
        return None

    # 通过群名获取群聊的 open_chat_id
    open_chat_id = None
    for chat in chat_list:
        if chat.get('name') == chat_name:
            open_chat_id = chat.get('chat_id')
            break
    if not open_chat_id:
        print(f"未找到名为 {chat_name} 的群聊")
        return None

    if is_image:
        if not os.path.isfile(content):
            print(f"指定的图片文件 {content} 不存在，请检查路径。")
            return None
        # 创建client
        client = lark.Client.builder() \
            .app_id(APP_ID) \
            .app_secret(APP_SECRET) \
            .log_level(lark.LogLevel.DEBUG) \
            .build()

        try:
            with open(content, "rb") as file:
                # 构造请求对象
                request: CreateImageRequest = CreateImageRequest.builder() \
                    .request_body(CreateImageRequestBody.builder() \
                                  .image_type("message") \
                                  .image(file) \
                                  .build()) \
                    .build()

                # 发起请求
                response: CreateImageResponse = client.im.v1.image.create(request)

                # 处理失败返回
                if not response.success():
                    lark.logger.error(
                        f"client.im.v1.image.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
                    return None

                image_key = response.data.image_key
        except Exception as e:
            print(f"打开图片文件时出错: {e}")
            return None

        message_data = {
            "msg_type": "image",
            "content": {
                "image_key": image_key
            }
        }
    else:
        message_data = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }

    # 发送消息
    send_url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    send_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    # 复制消息数据，避免修改原始数据
    data_to_send = message_data.copy()
    # 确保 content 是字符串
    if isinstance(data_to_send.get("content"), dict):
        data_to_send["content"] = json.dumps(data_to_send["content"])

    send_response = requests.post(send_url, headers=send_headers, json={
        "receive_id": open_chat_id,
        "content": data_to_send["content"],
        "msg_type": data_to_send["msg_type"]
    })
    if send_response.status_code == 200:
        send_result = send_response.json()
        if send_result.get("code") == 0:
            return send_result
    print(f"消息发送失败，错误码: {send_response.status_code}, 错误信息: {send_response.text}")
    return None


if __name__ == "__main__":
    # 示例调用
    # 发送文本消息
    send_group_message("浩", False, "这是一条文本消息")
    # 发送图片消息
    send_group_message("浩", True, "C:\\Users\\Top\\Desktop\\295.jpg")