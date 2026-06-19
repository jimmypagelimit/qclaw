import urllib.request, json

for aid in [461, 336, 31]:
    r = json.loads(urllib.request.urlopen('http://localhost:3456/api/albums/' + str(aid), timeout=5).read())
    print('=== ' + r['artist'] + ' - ' + r['album_name'] + ' ' + str(len(r.get('tracks',[]))) + ' tracks ===')
    for t in r['tracks'][:3]:
        print('  #' + str(t['track_number']) + ' ' + repr(t['track_name'][:40]) + ' (' + str(t.get('duration','-')) + 's)')
    print()
