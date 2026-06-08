import sqlite3, os

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
print('DB exists:', os.path.exists(db))
print('DB size:', os.path.getsize(db), 'bytes')
conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM artists WHERE image_url != '' AND image_url IS NOT NULL")
has = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM artists")
total = cur.fetchone()[0]
print(f'Artists with image: {has}/{total}')

cur.execute("SELECT name, image_url FROM artists WHERE image_url LIKE '/covers/artist-%' LIMIT 8")
for r in cur.fetchall():
    print(f'  {r[0]}: {r[1]}')

# Check covers dir
covers_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'
artist_files = [f for f in os.listdir(covers_dir) if f.startswith('artist-')]
print(f'\nArtist image files in covers/: {len(artist_files)}')
conn.close()
