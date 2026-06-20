import sqlite3, urllib.request, json, os, sys

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVERS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'

# 4 albums to add
albums = [
    {"name": "在别处", "artist": "许巍", "year": 1997, "mbid_rg": "19c7c9a2-0873-3f4e-8f8c-0239c12662a2", "country": "中国", "region": "大陆"},
    {"name": "那一年", "artist": "许巍", "year": 2000, "mbid_rg": "80e1f4f0-3249-39fb-9879-6073a7f5d25b", "country": "中国", "region": "大陆"},
    {"name": "在路上……", "artist": "许巍", "year": 2006, "mbid_rg": "273c4ffd-6edc-3074-91fb-68552392ada6", "country": "中国", "region": "大陆"},
    {"name": "无尽光芒", "artist": "许巍", "year": 2018, "mbid_rg": "ecaa105e-ef11-48d8-b398-9788bf0dc026", "country": "中国", "region": "大陆"},
]

conn = sqlite3.connect(DB)
c = conn.cursor()

# Get or create artist
c.execute("SELECT artist_id FROM artists WHERE name = '许巍'")
row = c.fetchone()
if row:
    artist_id = row[0]
else:
    c.execute("INSERT INTO artists (name, country, region) VALUES ('许巍', '中国', '大陆')")
    artist_id = c.lastrowid

results = []
for alb in albums:
    # Check duplicate
    c.execute("SELECT album_id FROM albums WHERE album_name = ? AND artist = ?", (alb['name'], alb['artist']))
    if c.fetchone():
        results.append(f"跳过(已存在): {alb['name']}")
        continue

    # Get release MBID from release-group
    release_mbid = None
    try:
        rg_url = f"https://musicbrainz.org/ws/2/release-group/{alb['mbid_rg']}?fmt=json"
        rg_data = json.loads(urllib.request.urlopen(rg_url, timeout=10).read())
        releases = rg_data.get('releases', [])
        # Pick first official release
        for rel in releases:
            if rel.get('status') == 'Official':
                release_mbid = rel.get('id')
                break
        if not release_mbid and releases:
            release_mbid = releases[0].get('id')
    except:
        pass

    # Get description from 网易云
    description = None
    try:
        search_url = f"https://music.163.com/api/search/get/web?s={urllib.request.quote(alb['artist'] + ' ' + alb['name'])}&type=10&limit=1"
        req = urllib.request.Request(search_url, headers={'Referer': 'https://music.163.com'})
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        items = data.get('result', {}).get('albums', [])
        if items:
            description = items[0].get('description', '') or None
    except:
        pass

    # Insert album
    c.execute("""INSERT INTO albums 
        (album_name, artist, country, region, release_year, release_mbid, artist_id, description, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'collection')""",
        (alb['name'], alb['artist'], alb['country'], alb['region'], alb['year'], release_mbid, artist_id, description))
    album_id = c.lastrowid
    results.append(f"入库: {alb['name']} (id={album_id}, mbid={release_mbid})")

conn.commit()

# Download covers
for alb in albums:
    c.execute("SELECT album_id FROM albums WHERE album_name = ? AND artist = ?", (alb['name'], alb['artist']))
    row = c.fetchone()
    if not row:
        continue
    album_id = row[0]
    
    # Check if cover exists
    cover_pattern = f"{album_id}-许巍-{alb['name']}"
    existing = [f for f in os.listdir(COVERS_DIR) if f.startswith(f"{album_id}-")] if os.path.exists(COVERS_DIR) else []
    if existing:
        results.append(f"封面已存在: {existing[0]}")
        continue

    # Try 网易云
    cover_url = None
    try:
        search_url = f"https://music.163.com/api/search/get/web?s={urllib.request.quote('许巍 ' + alb['name'])}&type=10&limit=1"
        req = urllib.request.Request(search_url, headers={'Referer': 'https://music.163.com'})
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        items = data.get('result', {}).get('albums', [])
        if items:
            pic = items[0].get('picUrl')
            if pic:
                cover_url = pic
    except:
        pass

    # Try iTunes fallback
    if not cover_url:
        try:
            itunes_url = f"https://itunes.apple.com/search?term={urllib.request.quote('许巍 ' + alb['name'])}&entity=album&limit=1"
            data = json.loads(urllib.request.urlopen(itunes_url, timeout=10).read())
            items = data.get('results', [])
            if items:
                art = items[0].get('artworkUrl100', '')
                cover_url = art.replace('100x100', '600x600') if art else None
        except:
            pass

    if cover_url:
        try:
            img_data = urllib.request.urlopen(cover_url, timeout=15).read()
            filename = f"{album_id}-许巍-{alb['name']}.jpg"
            filepath = os.path.join(COVERS_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(img_data)
            # Update DB
            c.execute("UPDATE albums SET cover_image_url = ? WHERE album_id = ?", (f'/covers/{filename}', album_id))
            results.append(f"封面下载: {filename} ({len(img_data)} bytes)")
        except Exception as e:
            results.append(f"封面下载失败: {e}")
    else:
        results.append(f"无封面源: {alb['name']}")

conn.commit()
conn.close()

with open(r'C:\Users\qujt\.qclaw\workspace\_xu_wei_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))
print("OK")
