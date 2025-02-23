import re
import imaplib
import email
from email.header import decode_header
import logging

class ReceiveEmail:
    '''
    接收信息
    '''
    def __init__(self, email_address, password, imap_server='imap.qq.com'):
        self.EMAIL = email_address
        self.PASSWORD = password
        self.IMAP_SERVER = imap_server

    def guess_charset(self, msg):
        charset = msg.get_charset()
        if charset is None:
            content_type = msg.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()
        return charset

    def decode_str(self, s):
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value

    def get_content(self, msg):
        if msg.is_multipart():
            parts = msg.get_payload()
            for part in parts:
                content = self.get_content(part)
                if content:
                    return content
        else:
            content_type = msg.get_content_type()
            if content_type == 'text/plain' or content_type == 'text/html':
                content = msg.get_payload(decode=True)
                if isinstance(content, bytes):
                    charset = self.guess_charset(msg)
                    if charset:
                        try:
                            content = content.decode(charset)
                        except (UnicodeDecodeError, LookupError):
                            pass
                    if isinstance(content, bytes):
                        try:
                            content = content.decode('utf-8')
                        except (UnicodeDecodeError, LookupError):
                            try:
                                content = content.decode('gbk')
                            except (UnicodeDecodeError, LookupError):
                                content = content.decode('gb2312', errors='ignore')
                return content
        return None

    def qe_main(self):
        # 连接到IMAP服务器:
        mail = imaplib.IMAP4_SSL(self.IMAP_SERVER)
        # 登录到服务器:
        mail.login(self.EMAIL, self.PASSWORD)
        # 选择收件箱:
        mail.select("inbox")
        # 搜索未读邮件:
        status, messages = mail.search(None, '(UNSEEN)')
        # 获取邮件编号列表:
        email_ids = messages[0].split()

        # 从最新邮件开始遍历
        for e_id in reversed(email_ids):
            status, msg_data = mail.fetch(e_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            content = self.get_content(msg)

            # 检查邮件是否包含验证码
            if content:
                # 有时候通知显示不全
                verification_code = re.findall(r'码为(\d+)', content, re.S)
                if verification_code:
                    print('短信验证码:', verification_code[0])
                    # 标记邮件为已读
                    mail.store(e_id, '+FLAGS', '\\Seen')  # 已读
                    mail.store(e_id, '+FLAGS', '\\Deleted')  # 删除
                    mail.expunge()
                    mail.logout()
                    return verification_code[0]

        # 关闭连接:
        mail.logout()
        print('未读取到邮件内容')
        return None

# 示例用法：
# email_address = 'your_email@example.com'
# password = 'your_password'
# receive_email = ReceiveEmail(email_address, password)
# verification_code = receive_email.qe_main()
# print(verification_code)
# if not verification_code:
#     print('未找到验证码')
