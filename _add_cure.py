import sqlite3, datetime

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

# 检查专辑是否已存在
cur.execute("SELECT album_id FROM albums WHERE album_name=? AND artist=?", 
            ('Songs of a Lost World', 'The Cure'))
existing = cur.fetchone()

if existing:
    album_id = existing[0]
    print(f'专辑已存在，ID={album_id}')
else:
    # 插入新专辑
    cur.execute('''INSERT INTO albums (album_name, artist, release_year, style, country, region)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                ('Songs of a Lost World', 'The Cure', 2024, 'Post-Punk', 'UK', '欧美'))
    conn.commit()
    album_id = cur.lastrowid
    print(f'新专辑入库，ID={album_id}')

# 插入听歌记录
today = datetime.date.today().isoformat()
cur.execute('INSERT INTO listen_history (album_id, listen_date, listen_year) VALUES (?, ?, ?)',
            (album_id, today, 2026))
conn.commit()
print(f'已记录听歌：{today}')

conn.close()
