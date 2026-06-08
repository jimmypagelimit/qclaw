import sqlite3, os

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
print('DB exists:', os.path.exists(db))
print('DB size:', os.path.getsize(db), 'bytes')
conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]
print('Tables:', tables)

print('\n=== artists columns ===')
cur.execute('PRAGMA table_info(artists)')
for r in cur.fetchall():
    print(r)

print('\n=== /api/artists query (current) ===')
# Simulate the current server.ts query
sql = """
SELECT a.artist_id, a.name, 
       COUNT(DISTINCT lh.listen_id) as listen_count,
       (SELECT al.cover_image_url FROM albums al 
        JOIN listen_history lh2 ON al.album_id = lh2.album_id 
        WHERE al.artist = a.name 
        ORDER BY al.total_listen_count DESC LIMIT 1) as top_cover
FROM artists a
JOIN albums al2 ON al2.artist = a.name
LEFT JOIN listen_history lh ON lh.album_id = al2.album_id
GROUP BY a.artist_id, a.name
ORDER BY listen_count DESC
LIMIT 10
"""
try:
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    print('Columns:', cols)
    for r in cur.fetchall():
        print(r)
except Exception as e:
    print(f'Error: {e}')

conn.close()
