import subprocess, json, urllib.parse

def curl_mb_raw(url):
    try:
        r = subprocess.run(['curl.exe','-s','-L','-A','AlbumTracker/1.0','-m','15',url],
            capture_output=True, timeout=20)
        if r.returncode == 0:
            return r.stdout
    except Exception as e:
        print(f'error: {e}')
    return ''

# Car Seat Headrest - 看完整返回
name = 'Car Seat Headrest'
url = f'https://musicbrainz.org/ws/2/artist/?query=artist:{urllib.parse.quote(name)}&fmt=json&limit=3'
raw = curl_mb_raw(url)
data = json.loads(raw)
for a in data.get('artists', []):
    print(f"name: {a.get('name')}, area: {a.get('area')}, ls: {a.get('life-span')}")
