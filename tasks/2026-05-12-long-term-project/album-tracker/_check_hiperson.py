import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# 搜海朋森
print('=== 海朋森专辑 ===')
cur.execute("SELECT album_id, album_name, artist, release_year, total_listen_count FROM albums WHERE artist LIKE '%Hiperson%' OR artist LIKE '%海朋森%'")
for r in cur.fetchall():
    print(r)

# 搜 listen_history
print('\n=== 海朋森 listen_history ===')
for row in cur.execute("SELECT lh.id, lh.album_id, lh.listen_year, lh.listen_date, a.album_name FROM listen_history lh JOIN albums a ON lh.album_id = a.album_id WHERE a.artist LIKE '%Hiperson%' OR a.artist LIKE '%海朋森%'"):
    print(row)

# 检查 release_year 类型
print('\n=== 2026 年全部（按 release_year） ===')
cur.execute("SELECT COUNT(*) FROM albums WHERE release_year = '2026'")
print(f"TEXT '2026': {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM albums WHERE release_year = 2026")
print(f"INT 2026: {cur.fetchone()[0]}")

conn.close()
