import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# 专辑详情
print('=== 专辑详情 ===')
cur.execute("SELECT * FROM albums WHERE album_id = 540")
row = cur.fetchone()
if row:
    cols = [d[0] for d in cur.description]
    for c, v in zip(cols, row):
        print(f'  {c}: {v}')
else:
    print('  NOT FOUND')

# listen_history
print('\n=== 收听记录 ===')
cur.execute("SELECT COUNT(*) FROM listen_history WHERE album_id = 540")
print(f'  记录数: {cur.fetchone()[0]}')

# 2026年 listen_history 统计
print('\n=== 2026年收听统计 ===')
cur.execute("""
    SELECT a.album_name, a.artist, COUNT(lh.listen_id) as listens
    FROM albums a
    LEFT JOIN listen_history lh ON a.album_id = lh.album_id
    WHERE a.release_year = 2026
    GROUP BY a.album_id
    ORDER BY listens DESC
    LIMIT 10
""")
for r in cur.fetchall():
    print(f'  {r[0][:30]:30} | {r[1][:15]:15} | {r[2]}次')

conn.close()
