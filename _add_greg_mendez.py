import sqlite3, json, urllib.request

DB = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db'
COVERS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 1. Check artist
cur.execute("SELECT artist_id, name FROM artists WHERE name = 'Greg Mendez'")
artist = cur.fetchone()
if artist:
    artist_id = artist[0]
    print(f"Artist exists: {artist_id} - {artist[1]}")
else:
    # Create new artist
    import hashlib
    artist_id = None
    cur.execute("SELECT MAX(artist_id) FROM artists")
    max_id = cur.fetchone()[0] or 0
    artist_id = max_id + 1
    cur.execute("INSERT INTO artists (artist_id, name) VALUES (?, ?)", (artist_id, 'Greg Mendez'))
    conn.commit()
    print(f"Created artist: {artist_id}")

# 2. Determine genre/style
# Apple Music says: Alternative
# Discogs says: Rock/Pop, Indie Rock/Indo-Pop
# Set style to 'Indie Rock'
style = 'Indie Rock'

# Find closest genre_id
# "Alternative Rock" genre_id = 5 
# "Alternative" (as genre name... doesn't exist neatly, use genre_id 5 as Alternative Rock)
genre = 'Alternative Rock'
cur.execute("SELECT genre_id FROM genres WHERE name = ?", ('Alternative Rock',))
genre_row = cur.fetchone()
if genre_row:
    genre_id = genre_row[0]
else:
    # Fallback
    cur.execute("SELECT genre_id FROM albums WHERE genre LIKE '%Altern%' LIMIT 1")
    genre_id = cur.fetchone()
    genre_id = genre_id[0] if genre_id else None
    genre = 'Alternative'

# Find style_id for Indie Rock
style_name = 'Indie Rock'
cur.execute("SELECT style_id FROM styles WHERE name = ?", (style_name,))
style_row = cur.fetchone()
style_id = style_row[0] if style_row else None

print(f"genre: {genre} (id={genre_id}), style: {style_name} (id={style_id})")

# 3. Insert album
album_id = 552
album_data = {
    'album_id': album_id,
    'album_name': 'Beauty Land',
    'artist': 'Greg Mendez',
    'genre': genre,
    'style': style_name,
    'release_year': '2026',
    'first_listen_date': '2026-06-11',
    'total_listen_count': 1,
    'country': 'US',
    'region': 'US',
    'duration': '25:06',
    'artist_id': artist_id,
    'genre_id': genre_id,
    'style_id': style_id,
    'release_company': '',
    'cover_image_url': '/covers/552-Greg Mendez-Beauty Land.jpg'
}

columns = ', '.join(album_data.keys())
placeholders = ', '.join(['?' for _ in album_data])
values = list(album_data.values())

sql = f"INSERT INTO albums ({columns}) VALUES ({placeholders})"
cur.execute(sql, values)
conn.commit()
print(f"Album inserted: {album_data['album_name']} (id={album_id})")

# 4. Insert listen_history
cur.execute("SELECT MAX(id) FROM listen_history")
lh_id = (cur.fetchone()[0] or 0) + 1

cur.execute(
    "INSERT INTO listen_history (id, album_id, listen_date, listen_year, notes, source) VALUES (?, ?, ?, ?, ?, ?)",
    (lh_id, album_id, '2026-06-11', 2026, '', '')
)
conn.commit()
print(f"Listen history added: id={lh_id}")

# 5. Download cover
cover_url = 'https://is1-ssl.mzstatic.com/image/thumb/Music221/v4/75/a3/41/75a341d8-5858-c0ea-3bd9-1a3f02bc202f/63326.jpg/3000x3000bb.jpg'

import os
cover_filename = f'552-Greg Mendez-Beauty Land.jpg'
cover_path = os.path.join(COVERS_DIR, cover_filename)

try:
    req = urllib.request.Request(cover_url, headers={'User-Agent': 'iTunes/12.0'})
    cover_data = urllib.request.urlopen(req, timeout=15).read()
    with open(cover_path, 'wb') as f:
        f.write(cover_data)
    print(f"Cover downloaded: {os.path.getsize(cover_path)} bytes")
except Exception as e:
    print(f"Cover download failed: {e}")

conn.close()
print("\nDone!")
