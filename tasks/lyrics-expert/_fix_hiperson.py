import sqlite3, sys, urllib.request, json, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# 1) 清空错误 MBID 和 tracks
cur.execute("UPDATE albums SET release_mbid = NULL WHERE album_id = 424")
cur.execute("DELETE FROM tracks WHERE album_id = 424")
conn.commit()
print('已清空 ID 424 的 MBID 和 tracks')

# 2) 搜索 MusicBrainz release-group
def mb_search(query, limit=10):
    url = f'https://musicbrainz.org/ws/2/release-group?query={urllib.parse.quote(query)}&fmt=json&limit={limit}'
    req = urllib.request.Request(url, headers={'User-Agent': 'AlbumTracker/1.0', 'Accept': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=15).read())

# 搜索海朋森成长小说
result = mb_search('artist:海朋森 AND releasegroup:成长小说')
print(f'\n搜索 "artist:海朋森 AND releasegroup:成长小说"')
if 'release-groups' in result:
    for rg in result['release-groups']:
        print(f'  RG: {rg.get("title","?")} ({rg.get("id","?")}) type={rg.get("primary-type","?")} artist={rg.get("artist-credit",[{}])[0].get("name","?")}')

if not result.get('release-groups'):
    # try simpler query
    result = mb_search('海朋森 成长小说')
    print(f'\n搜索 "海朋森 成长小说"')
    if 'release-groups' in result:
        for rg in result['release-groups'][:5]:
            artists = ','.join(ac.get('name','?') for ac in rg.get('artist-credit',[]))
            print(f'  RG: {rg.get("title","?")} ({rg.get("id","?")}) type={rg.get("primary-type","?")} artist={artists}')

conn.close()
