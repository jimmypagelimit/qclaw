import sqlite3, datetime

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

# 先看看表结构
cur.execute('PRAGMA table_info(albums)')
cols = [r[1] for r in cur.fetchall()]
print('albums表字段:', cols)

# 检查专辑是否已存在
cur.execute("SELECT album_id FROM albums WHERE album_name=? AND artist=?", ('外面是夏天', '碎梦飞跃'))
existing = cur.fetchone()

if existing:
    album_id = existing[0]
    print(f'专辑已存在，ID={album_id}')
else:
    # 用正确的字段插入
    cur.execute('''INSERT INTO albums (album_name, artist, release_year, style)
                   VALUES (?, ?, ?, ?)''',
                ('外面是夏天', '碎梦飞跃', 2026, 'Indie Rock'))
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
