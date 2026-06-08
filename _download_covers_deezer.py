import sqlite3, urllib.request, json, os, time, sys

sys.stdout = open(r'C:\Users\qujt\.qclaw\workspace\_cover_deezer_log.txt', 'w', encoding='utf-8')
sys.stderr = sys.stdout

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVER_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'

conn = sqlite3.connect(DB)
cur = conn.cursor()
# only the ones still missing
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE cover_image_url IS NULL OR cover_image_url = '' OR cover_image_url = '/covers/'")
rows = cur.fetchall()
conn.close()

print(f'Remaining: {len(rows)}')

def deezer_search(artist, album, retries=2):
    for attempt in range(retries):
        try:
            q = urllib.request.quote(f'{artist} {album}')
            url = f'https://api.deezer.com/search/album?q={q}&limit=5'
            resp = urllib.request.urlopen(url, timeout=10)
            data = json.loads(resp.read())
            for item in data.get('data', []):
                art = item.get('cover_medium', '') or item.get('cover', '')
                if art:
                    return art.replace('/250x250', '/500x500')
            return None
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
            else:
                return None

def download(url, path):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        with open(path, 'wb') as f:
            f.write(data)
        return len(data)
    except Exception as e:
        return 0

conn2 = sqlite3.connect(DB)
cur2 = conn2.cursor()

success = 0
fail = 0

for aid, name, artist in rows:
    safe_artist = ''.join(c for c in artist if c.isalnum() or c in ' -_').strip()[:20]
    safe_name = ''.join(c for c in name if c.isalnum() or c in ' -_').strip()[:30]
    fname = f'{aid}-{safe_artist}-{safe_name}.jpg'
    fpath = os.path.join(COVER_DIR, fname)

    artwork_url = deezer_search(artist, name)
    if artwork_url:
        sz = download(artwork_url, fpath)
        if sz > 5000:
            url_db = f'/covers/{fname}'
            cur2.execute("UPDATE albums SET cover_image_url = ? WHERE album_id = ?", (url_db, aid))
            conn2.commit()
            success += 1
            print(f'OK [{aid}] {name} ({artist}) - Deezer: {artwork_url}')
        else:
            fail += 1
            print(f'FAIL [{aid}] {name} ({artist}) - bad size {sz}')
    else:
        fail += 1
        print(f'FAIL [{aid}] {name} ({artist}) - no Deezer result')

conn2.close()
print(f'\nDone: {success} ok, {fail} failed')
sys.stdout.close()
