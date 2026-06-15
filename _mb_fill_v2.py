"""
MusicBrainz 数据补全 - curl.exe版 (v2)
curl.exe: https://musicbrainz.org/ws/2/  (Python urllib SSL不通)
1. artists: formed_year (life-span.begin)
2. albums: release_company, duration (via release-group)
"""
import subprocess, sqlite3, json, urllib.parse, time, sys

# 修复 PowerShell GBK 编码问题
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

def curl_mb(url):
    """用 curl.exe 请求 MB API"""
    try:
        r = subprocess.run(
            ['curl.exe', '-s', '-L', '-A', 'AlbumTracker/1.0', '-m', '15', url],
            capture_output=True, timeout=20
        )
        if r.returncode == 0 and r.stdout:
            return json.loads(r.stdout)
    except Exception as e:
        sys.stderr.write(f'  curl error: {e}\n')
    return {}

def name_match(a_name, target):
    return a_name.lower().replace(' ', '').replace("'", '').replace('-', '') == \
           target.lower().replace(' ', '').replace("'", '').replace('-', '')

def get_best_artist(data, target_name):
    """从搜索结果中找最匹配的艺人"""
    if 'artists' not in data or not data['artists']:
        return None
    for a in data['artists']:
        if name_match(a.get('name', ''), target_name):
            return a
    return data['artists'][0]  # 无精确匹配，取第一个

def search_artist(name):
    """返回 (formed_year, artist_mbid)"""
    encoded = urllib.parse.quote(name)
    url = f'https://musicbrainz.org/ws/2/artist/?query=artist:{encoded}&fmt=json&limit=5'
    data = curl_mb(url)
    a = get_best_artist(data, name)
    if not a:
        return None, None
    ls = a.get('life-span', {})
    begin = ls.get('begin', '')[:4] if ls.get('begin') else ''
    return begin, a.get('id', '')

def get_area_country(area_id):
    """根据 area ID 获取 country name"""
    if not area_id:
        return None
    # 直接用 area ID 查，type=Country 的就是国家
    url = f'https://musicbrainz.org/ws/2/area/{area_id}?fmt=json&inc=area-rels'
    data = curl_mb(url)
    atype = data.get('type', '')
    if 'Country' in atype:
        return data.get('name', '')
    # 向上找 parent
    for rel in data.get('area-rels', []):
        if rel.get('type') == 'part of':
            parent = rel.get('area', {})
            if 'Country' in parent.get('type', ''):
                return parent.get('name', '')
    return None

def search_release(album_name, artist_name):
    """返回 (release_company, duration_str)"""
    q = urllib.parse.quote(f'{album_name} {artist_name}')
    url = f'https://musicbrainz.org/ws/2/release-group/?query={q}&fmt=json&limit=5'
    data = curl_mb(url)
    if 'release-groups' not in data or not data['release-groups']:
        return None, None
    
    best_rg = None
    for rg in data['release-groups']:
        rg_name = rg.get('title', '').lower().replace(' ', '').replace("'", '')
        target = album_name.lower().replace(' ', '').replace("'", '')
        if rg_name == target or target in rg_name or rg_name in target:
            best_rg = rg
            break
    if not best_rg:
        best_rg = data['release-groups'][0]
    
    label_name = None
    total_dur_ms = 0
    
    # 获取该 release-group 下的第一个 release（拿 label）
    rg_id = best_rg.get('id', '')
    if rg_id:
        rg_url = f'https://musicbrainz.org/ws/2/release-group/{rg_id}?fmt=json&inc=releases'
        rg_data = curl_mb(rg_url)
        releases = rg_data.get('releases', [])
        if releases:
            rel = releases[0]
            for lbl in rel.get('label-info', []):
                ln = lbl.get('name', '')
                if ln:
                    label_name = ln
                    break
            # 获取 recordings 时长
            rel_id = rel.get('id', '')
            if rel_id:
                tl_url = f'https://musicbrainz.org/ws/2/release/{rel_id}?fmt=json&inc=recordings'
                tl_data = curl_mb(tl_url)
                for medium in tl_data.get('media', []):
                    for track in medium.get('track-list', []):
                        dur = track.get('length')
                        if dur:
                            total_dur_ms += dur
    
    dur_str = None
    if total_dur_ms > 0:
        total_sec = round(total_dur_ms / 1000)
        dur_str = f'{total_sec // 60}:{total_sec % 60:02d}'
    
    return label_name, dur_str

def update_artist(conn, artist_id, formed_year):
    cur = conn.cursor()
    cur.execute(
        'UPDATE artists SET formed_year = ? WHERE artist_id = ?',
        (int(formed_year) if formed_year and formed_year.isdigit() else None, artist_id)
    )

def update_album(conn, album_id, field, value):
    cur = conn.cursor()
    cur.execute(f'UPDATE albums SET {field} = ? WHERE album_id = ?', (value, album_id))

def main():
    conn = sqlite3.connect(DB)
    
    # ======= 1. artists: formed_year =======
    print('=== 补全 artists.formed_year ===')
    cur = conn.cursor()
    cur.execute("SELECT artist_id, name FROM artists WHERE (formed_year IS NULL OR formed_year = 0) AND name != ''")
    artists = cur.fetchall()
    print(f'共 {len(artists)} 个艺人')
    
    updated = 0
    for i, (artist_id, name) in enumerate(artists):
        sys.stdout.write(f'[{i+1}/{len(artists)}] {name}')
        sys.stdout.flush()
        formed_year, mbid = search_artist(name)
        if formed_year:
            update_artist(conn, artist_id, formed_year)
            updated += 1
            sys.stdout.write(f' -> formed={formed_year}')
        else:
            sys.stdout.write(' -> 无')
        sys.stdout.write('\n')
        sys.stdout.flush()
        time.sleep(1.1)
        if (i+1) % 50 == 0:
            conn.commit()
            print(f'  已提交 {i+1} 条')
    
    conn.commit()
    print(f'artists 完成: {updated} 条')
    
    # ======= 2. albums: release_company =======
    print()
    print('=== 补全 albums.release_company ===')
    cur = conn.cursor()
    cur.execute("SELECT album_id, album_name, artist FROM albums WHERE (release_company IS NULL OR release_company = '') AND album_name != ''")
    albums = cur.fetchall()
    print(f'共 {len(albums)} 张专辑')
    
    updated = 0
    for i, (album_id, album_name, artist) in enumerate(albums):
        sys.stdout.write(f'[{i+1}/{len(albums)}] {artist} - {album_name}')
        sys.stdout.flush()
        label, dur = search_release(album_name, artist)
        if label:
            update_album(conn, album_id, 'release_company', label)
            updated += 1
            sys.stdout.write(f' -> label={label}')
            if dur:
                update_album(conn, album_id, 'duration', dur)
                sys.stdout.write(f', dur={dur}')
        else:
            sys.stdout.write(' -> 无')
        sys.stdout.write('\n')
        sys.stdout.flush()
        time.sleep(1.1)
        if (i+1) % 50 == 0:
            conn.commit()
            print(f'  已提交 {i+1} 条')
    
    conn.commit()
    print(f'release_company 完成: {updated} 条')
    
    # ======= 3. albums: duration =======
    print()
    print('=== 补全 albums.duration ===')
    cur = conn.cursor()
    cur.execute("SELECT album_id, album_name, artist FROM albums WHERE (duration IS NULL OR duration = '') AND album_name != ''")
    dur_albums = cur.fetchall()
    print(f'共 {len(dur_albums)} 张专辑')
    
    updated = 0
    for i, (album_id, album_name, artist) in enumerate(dur_albs := dur_albums):
        sys.stdout.write(f'[{i+1}/{len(dur_albs)}] {artist} - {album_name}')
        sys.stdout.flush()
        label, dur = search_release(album_name, artist)
        if dur:
            update_album(conn, album_id, 'duration', dur)
            updated += 1
            sys.stdout.write(f' -> dur={dur}')
        else:
            sys.stdout.write(' -> 无')
        sys.stdout.write('\n')
        sys.stdout.flush()
        time.sleep(1.1)
    
    conn.commit()
    conn.close()
    print(f'duration 完成: {updated} 条')
    print()
    print('=== 全部完成 ===')

if __name__ == '__main__':
    main()
