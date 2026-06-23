import sqlite3, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
db = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')

r = db.execute("SELECT album_id, album_name, artist FROM albums WHERE artist LIKE '%Sonic Youth%' AND album_name LIKE '%Sister%'").fetchone()
if r:
    aid, alb, art = r
    print('Found: [%s] %s - %s' % (aid, art, alb))
    today = datetime.date.today()
    db.execute("INSERT INTO listen_history (album_id, listen_date, listen_year) VALUES (?, ?, ?)", (aid, today, today.year))
    db.commit()
    cnt = db.execute('SELECT COUNT(*) FROM listen_history WHERE album_id=?', (aid,)).fetchone()[0]
    print('Listen count now: %s' % cnt)
else:
    print('Album not found')
db.close()
