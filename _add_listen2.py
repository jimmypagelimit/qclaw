import sqlite3, os, datetime

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Use known album_id=540 for Paul McCartney - The Boys of Dungeon Lane
album_id = 540
today = datetime.date.today().isoformat()

# Check current count
cur.execute('SELECT album_name, artist, total_listen_count FROM albums WHERE rowid = ?', (album_id,))
row = cur.fetchone()
print('Before:', row)

# Add listen_history record
cur.execute('INSERT INTO listen_history (album_id, listen_date, listen_year) VALUES (?, ?, ?)',
            (album_id, today, 2026))

# Update total count
cur.execute('UPDATE albums SET total_listen_count = total_listen_count + 1 WHERE rowid = ?', (album_id,))

# Get new count
cur.execute('SELECT total_listen_count FROM albums WHERE rowid = ?', (album_id,))
new_count = cur.fetchone()[0]

conn.commit()
conn.close()
print(f'Done! Added 1 listen. New total: {new_count}')
