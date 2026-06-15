import subprocess, json, urllib.parse, time, sys

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

def curl_mb(url):
    try:
        r = subprocess.run(
            ['curl.exe', '-s', '-L', '-A', 'AlbumTracker/1.0', '-m', '15', url],
            capture_output=True, timeout=20
        )
        if r.returncode == 0 and r.stdout:
            return json.loads(r.stdout)
    except Exception as e:
        sys.stderr.write(f'curl error: {e}\n')
    return {}

def name_match(a_name, target):
    return a_name.lower().replace(' ', '').replace("'", '').replace('-', '') == \
           target.lower().replace(' ', '').replace("'", '').replace('-', '')

def search_artist(name):
    encoded = urllib.parse.quote(name)
    url = f'https://musicbrainz.org/ws/2/artist/?query=artist:{encoded}&fmt=json&limit=5'
    data = curl_mb(url)
    if not data or 'artists' not in data:
        return None, None
    for a in data['artists']:
        if name_match(a.get('name', ''), name):
            break
    else:
        a = data['artists'][0]
    ls = a.get('life-span', {})
    begin = ls.get('begin', '')[:4] if ls.get('begin') else ''
    area = a.get('area', {})
    area_name = area.get('name', '')
    return begin, area_name

# 测试几个艺人
test_names = ['Car Seat Headrest', 'Pink Floyd', 'Sonic Youth', 'The Cure', 'Radiohead']
for n in test_names:
    fy, area = search_artist(n)
    print(f'{n}: formed_year={fy}, area={area}')
    time.sleep(1.2)
