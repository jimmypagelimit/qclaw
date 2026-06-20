import urllib.request, json, sqlite3, sys

mbid = "__MBID__"
rg_url = f"https://musicbrainz.org/ws/2/release-group?artist={mbid}&fmt=json&limit=50"
resp = json.loads(urllib.request.urlopen(rg_url, timeout=15).read())
rgs = resp.get('release-groups', [])

albums = [rg for rg in rgs if rg.get('primary-type') == 'Album']
albums.sort(key=lambda x: x.get('first-release-date', ''))

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("SELECT album_name FROM albums WHERE artist LIKE '%__ARTIST__%'")
existing = set(r[0] for r in c.fetchall())
conn.close()

lines = ["=== __ARTIST__ MusicBrainz 专辑 (Album only) ==="]
for rg in albums:
    name = rg.get('title', '?')
    date = rg.get('first-release-date', '????')
    rg_id = rg.get('id', '?')
    flag = "[X]" if name in existing else "[ ]"
    lines.append(f"{flag} {date} | {repr(name)} | {rg_id}")

lines.append(f"\n已入库 {len(existing)} 张")
with open(r'C:\Users\qujt\.qclaw\workspace\_artist_albums.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("OK - wrote to _artist_albums.txt")
