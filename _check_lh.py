import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()

# 检查 listen_history 中 album_id 与 albums 的对应关系
cur.execute("""
    SELECT lh.album_id, a.album_name, a.artist, COUNT(lh.id) as cnt
    FROM listen_history lh
    JOIN albums a ON lh.album_id = a.album_id
    WHERE lh.listen_year = 2026
    GROUP BY lh.album_id
    ORDER BY cnt DESC
    LIMIT 20
""")
for r in cur.fetchall():
    print(f"album_id={r[0]}, {r[1]} - {r[2]}, count={r[3]}")

# 也检查一下有没有孤立的 listen_history（album_id 不在 albums 表中）
cur.execute("""
    SELECT COUNT(*) FROM listen_history lh
    LEFT JOIN albums a ON lh.album_id = a.album_id
    WHERE a.album_id IS NULL AND lh.listen_year = 2026
""")
print(f"\n孤儿记录数: {cur.fetchone()[0]}")

conn.close()
