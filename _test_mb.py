import subprocess, json, urllib.parse, time

def curl_mb(url):
    try:
        r = subprocess.run(['curl.exe','-s','-L','-A','AlbumTracker/1.0','-m','15',url],
            capture_output=True, timeout=20)
        if r.returncode == 0 and r.stdout:
            return json.loads(r.stdout)
    except Exception as e:
        print(f'  error: {e}')
    return {}

# 测试1: Car Seat Headrest
name = 'Car Seat Headrest'
url = f'https://musicbrainz.org/ws/2/artist/?query=artist:{urllib.parse.quote(name)}&fmt=json&limit=3'
print(f'Testing: {name}')
data = curl_mb(url)
a = data.get('artists', [{}])[0]
print(f'  area: {a.get("area",{}).get("name")} / type: {a.get("area",{}).get("type")}')
print(f'  begin-area: {a.get("begin-area",{}).get("name")}')
print(f'  life-span.begin: {a.get("life-span",{}).get("begin")}')
print(f'  mbid: {a.get("id","")[:36]}')
time.sleep(1.5)

# 测试2: Twin Fantasy (album)
album = 'Twin Fantasy'
artist = 'Car Seat Headrest'
q = urllib.parse.quote(f'{album} {artist}')
url2 = f'https://musicbrainz.org/ws/2/release-group/?query={q}&fmt=json&limit=3'
print(f'\nTesting album: {album}')
data2 = curl_mb(url2)
rgs = data2.get('release-groups', [])
for rg in rgs[:2]:
    print(f'  RG: {rg.get("title")} | id: {rg.get("id","")[:20]}')
