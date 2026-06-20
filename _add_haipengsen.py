import sqlite3
from datetime import date

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

album_id = 424
today = date.today().isoformat()

c.execute('INSERT INTO listen_history (album_id, listen_date) VALUES (?, ?)', (album_id, today))
c.execute('SELECT COUNT(*) FROM listen_history WHERE album_id=?', (album_id,))
new_count = c.fetchone()[0]

conn.commit()
conn.close()

print(f'OK - 海朋森《成长小说》(id=424) 听次数 +1，当前共 {new_count} 次 ({today})')
