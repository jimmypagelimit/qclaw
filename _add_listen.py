import sqlite3, os, datetime

db = r'\\10.0.2.4\qemu\原创计划\music\music'
if not os.path.exists(db):
    print('DB not reachable, using local copy...')
    db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

conn = sqlite3.connect(db)
cur = conn.cursor()

# Find the album - search by artist and partial name
cur.execute("SELECT id, album_name, artist, total_listen_count FROM albums WHERE artist LIKE '%McCartney%' AND album_name LIKE '%Dungeon%'")
row = cur.fetchone()
print('Found:', row)

if row:
    album_id = row[0]
    today = datetime.date.today().isoformat()
    
    # Add listen_history record
    cur.execute('INSERT INTO listen_history (album_id, listen_date, listen_year) VALUES (?, ?, ?)',
                (album_id, today, 2026))
    
    # Update total count
    cur.execute('UPDATE albums SET total_listen_count = total_listen_count + 1 WHERE id = ?', (album_id,))
    
    # Get new count
    cur.execute('SELECT total_listen_count FROM albums WHERE id = ?', (album_id,))
    new_count = cur.fetchone()[0]
    
    conn.commit()
    print(f'Added 1 listen. New total: {new_count}')
else:
    print('Album not found!')

conn.close()
print('Done.')
