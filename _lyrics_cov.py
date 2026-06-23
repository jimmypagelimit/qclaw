import sqlite3
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM tracks')
total = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM tracks WHERE (lyrics_text_path IS NOT NULL AND lyrics_text_path != '') OR (lyrics_lrc_path IS NOT NULL AND lyrics_lrc_path != '')")
has = c.fetchone()[0]
pct = round(has/total*100, 1)
print(f'Coverage: {has}/{total} = {pct}%')
print(f'Missing: {total - has}')
conn.close()
