import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# 搜保罗相关
print('=== 搜 Paul McCartney ===')
cur.execute("SELECT album_id, album_name, artist, release_year, total_listen_count FROM albums WHERE artist LIKE '%Paul%' OR artist LIKE '%McCartney%'")
for r in cur.fetchall():
    print(r)

print('\n=== 搜 Dungeon ===')
cur.execute("SELECT album_id, album_name, artist, release_year FROM albums WHERE album_name LIKE '%Dungeon%'")
for r in cur.fetchall():
    print(r)

print('\n=== 搜 2026年专辑 ===')
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE release_year = 2026 ORDER BY album_id")
for r in cur.fetchall():
    print(r)

conn.close()
