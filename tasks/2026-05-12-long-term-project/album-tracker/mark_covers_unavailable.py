import sqlite3
import sys
import io

# Fix Windows encoding issue\sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Connect to database
conn = sqlite3.connect('_music_latest.db')
c = conn.cursor()

# Get albums without covers
c.execute('SELECT album_id, album_name, artist FROM albums WHERE cover_image_url IS NULL OR cover_image_url = "" ORDER BY total_listen_count DESC, rating DESC')
rows = c.fetchall()

print(f'Total albums without covers: {len(rows)}')
print('=' * 80)

# Update each album to mark as unavailable
for row in rows:
    album_id = row[0]
    album_name = row[1]
    artist = row[2]
    
    print(f'{album_id}: {artist} - {album_name}')
    
    # Mark as unavailable by setting a special marker
    c.execute('UPDATE albums SET cover_image_url = "UNAVAILABLE" WHERE album_id = ?', (album_id,))
    
    # Also update in yearly tables if they exist
    for table in ['albums_2024', 'albums_2025', 'albums_2026']:
        try:
            c.execute(f'UPDATE {table} SET cover_image_url = "UNAVAILABLE" WHERE album_id = ?', (album_id,))
        except:
            pass  # Table might not exist or album not in table

conn.commit()
print('=' * 80)
print(f'Marked {len(rows)} albums as UNAVAILABLE')

conn.close()
