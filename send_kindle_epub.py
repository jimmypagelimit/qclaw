#!/usr/bin/env python3
"""发送 EPUB 到 Kindle"""
import smtplib, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SMTP_HOST = "smtp.163.com"
SMTP_PORT = 465
SMTP_USER = "15206651142@163.com"
SMTP_PASS = "WWPkQKMPCMP4TPpx"

epub_path = r"C:\Users\15206\.qclaw\workspace\wechat_article.epub"

msg = MIMEMultipart()
msg['From'] = SMTP_USER
msg['To'] = "JIMMYPAGELIMIT_ACFYFR@KINDLE.com"
msg['Subject'] = "Convert"
msg.attach(MIMEText("微信文章 EPUB", 'plain', 'utf-8'))

with open(epub_path, 'rb') as f:
    part = MIMEBase('application', 'epub+zip')
    part.set_payload(f.read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', 'attachment; filename="wechat_article.epub"')
msg.attach(part)

print("发送到 Kindle...")
with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
    server.login(SMTP_USER, SMTP_PASS)
    server.sendmail(SMTP_USER, "JIMMYPAGELIMIT_ACFYFR@KINDLE.com", msg.as_string())
print("✅ 发送成功！")
