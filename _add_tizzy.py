import sqlite3, urllib.request, os, shutil

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

# Check if Tizzy Bac artist exists
cur.execute("SELECT artist_id, name FROM artists WHERE name LIKE '%Tizzy Bac%'")
row = cur.fetchone()
if row:
    artist_id = row[0]
    print(f"Tizzy Bac artist_id={artist_id}")
else:
    cur.execute("""
        INSERT INTO artists (name, country, formed_year)
        VALUES (?, ?, ?)
    """, ('Tizzy Bac', 'TW', 1999))
    artist_id = cur.lastrowid
    print(f"Created Tizzy Bac artist_id={artist_id}")
    conn.commit()

# Check if album exists
cur.execute("SELECT album_id FROM albums WHERE album_name = '夏季热' AND artist_id = ?", (artist_id,))
row = cur.fetchone()
if row:
    print(f"Album already exists: id={row[0]}")
    album_id = row[0]
else:
    # Download cover from NetEase
    cover_url = 'http://p3.music.126.net/109951172445569812/37819.jpg'
    cover_dir = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers'
    cover_path = os.path.join(cover_dir, '558-Tizzy_Bac-夏季热.jpg')
    
    try:
        urllib.request.urlretrieve(cover_url, cover_path)
        size = os.path.getsize(cover_path)
        print(f"Cover downloaded: {size} bytes")
    except Exception as e:
        print(f"Cover download failed: {e}")
        cover_path = None
    
    cover_rel = '/covers/558-Tizzy_Bac-夏季热.jpg' if cover_path and os.path.exists(cover_path) else None
    
    # Insert album (using artist text field + artist_id)
    cur.execute("""
        INSERT INTO albums (album_name, artist, artist_id, release_year, genre, style, country, cover_image_url, release_company)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('夏季热', 'Tizzy Bac', artist_id, 2005, 'Indie Rock', 'Piano Rock', 'TW', cover_rel, '角头音乐'))
    album_id = cur.lastrowid
    print(f"Album inserted: id={album_id}")
    conn.commit()
    
    # Insert listen history
    cur.execute("""
        INSERT INTO listen_history (album_id, listen_year, listen_date)
        VALUES (?, ?, date('now'))
    """, (album_id, 2026))
    print(f"Listen history inserted")
    conn.commit()

conn.close()
print("Done")
