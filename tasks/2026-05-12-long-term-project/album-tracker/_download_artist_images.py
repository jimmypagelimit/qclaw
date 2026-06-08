import sqlite3, json, urllib.request, ssl, os, time, sys

DB_PATH = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVERS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def req(url, timeout=8):
    try:
        return urllib.request.urlopen(url, timeout=timeout, context=ctx).read()
    except:
        return None

def add_column():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(artists)")
    cols = [r[1] for r in cur.fetchall()]
    if 'image_url' not in cols:
        cur.execute("ALTER TABLE artists ADD COLUMN image_url TEXT DEFAULT ''")
        conn.commit()
        print('Added image_url column', flush=True)
    conn.close()

def get_artists(limit=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    sql = "SELECT artist_id, name FROM artists ORDER BY total_listen_count DESC"
    if limit:
        sql += f" LIMIT {limit}"
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    return rows

def try_deezer(name):
    url = f"https://api.deezer.com/search/artist?q={urllib.request.quote(name)}&limit=1"
    data = req(url)
    if not data:
        return None
    j = json.loads(data)
    dl = j.get('data', [])
    if dl:
        pic = dl[0].get('picture_medium') or dl[0].get('picture')
        if pic:
            return pic.replace('/250x250-', '/200x200-')
    return None

def try_itunes(name):
    # iTunes artist search doesn't return images reliably
    # Try album search instead and take first result artwork
    url = f"https://itunes.apple.com/search?term={urllib.request.quote(name)}&entity=album&limit=1"
    data = req(url)
    if not data:
        return None
    j = json.loads(data)
    results = j.get('results', [])
    if results:
        art = results[0].get('artworkUrl100')
        if art:
            return art.replace('100x100bb', '200x200bb').replace('100x100', '200x200')
    return None

def download_image(url, save_path):
    data = req(url, timeout=12)
    if not data or len(data) < 800:
        return False
    with open(save_path, 'wb') as f:
        f.write(data)
    return True

def get_fallback_cover(artist_name, conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT cover_image_url FROM albums 
        WHERE artist = ? AND cover_image_url IS NOT NULL AND cover_image_url != ''
        ORDER BY total_listen_count DESC LIMIT 1
    """, (artist_name,))
    row = cur.fetchone()
    if row and row[0]:
        return row[0]
    return None

def main():
    add_column()
    os.makedirs(COVERS_DIR, exist_ok=True)
    
    artists = get_artists()  # all
    total = len(artists)
    print(f'Total artists: {total}', flush=True)
    
    conn = sqlite3.connect(DB_PATH)
    updated = 0
    downloaded = 0
    fallback_count = 0
    failed = 0
    
    for i, (aid, name) in enumerate(artists):
        filename = f"artist-{aid}.jpg"
        local_path = os.path.join(COVERS_DIR, filename)
        
        if os.path.exists(local_path) and os.path.getsize(local_path) > 800:
            img_url = f'/covers/{filename}'
        else:
            img_url = None
            
            # Strategy 1: Deezer (best for artist photos)
            durl = try_deezer(name)
            if durl and download_image(durl, local_path):
                img_url = f'/covers/{filename}'
                downloaded += 1
                print(f'[{i+1}/{total}] {name} -> deezer', flush=True)
            
            # Strategy 2: iTunes album artwork
            if not img_url:
                iurl = try_itunes(name)
                if iurl and download_image(iurl, local_path):
                    img_url = f'/covers/{filename}'
                    downloaded += 1
                    print(f'[{i+1}/{total}] {name} -> itunes', flush=True)
            
            # Strategy 3: fallback to best album cover
            if not img_url:
                fb = get_fallback_cover(name, conn)
                if fb:
                    if fb.startswith('/covers/'):
                        src = os.path.join(COVERS_DIR, os.path.basename(fb))
                        if os.path.exists(src):
                            import shutil
                            shutil.copy(src, local_path)
                            img_url = f'/covers/{filename}'
                    else:
                        if download_image(fb, local_path):
                            img_url = f'/covers/{filename}'
                    if img_url:
                        fallback_count += 1
                        print(f'[{i+1}/{total}] {name} -> fallback', flush=True)
            
            if not img_url:
                failed += 1
                print(f'[{i+1}/{total}] {name} -> FAIL', flush=True)
        
        # Update DB
        cur = conn.cursor()
        cur.execute("UPDATE artists SET image_url = ? WHERE artist_id = ?", (img_url or '', aid))
        conn.commit()
        updated += 1
        
        time.sleep(0.3)  # rate limit
    
    conn.close()
    
    print(f'\n=== DONE ===', flush=True)
    print(f'Downloaded: {downloaded}', flush=True)
    print(f'Fallback: {fallback_count}', flush=True)
    print(f'Failed: {failed}', flush=True)
    print(f'Total: {updated}/{total}', flush=True)

if __name__ == '__main__':
    main()
