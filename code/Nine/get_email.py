import imaplib
import email
from email.header import decode_header
import socket

# 配置邮箱信息
EMAIL = "zhanghao@egicleasing.com" 
PASSWORD = "vVorEBOM3tSdzTcG"      
IMAP_SERVER = "imap.qiye.aliyun.com"
IMAP_PORT = 993  

try:
    # 连接 IMAP 服务器，设置超时时间为 10 秒，并指定端口
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, port=IMAP_PORT, timeout=10)
    # 尝试登录邮箱
    mail.login(EMAIL, PASSWORD)
    print("登录成功")
    mail.select("INBOX")  # 选择收件箱

    # 搜索所有邮件
    status, messages = mail.search(None, "ALL")
    print(messages) 
    if status == "OK":
        for msg_id in messages[0].split():
            status, data = mail.fetch(msg_id, "(RFC822)")  # 获取原始邮件
            if status == "OK":
                raw_email = data[0][1]
                email_message = email.message_from_bytes(raw_email)
                print("邮件ID:", msg_id)  # 打印邮件ID，方便调试，如需要，可以注释掉这行代码

                # 解析邮件主题（处理编码）
                subject_parts = decode_header(email_message["Subject"])
                subject = ""
                for part, encoding in subject_parts:
                    if isinstance(part, bytes):
                        try:
                            if encoding:
                                subject += part.decode(encoding)
                            else:
                                # 尝试多种编码
                                encodings = ['utf-8', 'gbk', 'gb2312']
                                for enc in encodings:
                                    try:
                                        subject += part.decode(enc)
                                        break
                                    except UnicodeDecodeError:
                                        continue
                        except UnicodeDecodeError:
                            # 如果所有编码尝试都失败，使用原始字节的 repr 形式
                            subject += repr(part)
                    else:
                        subject += part

                # 获取发件人
                from_ = email_message["From"]
                print("发件人:", from_)
                print("主题:", subject)

                # 提取正文（纯文本部分）
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        raw_body = part.get_payload(decode=True)
                        encodings = ['utf-8', 'gbk', 'gb2312']
                        body = None
                        for enc in encodings:
                            try:
                                body = raw_body.decode(enc)
                                break
                            except UnicodeDecodeError:
                                continue
                        if body is not None:
                            print("正文:", body)  # 打印全部正文内容
                        else:
                            print("无法解码邮件正文，请检查邮件编码。")
                        break
except imaplib.IMAP4.error as e:
    print(f"登录失败: {e}，请检查邮箱账号、密码、IMAP 服务设置。")
except socket.timeout:
    print("连接 IMAP 服务器超时，请检查服务器地址和网络连接。")
except TimeoutError:
    print("连接 IMAP 服务器超时，请检查服务器地址和网络连接。")
finally:
    if 'mail' in locals():
        mail.logout()