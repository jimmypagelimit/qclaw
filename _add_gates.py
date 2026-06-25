import sqlite3, os, urllib.request, ssl, subprocess
from datetime import datetime

# === Configuration ===
DB_PATH = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVERS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'
WORKSPACE = r'C:\Users\qujt\.qclaw\workspace'
ALBUM_TRACKER = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker'

# === Album data ===
ARTIST = 'At The Gates'
ALBUM = 'The Ghost of a Future Dead'
RELEASE_DATE = '2026-04-24'
RELEASE_YEAR = 2026
TRACK_COUNT = 12
GENRE = 'Melodic Death Metal'
STYLE = 'Death Metal'
COUNTRY = 'Sweden'
REGION = ''
APPLE_MUSIC_ID = 1873364809
MBID = '717ffd39-881e-41d8-a8cc-1aa6dfec62ed'
COVER_URL = 'https://is1-ssl.mzstatic.com/image/thumb/Music221/v4/0a/ae/80/0aae8004-6b6d-6075-6293-f3ae4fb017bc/196873096056.jpg/600x600bb.jpg'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# === Step 1: Stop Web Service ===
print('=== Step 1: Stop Web service ===')
os.chdir(ALBUM_TRACKER)
try:
    # Find and kill node process on port 3456
    out = subprocess.run(['cmd', '/c', 'netstat -ano | findstr :3456'], capture_output=True, text=True)
    for line in out.stdout.splitlines():
        if 'LISTENING' in line:
            parts = line.split()
            pid = parts[-1]
            print('Found PID:', pid)
            subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
            print('Killed PID:', pid)
except Exception as e:
    print('Web service stop error:', e)

# === Step 2: Download cover ===
print('\n=== Step 2: Download cover ===')
req = urllib.request.Request(COVER_URL, headers={'User-Agent': 'Mozilla/5.0'})
cover_data = urllib.request.urlopen(req, context=ctx, timeout=20).read()
print('Cover size:', len(cover_data), 'bytes')

# === Step 3: Insert into database ===
print('\n=== Step 3: Insert into database ===')
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Insert artist
cur.execute('''
    INSERT INTO artists (name, country, region, is_active, album_count, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
''', (ARTIST, COUNTRY, REGION, 1, 1, datetime.now().isoformat()))
new_artist_id = cur.lastrowid
print('New artist_id:', new_artist_id)

# Insert album
cover_path = f'/covers/{new_artist_id}-{ARTIST}-{ALBUM}.jpg'  # placeholder, will use album_id
cur.execute('''
    INSERT INTO albums (
        album_name, artist, country, region, genre, style,
        is_compilation, first_listen_date,
        cover_image_url, release_year, release_mbid, status, artist_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    ALBUM, ARTIST, COUNTRY, REGION, GENRE, STYLE,
    0, RELEASE_DATE,
    '', RELEASE_YEAR, MBID, 'active', new_artist_id
))
new_album_id = cur.lastrowid
print('New album_id:', new_album_id)

# Update cover path with actual album_id
cover_filename = f'{new_album_id}-{ARTIST}-{ALBUM}.jpg'
cover_rel_path = f'/covers/{cover_filename}'
cur.execute('UPDATE albums SET cover_image_url = ? WHERE album_id = ?', (cover_rel_path, new_album_id))
print('Updated cover_image_url:', cover_rel_path)

# Insert listen_history
today = datetime.now().strftime('%Y-%m-%d')
this_year = datetime.now().year
cur.execute('''
    INSERT INTO listen_history (album_id, listen_date, listen_year, source)
    VALUES (?, ?, ?, ?)
''', (new_album_id, today, this_year, 'manual'))
new_listen_id = cur.lastrowid
print('New listen_history id:', new_listen_id)

conn.commit()
conn.close()
print('Database committed.')

# === Step 4: Save cover to public/covers ===
print('\n=== Step 4: Save cover to public/covers ===')
cover_full_path = os.path.join(COVERS_DIR, cover_filename)
with open(cover_full_path, 'wb') as f:
    f.write(cover_data)
print('Saved cover:', cover_full_path, '(', os.path.getsize(cover_full_path), 'bytes )')

# === Step 5: Export SQL ===
print('\n=== Step 5: Export SQL ===')
sql_out = os.path.join(ALBUM_TRACKER, 'database.sql')
# Use the same export approach as album-tracker
try:
    out = subprocess.run(
        ['cmd', '/c', f'cd /d "{ALBUM_TRACKER}" && node dist/cli.js export-sql'],
        capture_output=True, text=True, timeout=30
    )
    print('Export stdout:', out.stdout)
    print('Export stderr:', out.stderr)
except Exception as e:
    print('SQL export error:', e)

# === Step 6: Restart Web service ===
print('\n=== Step 6: Restart Web service ===')
try:
    subprocess.Popen(
        ['cmd', '/c', f'cd /d "{ALBUM_TRACKER}" && start /B node dist/server.js'],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    print('Web service restarting...')
except Exception as e:
    print('Web service start error:', e)

# === Summary ===
print('\n=== SUMMARY ===')
print(f'Artist: {ARTIST} (ID={new_artist_id})')
print(f'Album: {ALBUM} (ID={new_album_id})')
print(f'Cover: {cover_filename}')
print(f'Listen: id={new_listen_id}, date={today}')
