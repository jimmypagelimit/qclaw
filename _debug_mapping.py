import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()

# 检查 listen_history 中 album_id=3 的原始数据
cur.execute("SELECT id, album_id, listen_date, listen_year FROM listen_history WHERE album_id=3 AND listen_year=2026")
print("=== listen_history album_id=3 (2026) ===")
for r in cur.fetchall():
    print(r)

# albums 表 id=3 是什么
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE album_id=3")
print(f"\nalbums id=3: {cur.fetchone()}")

# 看看海朋森-沙之小说在 albums 表的 id
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE album_name LIKE '%沙%' OR album_name LIKE '%She Came%'")
print(f"\n海朋森在albums表: {cur.fetchall()}")

# 对比：albums_2026 有但 albums 没有/不对应的专辑
cur.execute("SELECT album_name, artist FROM albums_2026 WHERE album_id=3")
print(f"\nalbums_2026 id=3: {cur.fetchone()}")

# 更广泛检查：listen_history 2026 的 album_id 对应的专辑是否真的在 2026 年听过
# 对比 albums_2026 的专辑列表
cur.execute("SELECT album_name, artist FROM albums_2026 ORDER BY total_listen_count DESC")
y2026 = cur.fetchall()

# 看看这些专辑在 albums 表里的 id
for name, artist in y2026[:5]:
    cur.execute("SELECT album_id FROM albums WHERE album_name=? AND artist=?", (name, artist))
    r = cur.fetchone()
    print(f"  '{name}' by '{artist}': albums.id={r[0] if r else 'NOT FOUND'}")

conn.close()
