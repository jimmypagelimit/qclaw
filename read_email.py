#!/usr/bin/env python3
import imaplib, email, sys
from email.header import decode_header
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

mail = imaplib.IMAP4_SSL('imap.163.com', 993)
mail.login('15206651142@163.com', 'WWPkQKMPCMP4TPpx')

# 先列出所有文件夹
status, folders = mail.list()
print('邮箱文件夹:')
for f in folders[:10]:
    print(f'  {f.decode()}')

# 选择收件箱
status, count = mail.select('INBOX')
print(f'\n收件箱邮件数: {count}')

status, msgs = mail.search(None, 'ALL')
ids = msgs[0].split()

# 检查最近 20 封
keywords = ['car seat', 'headrest', 'matador', 'bandcamp']

found = []
for mid in ids[-20:]:
    status, data = mail.fetch(mid, '(RFC822)')
    msg = email.message_from_bytes(data[0][1])
    
    subject_raw = msg.get('Subject', '')
    subject = ''
    for part, enc in decode_header(subject_raw):
        if isinstance(part, bytes):
            subject += part.decode(enc or 'utf-8', errors='replace')
        else:
            subject += part
    
    sender = msg.get('From', '')
    date = msg.get('Date', '')
    
    text = (subject + ' ' + sender).lower()
    if any(kw in text for kw in keywords):
        found.append((sender, subject, date, msg))
        print(f'\n--- 找到 ---')
        print(f'From: {sender}')
        print(f'Subject: {subject}')
        print(f'Date: {date}')

if not found:
    print('\n未找到 Car Seat Headrest 相关邮件')
    print('\n最近 10 封邮件:')
    for mid in ids[-10:]:
        status, data = mail.fetch(mid, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        subject_raw = msg.get('Subject', '')
        subject = ''
        for part, enc in decode_header(subject_raw):
            if isinstance(part, bytes):
                subject += part.decode(enc or 'utf-8', errors='replace')
            else:
                subject += part
        sender = msg.get('From', '')
        print(f'  {sender} | {subject}')

mail.logout()
