import sqlite3, datetime, subprocess

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

# Kill web service
r = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
for line in r.stdout.splitlines():
    if ':3456' in line and 'LISTENING' in line:
        pid = line.split()[-1]
        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)

conn = sqlite3.connect(db)
cur = conn.cursor()

# Insert album
cur.execute("""
    INSERT INTO albums (album_name, artist, artist_id, release_year, genre, style, duration)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", ('\u8352\u829c\u4e4b\u5883', '\u9648\u695a\u751f', 296, 2025, 'Indie Folk', 'Indie Folk', 32))
conn.commit()

cur.execute("SELECT album_id FROM albums WHERE album_name = ?", ('\u8352\u829c\u4e4b\u5883',))
album_id = cur.fetchone()[0]
print(f'Album ID: {album_id}')

# Add style links (Indie Folk=54, Folk=3)
cur.execute("INSERT INTO album_styles (album_id, style_id, style_order) VALUES (?, 54, 1)", (album_id,))
cur.execute("INSERT INTO album_styles (album_id, style_id, style_order) VALUES (?, 3, 2)", (album_id,))

# Add genre links
cur.execute("SELECT genre_id, name FROM genres WHERE name LIKE '%olk%'")
for g in cur.fetchall():
    print(f'Genre: {g}')
cur.execute("INSERT INTO album_genres (album_id, genre_id, genre_order) VALUES (?, 54, 1)", (album_id,))

# Add listen_history
today = datetime.date.today().strftime('%Y-%m-%d')
cur.execute("INSERT INTO listen_history (album_id, listen_year, listen_date) VALUES (?, 2025, ?)", (album_id, today))
conn.commit()

cur.execute("SELECT COUNT(*) FROM albums")
print(f'Total albums: {cur.fetchone()[0]}')

conn.close()

# Restart web service
import os
os.chdir(r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker')
subprocess.Popen(['node', 'dist/server.js'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print('Done')
