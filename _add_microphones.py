import sqlite3, datetime

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

# 查重
cur.execute("SELECT album_id FROM albums WHERE album_name=? AND artist=?",
            ('The Glow, Pt. 2', 'The Microphones'))
existing = cur.fetchone()

if existing:
    album_id = existing[0]
    print(f'专辑已存在，ID={album_id}')
else:
    cur.execute('''INSERT INTO albums (album_name, artist, release_year, style, country, region)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                ('The Glow, Pt. 2', 'The Microphones', 2001, 'Lo-Fi Indie', 'US', '欧美'))
    conn.commit()
    album_id = cur.lastrowid
    print(f'新专辑入库，ID={album_id}')

# 2026年听歌记录
today = datetime.date.today().isoformat()
cur.execute('INSERT INTO listen_history (album_id, listen_date, listen_year) VALUES (?, ?, ?)',
            (album_id, today, 2026))
conn.commit()
print(f'已记录：{today} 听歌1次')

conn.close()
