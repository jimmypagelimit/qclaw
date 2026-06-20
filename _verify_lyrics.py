import os, sqlite3, glob

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'

conn = sqlite3.connect(DB)
conn.execute('PRAGMA journal_mode=WAL')
c = conn.cursor()

# 检查嘎调 id=444 的曲目歌词路径
c.execute("SELECT track_name, lyrics_text_path FROM tracks WHERE album_id=444 AND lyrics_text_path IS NOT NULL")
rows = c.fetchall()
print(f'Tracks with lyrics paths in DB: {len(rows)}')
for r in rows:
    print(f'  {r[0]}: {r[1]}')

# 检查文件系统
print('\nLyrics files:')
found = []
for root, dirs, files in os.walk(LYRICS):
    for f in files:
        if f.endswith('.txt') or f.endswith('.lrc'):
            full = os.path.join(root, f)
            size = os.path.getsize(full)
            found.append(full)
            print(f'  {os.path.basename(os.path.dirname(full))}/{f} ({size}b)')

print(f'\nTotal files found: {len(found)}')

# 检查数据库中其他缺歌词的专辑
print('\n其他待补专辑的网易云ID:')
targets = [
    (370393422, '东京酒吐座', 'Remains'),
    (3070021, '葬尸湖', '冬霾'),
    (263245626, '施鑫文月', '灰太阳'),
]
for wy_id, artist, album in targets:
    c.execute("SELECT album_id, album_name, artist FROM albums WHERE album_name=? OR album_name=?", [album, album])
    row = c.fetchone()
    if row:
        print(f'  {artist} - {album} (wy:{wy_id}) -> DB id={row[0]} {row[1]}')
    else:
        print(f'  {artist} - {album} (wy:{wy_id}) -> NOT in DB')
conn.close()
