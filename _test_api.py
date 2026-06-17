import urllib.request, json

# 测试专辑 1
print("=== Album 1 ===")
try:
    resp = urllib.request.urlopen('http://localhost:3456/api/albums/1', timeout=5)
    data = json.loads(resp.read())
    print('album:', data.get('album_name'), '-', data.get('artist'))
    print('tracks:', len(data.get('tracks') or []), 'tracks')
    print('external_ratings:', len(data.get('external_ratings') or []), 'ratings')
    print('review_url:', data.get('review_url'))
    if data.get('tracks'):
        print('first track:', data['tracks'][0])
    if data.get('external_ratings'):
        print('first rating:', data['external_ratings'][0])
except Exception as e:
    print('ERROR:', e)

print()

# 测试专辑 20 (Car Seat Headrest - Twin Fantasy, 应该有 RYM 评分)
print("=== Album 20 (Twin Fantasy) ===")
try:
    resp = urllib.request.urlopen('http://localhost:3456/api/albums/20', timeout=5)
    data = json.loads(resp.read())
    print('album:', data.get('album_name'), '-', data.get('artist'))
    print('tracks:', len(data.get('tracks') or []), 'tracks')
    print('external_ratings:', len(data.get('external_ratings') or []), 'ratings')
    print('review_url:', data.get('review_url'))
    if data.get('external_ratings'):
        for r in data['external_ratings']:
            print('  rating:', r)
except Exception as e:
    print('ERROR:', e)
