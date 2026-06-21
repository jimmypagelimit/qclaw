import sqlite3
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
conn.text_factory = str
c = conn.cursor()

# Search for pixies
c.execute("SELECT album_id, album_name, artist FROM albums WHERE LOWER(artist) LIKE '%pix%'")
rows = c.fetchall()
print('Pix results:', rows)

# Search for doolittle
c.execute("SELECT album_id, album_name, artist FROM albums WHERE LOWER(album_name) LIKE '%doolittle%'")
rows2 = c.fetchall()
print('Doolittle results:', rows2)

# Full text search
c.execute("SELECT album_id, album_name, artist FROM albums")
all_rows = c.fetchall()
for r in all_rows:
    name = (r[1] or '').lower()
    artist = (r[2] or '').lower()
    if 'pix' in name or 'pix' in artist or 'dool' in name or 'dool' in artist:
        print(repr(r[1]), repr(r[2]))

conn.close()
