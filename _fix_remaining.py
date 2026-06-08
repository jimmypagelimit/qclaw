import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()

# 修复1: 海朋森 [Hiperson] - 专辑名在 albums 表已改
# 查看 albums 表中海朋森的记录
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE artist LIKE '%海朋森%' OR artist LIKE '%Hiperson%' OR artist LIKE '%446%'")
for r in cur.fetchall():
    print(r)

# 查看 albums_2026 中 id=33
cur.execute("SELECT album_id, album_name, artist, total_listen_count FROM albums_2026 WHERE album_id=33")
print("\nalbums_2026 id=33:", cur.fetchone())

# 查看 albums id=446
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE album_id=446")
print("albums id=446:", cur.fetchone())

# 修复2: 韩寒/何某某 - 查找
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE artist LIKE '%何%' OR album_name LIKE '%无政府%'")
for r in cur.fetchall():
    print(r)

# 查看 albums_2026 id=195
cur.execute("SELECT album_id, album_name, artist, total_listen_count FROM albums_2026 WHERE album_id=195")
print("\nalbums_2026 id=195:", cur.fetchone())

conn.close()
