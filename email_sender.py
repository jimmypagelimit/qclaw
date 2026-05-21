#!/usr/bin/env python3
"""公共邮件发送模块"""
import smtplib, sys, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SMTP_HOST = "smtp.163.com"
SMTP_PORT = 465
SMTP_USER = "15206651142@163.com"
SMTP_PASS = "WWPkQKMPCMP4TPpx"
KINDLE_EMAIL = "JIMMYPAGELIMIT_ACFYFR@KINDLE.com"


def send_email(to, subject, body, filepath=None, filename=None):
    """发送邮件，可选附件"""
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    if filepath and os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        name = filename or os.path.basename(filepath)
        part.add_header('Content-Disposition', f'attachment; filename="{name}"')
        msg.attach(part)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to, msg.as_string())

    size = os.path.getsize(filepath) // 1024 if filepath and os.path.exists(filepath) else 0
    print(f"✅ 发送成功 -> {to} ({size}KB)")
    return True


def send_kindle(filepath, filename=None, subject="Convert"):
    """发送文件到 Kindle"""
    return send_email(KINDLE_EMAIL, subject, "Kindle 文档", filepath, filename)


# 测试
if __name__ == "__main__":
    send_email("15206651142@163.com", "测试", "邮件模块测试")
