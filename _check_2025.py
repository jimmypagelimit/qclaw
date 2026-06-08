import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()

# 对比 2025 年：albums_2025 的 album_id 和 albums 表是否对应
cur.execute("SELECT album_id, album_name, artist, total_listen_count FROM albums_2025 ORDER BY total_listen_count DESC LIMIT 20")
print("=== albums_2025 Top 20 ===")
for r in cur.fetchall():
    # 查 albums 表中同名的正确 id
    cur.execute("SELECT album_id FROM albums WHERE album_name=? AND artist=?", (r[1], r[2]))
    match = cur.fetchone()
    correct_id = match[0] if match else 'NOT FOUND'
    status = 'OK' if match and match[0] == r[0] else f'WRONG should be {correct_id}'
    print(f"  2025表id={r[0]}, {r[1]} - {r[2]}: {status}")

# 检查 listen_history 2025 的数据
print("\n=== listen_history 2025 Top 10 ===")
cur.execute("""
    SELECT a.album_name, a.artist, COUNT(lh.id) as cnt
    FROM listen_history lh JOIN albums a ON lh.album_id = a.album_id
    WHERE lh.listen_year = 2025
    GROUP BY lh.album_id ORDER BY cnt DESC LIMIT 10
""")
for r in cur.fetchall():
    print(f"  {r[0]} - {r[1]}: {r[2]}")

conn.close()
