import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute('''
SELECT a.album_id, a.album_name, a.artist, a.country,
       COUNT(lh.id) as cnt
FROM albums a
JOIN listen_history lh ON lh.album_id = a.album_id
WHERE lh.listen_year = 2026
GROUP BY a.album_id
ORDER BY cnt DESC
LIMIT 30
''')

rows = c.fetchall()

with open(r'C:\Users\qujt\.qclaw\workspace\_2026_ranking.txt', 'w', encoding='utf-8') as f:
    total = sum(r['cnt'] for r in rows)
    f.write(f'2026听歌总数: {total} 次，共 {len(rows)} 张专辑\n\n')
    for i, row in enumerate(rows, 1):
        f.write(f'{i}. {row["artist"]} - {row["album_name"]} [{row["country"]}] x{row["cnt"]}\n')

conn.close()
print('Done - check _2026_ranking.txt')
