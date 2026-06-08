import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()

# albums_2026 的专辑名列表
cur.execute("SELECT album_id, album_name, artist, total_listen_count FROM albums_2026 ORDER BY total_listen_count DESC LIMIT 20")
print("=== albums_2026 表 ===")
for r in cur.fetchall():
    print(f"  id={r[0]}, {r[1]} - {r[2]}, count={r[3]}")

# 检查 albums_2026 的 album_id 3 对应什么
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE album_id = 3")
print(f"\nalbums 表 id=3: {cur.fetchone()}")

# 检查 albums_2026 的 album_id 和 albums 的映射
# albums_2026 是独立自增 ID，不对应 albums 表
# 看看 albums_2026 id=1 在 albums 表叫什么
for aid in [1, 3, 11, 13, 15, 50, 55, 91, 108, 111, 115, 181]:
    cur.execute("SELECT album_name, artist FROM albums_2026 WHERE album_id=?", (aid,))
    y = cur.fetchone()
    cur.execute("SELECT album_name, artist FROM albums WHERE album_id=?", (aid,))
    t = cur.fetchone()
    if y and t:
        print(f"  id={aid}: 2026表={y[0]}-{y[1]} | 总表={t[0]}-{t[1]}")

conn.close()
