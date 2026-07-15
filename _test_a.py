import urllib.request, time
time.sleep(2)
try:
    r = urllib.request.urlopen('http://localhost:3456/api/stats', timeout=3)
    import json
    d = json.loads(r.read())
    print('OK - %s albums, %s listens' % (d.get('totalAlbums', '?'), d.get('totalListens', '?')))
except Exception as e:
    print('NOT READY: %s' % e)
