import urllib.request, json

# Search MusicBrainz for the release
url = 'https://musicbrainz.org/ws/2/release-group?query=artist:%E6%96%BD%E9%91%AB%E6%96%87%E6%9C%88+release:%E5%B7%B4%E8%9C%80%E6%96%87%E8%89%BA%E5%A4%8D%E5%85%B4+%E7%AC%AC%E4%B8%80%E7%AB%A0&fmt=json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
for rg in resp.get('release-groups', []):
    print(f"ID: {rg.get('id')} | Title: {rg.get('title')} | Type: {rg.get('primary-type')}")
    # Get first release ID
    for rel in rg.get('releases', []):
        print(f"  ReleaseID: {rel.get('id')}")
        break
