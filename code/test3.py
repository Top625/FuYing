from lark_oapi import im


import requests
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

access_token = get_tenant_access_token(APP_ID, APP_SECRET)
print(f"获取到的访问令牌: {access_token}")  # 打印令牌用于检查
if not access_token:
    print("无法获取访问令牌，程序终止。")
else:
    # 获取群聊列表
    chat_list = get_chat_list(access_token)
    if chat_list:
        print("群聊列表:")
        for chat in chat_list:
            print(f"群聊名称: {chat.get('name')}, OPEN_CHAT_ID: {chat.get('chat_id')}")
    else:
        print("未获取到群聊列表。")

    # 这里可以手动选择 OPEN_CHAT_ID 并赋值
    OPEN_CHAT_ID = "your_open_chat_id"