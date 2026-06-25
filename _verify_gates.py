import sqlite3, os, subprocess

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVERS = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'

# Verify database
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute('SELECT album_id, album_name, artist, release_year, release_mbid, cover_image_url FROM albums WHERE album_id = 597')
row = cur.fetchone()
print('=== Album 597 ===')
if row:
    for i, k in enumerate(['album_id', 'album_name', 'artist', 'release_year', 'release_mbid', 'cover_image_url']):
        print(f'  {k}: {row[i]}')

cur.execute('SELECT artist_id, name, country, region, album_count FROM artists WHERE artist_id = 326')
row = cur.fetchone()
print('=== Artist 326 ===')
if row:
    for i, k in enumerate(['artist_id', 'name', 'country', 'region', 'album_count']):
        print(f'  {k}: {row[i]}')

cur.execute('SELECT id, album_id, listen_date, listen_year, source FROM listen_history WHERE album_id = 597')
print('=== Listen history for album 597 ===')
for r in cur.fetchall():
    print('  ', r)
conn.close()

# Verify cover file
target = os.path.join(COVERS, '597-At The Gates-The Ghost of a Future Dead.jpg')
print('\n=== Cover file ===')
print('  Path:', target)
print('  Exists:', os.path.exists(target))
if os.path.exists(target):
    print('  Size:', os.path.getsize(target), 'bytes')
    from PIL import Image
    img = Image.open(target)
    print('  Dimensions:', img.size)
    print('  Mode:', img.mode)

# Check Web service
print('\n=== Web service ===')
out = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, shell=True)
for line in out.stdout.splitlines():
    if ':3456' in line:
        print(' ', line)
