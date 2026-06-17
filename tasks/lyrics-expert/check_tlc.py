import sqlite3, urllib.request, json

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 1. 查 albums 表的 total_listen_count 字段
cur.execute("SELECT album_id, total_listen_count, album_name FROM albums WHERE album_id=555")
r = cur.fetchone()
print(f"albums表 total_listen_count 字段: {r[1]} (album_id={r[0]})")

# 2. 查 listen_history
cur.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=555")
cnt = cur.fetchone()[0]
print(f"listen_history 实际记录数: {cnt}")

# 3. 看看 server 用哪个字段
cur.execute("PRAGMA table_info(albums)")
cols = [c[1] for c in cur.fetchall()]
if 'total_listen_count' in cols:
    print("\n注意: total_listen_count 字段仍然存在于 albums 表中！")
    cur.execute("SELECT album_id, total_listen_count, album_name FROM albums WHERE album_id=555")
    r = cur.fetchone()
    print(f"  值 = {r[1]}")
else:
    print("\ntotal_listen_count 字段已被移除（新架构实时计算）")

conn.close()
