import sqlite3

conn = sqlite3.connect('_music_latest.db')
c = conn.cursor()
c.execute('SELECT album_id, album_name, artist FROM albums WHERE cover_image_url IS NULL OR cover_image_url = "" ORDER BY total_listen_count DESC, rating DESC')
rows = c.fetchall()
print(f'Total albums without covers: {len(rows)}')
for row in rows:
    print(row)
conn.close()
