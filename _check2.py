import urllib.request, json

# Get listen history for both albums
r = urllib.request.urlopen('http://localhost:3456/api/albums/609', timeout=5)
album = json.loads(r.read())
print('BMTH:', album.get('album_name'), album.get('artist'))
print('  listen_count:', album.get('listen_count'))
print('  first_listen_date:', album.get('first_listen_date'))
print()

r2 = urllib.request.urlopen('http://localhost:3456/api/albums/610', timeout=5)
album2 = json.loads(r2.read())
print('acloudyskye:', album2.get('album_name'), album2.get('artist'))
print('  listen_count:', album2.get('listen_count'))
print('  first_listen_date:', album2.get('first_listen_date'))
