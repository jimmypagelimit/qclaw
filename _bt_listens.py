import sqlite3

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

# Get listen counts for all Big Thief albums
cur.execute("""
SELECT a.album_id, a.album_name, a.release_year,
       COUNT(lh.id) as listen_count,
       GROUP_CONCAT(lh.listen_year) as years
FROM albums a
LEFT JOIN listen_history lh ON a.album_id = lh.album_id
WHERE a.artist_id = 21
GROUP BY a.album_id
ORDER BY a.release_year
""")

print("Big Thief 各专辑听歌次数：\n")
for r in cur.fetchall():
    album_id, name, year, count, years = r
    years_str = years if years else "无记录"
    print(f"  {name} ({year}) | 听了 {count} 次 | 年份：{years_str}")

# Also show total listens
cur.execute("""
SELECT SUM(cnt) FROM (
    SELECT COUNT(*) as cnt FROM listen_history lh
    JOIN albums a ON lh.album_id = a.album_id
    WHERE a.artist_id = 21
)
""")
total = cur.fetchone()[0]
print(f"\nBig Thief 合计：{total} 次")

conn.close()
