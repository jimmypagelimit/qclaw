import sqlite3, datetime

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

# 专辑已入库 ID=600
album_id = 600

# 插入曲目
tracks = [
    ('雨', 1),
    ('与我交谈', 2),
    ('谢谢你', 3),
    ('后记', 4),
    ('不陌生的人', 5),
    ('空港曲', 6),
    ('知道', 7),
    ('落雁', 8),
    ('郭源潮', 9),
    ('再想想', 10),
    ('別', 11)
]

for title, pos in tracks:
    cur.execute('SELECT id FROM tracks WHERE album_id=? AND track_name=?', (album_id, title))
    if not cur.fetchone():
        cur.execute('INSERT INTO tracks (album_id, track_name, track_number) VALUES (?, ?, ?)',
                    (album_id, title, pos))

conn.commit()
print(f'曲目入库完成：{len(tracks)} 首')
conn.close()
