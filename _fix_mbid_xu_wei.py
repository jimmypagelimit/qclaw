import sqlite3, urllib.request, json, time

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

albums = [
    (561, "19c7c9a2-0873-3f4e-8f8c-0239c12662a2"),  # 在别处
    (562, "80e1f4f0-3249-39fb-9879-6073a7f5d25b"),  # 那一年
    (563, "273c4ffd-6edc-3074-91fb-68552392ada6"),  # 在路上
    (564, "ecaa105e-ef11-48d8-b398-9788bf0dc026"),  # 无尽光芒
]

conn = sqlite3.connect(DB)
c = conn.cursor()
results = []

for album_id, rg_mbid in albums:
    try:
        time.sleep(1)  # rate limit
        url = f"https://musicbrainz.org/ws/2/release-group/{rg_mbid}?inc=releases&fmt=json"
        data = json.loads(urllib.request.urlopen(url, timeout=15).read())
        releases = data.get('releases', [])
        release_mbid = None
        for rel in releases:
            if rel.get('status') == 'Official':
                release_mbid = rel.get('id')
                break
        if not release_mbid and releases:
            release_mbid = releases[0].get('id')
        if release_mbid:
            c.execute("UPDATE albums SET release_mbid = ? WHERE album_id = ?", (release_mbid, album_id))
            results.append(f"id={album_id}: release_mbid={release_mbid}")
        else:
            results.append(f"id={album_id}: no release found")
    except Exception as e:
        results.append(f"id={album_id}: error={e}")

conn.commit()
conn.close()

with open(r'C:\Users\qujt\.qclaw\workspace\_mbid_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))
print("OK")
