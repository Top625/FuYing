import requests
import os
import json  # 导入 json 模块

# 替换为你的 App ID 和 App Secret
APP_ID = "cli_a88b075ce993900b"
APP_SECRET = "bZn1pyDn7mnBjoTCrBS4vc1MAN5vjVy1"

# 替换为你的图片绝对路径
IMAGE_PATH = 'C:\\Users\\Top\\Desktop\\295.jpg'

if not os.path.exists(IMAGE_PATH):
    print(f"图片文件 {IMAGE_PATH} 不存在，请检查路径。")
else:
    # 替换为你的目标群聊的 open_chat_id
    OPEN_CHAT_ID = "oc_9b02e7b804f018c1f165a900410d1469"
    print(f"图片路径: {IMAGE_PATH}")  # 打印图片路径用于检查

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

def upload_image(access_token, image_path):
    if not os.path.exists(image_path):
        print(f"图片文件 {image_path} 不存在，请检查路径。")
        return None
    url = "https://open.feishu.cn/open-apis/im/v1/images?image_type=message"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    print(f"请求 URL: {url}")
    print(f"请求头: {headers}")
    try:
        with open(image_path, 'rb') as f:
            files = {
                'image': f
            }
            response = requests.post(url, headers=headers, files=files)
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    return result.get("data", {}).get("image_key")
    except Exception as e:
        print(f"打开图片文件时出错: {e}")
    print(f"图片上传失败，错误码: {response.status_code}, 错误信息: {response.text}")
    return None

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

# 获取租户访问令牌
access_token = get_tenant_access_token(APP_ID, APP_SECRET)
print(f"获取到的访问令牌: {access_token}")  # 打印令牌用于检查
if not access_token:
    print("无法获取访问令牌，程序终止。")
else:
    # 上传图片
    image_key ='img_v3_02lf_61035b1f-182a-4e5d-826f-d546a157854g'

    if image_key:
        # 构造仅包含图片的消息内容
        message_data = {
            "msg_type": "image",
            "content": {
                "image_key": image_key
            }
        }
    else:
        print("未获取到图片 key，无法发送图片消息。")
        message_data = None

    if message_data:
        # 发送消息
        send_message(access_token, OPEN_CHAT_ID, message_data)
