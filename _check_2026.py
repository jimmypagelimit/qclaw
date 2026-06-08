import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()

# 检查 listen_history 中 2026 年的数据
cur.execute("""
    SELECT lh.album_id, a.album_name, a.artist, COUNT(lh.id) as listen_count, a.total_listen_count
    FROM listen_history lh
    JOIN albums a ON lh.album_id = a.album_id
    WHERE lh.listen_year = 2026
    GROUP BY lh.album_id
    ORDER BY listen_count DESC
    LIMIT 15
""")
print("=== 2026年 listen_history ===")
for r in cur.fetchall():
    print(f"album_id={r[0]}, name={r[1]}, artist={r[2]}, year_count={r[3]}, total={r[4]}")

# 检查 albums_2026 的数据对比
cur.execute("SELECT album_id, album_name, artist, total_listen_count FROM albums_2026 ORDER BY total_listen_count DESC LIMIT 15")
print("\n=== albums_2026 原表 ===")
for r in cur.fetchall():
    print(f"album_id={r[0]}, name={r[1]}, artist={r[2]}, count={r[3]}")

conn.close()
