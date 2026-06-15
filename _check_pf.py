import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

c.execute('SELECT COUNT(*) FROM albums WHERE pitchfork_score IS NOT NULL')
has_pf = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM albums')
total = c.fetchone()[0]
print(f'Pitchfork评分覆盖: {has_pf}/{total} ({has_pf*100//total}%)')

c.execute('SELECT album_name, artist, pitchfork_score, review_url FROM albums WHERE pitchfork_score IS NOT NULL')
for r in c.fetchall():
    url = (r[3][:60] + '...') if r[3] and len(r[3]) > 60 else (r[3] or 'no url')
    print(f'  {r[1]} - {r[0]}: {r[2]} | {url}')

conn.close()
