import sqlite3, json

db = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute('''
SELECT a.name, COUNT(al.album_id) as cnt
FROM artists a
LEFT JOIN albums al ON al.artist_id = a.artist_id
GROUP BY a.artist_id
ORDER BY cnt DESC
LIMIT 30
''')

rows = cur.fetchall()
artists = [{'name': r[0], 'count': r[1]} for r in rows]

with open(r'C:\Users\qujt\.qclaw\workspace\_top_artists.json', 'w', encoding='utf-8') as f:
    json.dump(artists, f, ensure_ascii=False, indent=2)

print('Saved to _top_artists.json')
for i, a in enumerate(artists[:15], 1):
    print(f"{i:2d}. {a['name']} ({a['count']}张)")

conn.close()
