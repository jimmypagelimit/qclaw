#!/usr/bin/env python3
"""发送 EPUB 到 Kindle"""
import smtplib, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

epub_path = r"C:\Users\15206\.qclaw\workspace\wechat_article_v2.epub"

msg = MIMEMultipart()
msg['From'] = "15206651142@163.com"
msg['To'] = "JIMMYPAGELIMIT_ACFYFR@KINDLE.com"
msg['Subject'] = "Convert"
msg.attach(MIMEText("微信文章 EPUB（含图片）", 'plain', 'utf-8'))

with open(epub_path, 'rb') as f:
    part = MIMEBase('application', 'epub+zip')
    part.set_payload(f.read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', 'attachment; filename="wechat_article.epub"')
msg.attach(part)

print(f"文件大小: {__import__('os').path.getsize(epub_path)//1024}KB")
print("发送到 Kindle...")
with smtplib.SMTP_SSL("smtp.163.com", 465) as server:
    server.login("15206651142@163.com", "WWPkQKMPCMP4TPpx")
    server.sendmail("15206651142@163.com", "JIMMYPAGELIMIT_ACFYFR@KINDLE.com", msg.as_string())
print("✅ 发送成功！")
