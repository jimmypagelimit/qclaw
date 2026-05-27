# -*- coding: utf-8 -*-
import sqlite3
import urllib.request
import os
import ssl
import json
import subprocess

# 数据库路径
db_path = r'\\10.0.2.4\qemu\原创计划\music'
covers_dir = r'\\10.0.2.4\qemu\原创计划\covers'

# 连接数据库
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 查最大album_id
c.execute('SELECT MAX(album_id) FROM albums')
max_id = c.fetchone()[0] or 0
new_id = max_id + 1
print(f'New album_id: {new_id}')

# 插入albums总表
c.execute('''INSERT INTO albums (album_id, album_name, artist, release_year, genre, rating, total_listen_count, country)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
(new_id, 'Teen of Denial (Joe''s Story)', 'Car Seat Headrest', '2026', 'Indie Rock / Power Pop', 2.35, 2, 'US'))

# 插入albums_2026表
c.execute('SELECT MAX(album_id) FROM albums_2026')
max_2026_id = c.fetchone()[0] or 0
new_2026_id = max_2026_id + 1
c.execute('''INSERT INTO albums_2026 (album_id, album_name, artist, release_year, genre, rating, total_listen_count, country)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
(new_2026_id, 'Teen of Denial (Joe''s Story)', 'Car Seat Headrest', '2026', 'Indie Rock / Power Pop', 2.35, 2, 'US'))

conn.commit()
print('Database updated')

# 下载封面
cover_url = 'https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/48/42/77/484277b5-408a-05f3-1ddc-14f6b15bba80/191401224772.png/600x600bb.jpg'
os.makedirs(covers_dir, exist_ok=True)
cover_path = os.path.join(covers_dir, f'{new_id}-Car_Seat_Headrest-Teen_of_Denial.jpg')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
img = urllib.request.urlopen(cover_url, timeout=30, context=ctx).read()
with open(cover_path, 'wb') as f:
    f.write(img)
print(f'Cover saved: {len(img)} bytes')

conn.close()
