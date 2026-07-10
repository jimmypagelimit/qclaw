import sqlite3
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

c.execute("SELECT album_id, album_name, release_year, description, cover_image_url FROM albums WHERE artist = 'American Football' ORDER BY release_year")
rows = c.fetchall()
print(f'American Football albums: {len(rows)}')
for r in rows:
    c2 = conn.cursor()
    c2.execute("SELECT COUNT(*) FROM listen_history WHERE album_id = ?", (r[0],))
    listens = c2.fetchone()[0]
    print(f'  id={r[0]:>3} | {r[3] if r[3] else ""} | year={r[2]} | listens={listens} | cover={r[4]}')

# Also check artist
c.execute("SELECT artist_id, name FROM artists WHERE name LIKE '%American%Football%'")
print(f'Artist: {c.fetchall()}')

# Search for LP4
c.execute("SELECT album_id, album_name, release_year FROM albums WHERE album_name LIKE '%LP4%' OR album_name LIKE '%American Football%'")
for r in c.fetchall():
    print(f'  id={r[0]} | {r[1]} ({r[2]})')

conn.close()
