import sqlite3

conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()

# 查老表里缺失的两张专辑的 total_listen_count
print("=== 老表 albums_2026 缺失条目 ===")
cur.execute("SELECT album_name, artist, total_listen_count FROM albums_2026 WHERE album_name LIKE '%不要别的历史%' OR album_name LIKE '%Teen of Denial%' OR album_name LIKE '%Joes Story%'")
rows = cur.fetchall()
for row in rows:
    print(f"  {row[0]} - {row[1]}: count={row[2]}")

# 查我不要别的历史在总表的情况
print("\n=== 我不要别的历史 总表 ===")
cur.execute("SELECT album_id, album_name, artist, total_listen_count FROM albums WHERE album_name LIKE '%不要别的历史%'")
r = cur.fetchone()
if r:
    print(f"  album_id={r[0]}, {r[1]} - {r[2]}, total={r[3]}")
    cur.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=? AND listen_year=2026", (r[0],))
    cnt = cur.fetchone()[0]
    print(f"  2026 listen_history: {cnt} 条")
else:
    print("  总表未找到")

# 查Teen of Denial (Joes Story) 是否总表有
print("\n=== Teen of Denial (Joes Story) 总表 ===")
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE album_name LIKE '%Joes Story%' OR album_name LIKE '%Teen of Denial%'")
rows = cur.fetchall()
if rows:
    for r in rows:
        print(f"  找到: album_id={r[0]}, {r[1]} - {r[2]}")
else:
    print("  总表未找到，需要新增")

conn.close()
