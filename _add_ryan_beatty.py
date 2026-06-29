"""入库 Ryan Beatty - Sweet Fortune (2026)"""
import sqlite3, urllib.request, os, json

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVERS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 检查艺人是否存在
cur.execute("SELECT artist_id FROM artists WHERE name = 'Ryan Beatty' LIMIT 1")
row = cur.fetchone()
if row:
    artist_id = row[0]
    print(f'艺人已存在 artist_id={artist_id}')
else:
    cur.execute("""
        INSERT INTO artists (name, country, is_active)
        VALUES ('Ryan Beatty', 'US', 1)
    """)
    artist_id = cur.lastrowid
    print(f'新增艺人 artist_id={artist_id}')

# 检查专辑是否已存在（判重：album_name + artist）
cur.execute(
    "SELECT album_id FROM albums WHERE album_name=? AND artist=?",
    ('Sweet Fortune', 'Ryan Beatty')
)
row = cur.fetchone()
if row:
    print(f'专辑已存在 album_id={row[0]}，跳过插入')
    album_id = row[0]
else:
    cur.execute("""
        INSERT INTO albums (artist, album_name, release_year,
                           release_mbid, cover_image_url, status, artist_id)
        VALUES (?, ?, ?, ?, ?, 'active', ?)
    """, (
        'Ryan Beatty',
        'Sweet Fortune',
        2026,
        'bab213e5-a0fe-42a2-b402-de1469203901',
        '',
        artist_id
    ))
    album_id = cur.lastrowid
    print(f'新增专辑 album_id={album_id}')

# 收听记录（1次，今天）
cur.execute("""
    INSERT INTO listen_history (album_id, listen_date, listen_year, notes, source)
    VALUES (?, date('now'), strftime('%Y', 'now'), '入库', 'manual')
""", (album_id,))
lh_id = cur.lastrowid
print(f'收听记录 id={lh_id}')

conn.commit()
conn.close()

# 下载封面
cover_url = 'https://dn711002.ca.archive.org/0/items/mbid-d65718b1-1715-4387-b899-65b56654e853/mbid-d65718b1-1715-4387-b899-65b56654e853-45286472631.jpg'
cover_file = os.path.join(COVERS_DIR, f'{album_id}-Ryan Beatty-Sweet Fortune.jpg')
try:
    urllib.request.urlretrieve(cover_url, cover_file)
    size = os.path.getsize(cover_file)
    print(f'封面下载成功: {size//1024}KB')

    # 更新数据库封面路径
    conn2 = sqlite3.connect(DB)
    cur2 = conn2.cursor()
    cur2.execute(
        "UPDATE albums SET cover_image_url=? WHERE album_id=?",
        (f'/covers/{album_id}-Ryan Beatty-Sweet Fortune.jpg', album_id)
    )
    conn2.commit()
    conn2.close()
    print('封面路径已更新')
except Exception as e:
    print(f'封面下载失败: {e}')

# 插入曲目（第10首截断未知，搜索补全）
tracks = [
    (1, 'Phantom',         223000, '6f8dd349-8136-4589-a7f6-2bb02b16b038'),
    (2, 'White Lightning', 265000, '99678552-3b14-4792-8886-0dda262b2162'),
    (3, 'Virtuoso',        222000, '3326683a-82d0-4bd3-acdd-d938c40b3fb5'),
    (4, 'Secret Language', 234000, '15a18b9e-98bf-4968-aea5-1eaa11416203'),
    (5, 'Sweet Fortune',   176000, '5ad678e3-795e-4b8e-a6c3-94808ee12263'),
    (6, 'Too Many Ways',   234000, 'ce938eb8-5015-44a6-bb21-ec2deff69a27'),
    (7, 'Delancey',        222000, '7941c674-9566-471a-b101-ffffd879fdf0'),
    (8, 'Annie, Anything', 213000, '7e44ed5f-fdbb-48c3-ab8d-c61609418814'),
    (9, 'Dust',            189000, 'e96decd7-b7cb-4d87-82d1-df3626db5738'),
]

conn3 = sqlite3.connect(DB)
cur3 = conn3.cursor()
for num, title, duration, mbid in tracks:
    cur3.execute(
        "INSERT INTO tracks (album_id, track_name, track_number, duration, source) VALUES (?,?,?,?,'musicbrainz')",
        (album_id, title, num, duration)
    )
conn3.commit()
conn3.close()
print(f'已插入 {len(tracks)} 首曲目（track_10 待补）')

print(f'\n入库完成: album_id={album_id}')
