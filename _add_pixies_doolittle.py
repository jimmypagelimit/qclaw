import sqlite3, urllib.request, json, os

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
conn.text_factory = str
c = conn.cursor()

# Get next album_id
c.execute('SELECT MAX(album_id) FROM albums')
max_id = c.fetchone()[0] or 0
new_id = max_id + 1
print(f'New album_id: {new_id}')

today = '2026-06-21'
listen_year = 2026

# Insert album
c.execute('''
INSERT INTO albums (album_id, album_name, artist, country, release_year, genre, style, status)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (new_id, 'Doolittle', 'Pixies', 'US', 1989, 'Alternative Rock', 'Alternative Rock / Noise Pop / Post-Punk', 'active'))

# Insert 3 listen history records
for i in range(3):
    c.execute('''
    INSERT INTO listen_history (album_id, listen_date, listen_year, source)
    VALUES (?, ?, ?, ?)
    ''', (new_id, today, listen_year, 'personal'))

conn.commit()
print(f'Inserted Doolittle (ID={new_id}) with 3 listen records')

# Try to get cover art - iTunes first
cover_url = None
cover_path = None
filename = f'{new_id}-Pixies-Doolittle.jpg'

# iTunes Search API
itunes_url = 'https://itunes.apple.com/search?term=Pixies+Doolittle&entity=album&limit=1'
try:
    req = urllib.request.Request(itunes_url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=5)
    data = json.loads(resp.read())
    if data['resultCount'] > 0:
        cover_url = data['results'][0]['artworkUrl100'].replace('100x100', '600x600')
        print(f'iTunes cover: {cover_url}')
except Exception as e:
    print(f'iTunes failed: {e}')

# Download cover
if cover_url:
    try:
        req = urllib.request.Request(cover_url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        img_data = resp.read()
        
        covers_dir = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers'
        os.makedirs(covers_dir, exist_ok=True)
        cover_path = os.path.join(covers_dir, filename)
        with open(cover_path, 'wb') as f:
            f.write(img_data)
        print(f'Cover saved: {cover_path}')
        
        # Update database with cover path
        c.execute('UPDATE albums SET cover_image_url=? WHERE album_id=?', (f'/covers/{filename}', new_id))
        conn.commit()
        print('Cover URL updated in DB')
    except Exception as e:
        print(f'Download failed: {e}')
        cover_path = None

conn.close()
print('Done!')
