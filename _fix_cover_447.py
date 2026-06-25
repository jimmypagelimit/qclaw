import urllib.request, ssl, json, urllib.parse

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

covers_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'

# Artist: 刺猬 [Hedgehog], Album: Honeyed and Killed
# NetEase search with UTF-8
queries = [
    '刺猬乐队 甜蜜与杀害',
    'Hedgehog 刺猬 Honeyed Killed',
]

for q in queries:
    kw_enc = urllib.parse.quote(q)
    url = 'https://music.163.com/api/search/get?s=' + kw_enc + '&type=10&limit=10'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com/'})
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        raw = resp.read()
        try:
            text = raw.decode('utf-8')
        except:
            text = raw.decode('gbk', errors='replace')
        data = json.loads(text)
        result = data.get('result', {})
        albums = result.get('albums', [])
        print('Query:', q, '->', len(albums), 'results')
        for a in albums[:5]:
            name = a.get('name', '')
            artist = a.get('artist', {})
            artist_name = artist.get('name', '') if isinstance(artist, dict) else str(artist)
            print('  ID:', a.get('id'), '| Name:', name, '| Artist:', artist_name)
            print('  Pic:', a.get('pic'))
        print()
    except Exception as e:
        print('Error:', e)

# Also try Apple Music
print('=== Apple Music ===')
url = 'https://itunes.apple.com/search?term=%E8%92%9C%E7%8C%AC+Honeyed+Killed&entity=album&limit=5'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    resp = urllib.request.urlopen(req, context=ctx, timeout=10)
    data = json.loads(resp.read())
    print('iTunes results:', data.get('resultCount'))
    for album in data.get('results', [])[:5]:
        print('  ID:', album.get('collectionId'), '| Name:', album.get('collectionName'), '| Art:', album.get('artworkUrl100'))
except Exception as e:
    print('iTunes error:', e)
