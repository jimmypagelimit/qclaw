#!/usr/bin/env python3
"""用 Python smtplib 发送带附件的邮件"""
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SMTP_HOST = "smtp.163.com"
SMTP_PORT = 465
SMTP_USER = "15206651142@163.com"
SMTP_PASS = "WWPkQKMPCMP4TPpx"

def send_email(to, subject, body, attach_path=None):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    if attach_path and os.path.exists(attach_path):
        with open(attach_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        filename = os.path.basename(attach_path)
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        msg.attach(part)
        print(f"附件: {filename} ({os.path.getsize(attach_path)} bytes)")

    print(f"连接 {SMTP_HOST}:{SMTP_PORT}...")
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to, msg.as_string())
    print(f"✅ 发送成功 → {to}")

send_email(
    to="15206651142@163.com",
    subject="测试文档 - MOBI格式电子书",
    body="这是测试邮件，附件为 MOBI 格式电子书。\n\n由小飞自动发送。",
    attach_path=r"C:\Users\15206\.qclaw\workspace\test_book.mobi"
)
