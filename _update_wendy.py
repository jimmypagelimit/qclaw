import sqlite3, urllib.request, json
from datetime import date

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
c = conn.cursor()

album_id = 543
today = str(date.today())
year = today[:4]

# 1. Add listen history
c.execute("INSERT INTO listen_history (album_id, listen_date, listen_year) VALUES (?, ?, ?)", (album_id, today, year))
print(f"Listen added: {today}")

# 2. Get current info
c.execute("SELECT release_mbid, description, cover_image_url, status FROM albums WHERE album_id = ?", (album_id,))
info = c.fetchone()
print(f"Current: mbid={bool(info[0])}, desc={bool(info[1])}, cover={bool(info[2])}, status={info[3]}")

# 3. MBID from MusicBrainz
if not info[0]:
    try:
        url = f"https://musicbrainz.org/ws/2/release-group/?query=artist:{urllib.request.quote('Wendy Eisenberg')}&fmt=json&limit=10"
        data = json.loads(urllib.request.urlopen(url, timeout=15).read())
        rgs = [rg for rg in data.get('release-groups', []) if rg.get('primary-type') == 'Album']
        if rgs:
            rg_mbid = rgs[0]['id']
            print(f"RG found: {rgs[0]['title']} ({rg_mbid})")
            # Get releases
            import time; time.sleep(1)
            rg_detail = json.loads(urllib.request.urlopen(f"https://musicbrainz.org/ws/2/release-group/{rg_mbid}?inc=releases&fmt=json", timeout=15).read())
            for rel in rg_detail.get('releases', []):
                if rel.get('status') == 'Official':
                    c.execute("UPDATE albums SET release_mbid = ? WHERE album_id = ?", (rel['id'], album_id))
                    print(f"MBID: {rel['id']}")
                    break
        else:
            print("No Album type RG found")
    except Exception as e:
        print(f"MB error: {e}")

# 4. Description from 网易云
if not info[1]:
    try:
        search_url = f"https://music.163.com/api/search/get/web?s={urllib.request.quote('Wendy Eisenberg')}&type=10&limit=1"
        req = urllib.request.Request(search_url, headers={'Referer': 'https://music.163.com'})
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        items = data.get('result', {}).get('albums', [])
        if items and items[0].get('description'):
            desc = items[0]['description']
            c.execute("UPDATE albums SET description = ? WHERE album_id = ?", (desc, album_id))
            print(f"Desc: got ({len(desc)} chars)")
        else:
            print("Desc: no result")
    except Exception as e:
        print(f"Desc error: {e}")

# 5. Cover
if not info[2]:
    try:
        search_url = f"https://music.163.com/api/search/get/web?s={urllib.request.quote('Wendy Eisenberg')}&type=10&limit=1"
        req = urllib.request.Request(search_url, headers={'Referer': 'https://music.163.com'})
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        items = data.get('result', {}).get('albums', [])
        pic_url = None
        if items and items[0].get('picUrl'):
            pic_url = items[0]['picUrl']
        
        if not pic_url:
            itunes_url = f"https://itunes.apple.com/search?term={urllib.request.quote('Wendy Eisenberg')}&entity=album&limit=1"
            itunes_data = json.loads(urllib.request.urlopen(itunes_url, timeout=10).read())
            results = itunes_data.get('results', [])
            if results:
                art = results[0].get('artworkUrl100', '')
                if art:
                    pic_url = art.replace('100x100', '600x600')
        
        if pic_url:
            import os
            img_data = urllib.request.urlopen(pic_url, timeout=15).read()
            filename = f"{album_id}-Wendy Eisenberg-Wendy Eisenberg.jpg"
            covers_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'
            filepath = os.path.join(covers_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(img_data)
            c.execute("UPDATE albums SET cover_image_url = ? WHERE album_id = ?", (f'/covers/{filename}', album_id))
            print(f"Cover: {filename} ({len(img_data)} bytes)")
        else:
            print("Cover: no source found")
    except Exception as e:
        print(f"Cover error: {e}")

# 6. Status -> active
c.execute("UPDATE albums SET status = 'active' WHERE album_id = ?", (album_id,))
print("Status: active")

conn.commit()
conn.close()
print("DONE")
