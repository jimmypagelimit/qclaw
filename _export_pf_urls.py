import sqlite3, os

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
out = r'C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\data\review_urls.txt'

conn = sqlite3.connect(db)
c = conn.cursor()
c.execute('SELECT album_name, artist, review_url FROM albums WHERE review_url IS NOT NULL')
rows = c.fetchall()
conn.close()

os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(r[2] + '\n')

print(f'导出 {len(rows)} 条 review URL → {out}')
for r in rows:
    print(f'  {r[1]} - {r[0]}: {r[2][:70]}')
