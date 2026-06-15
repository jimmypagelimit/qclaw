"""
MusicBrainz 数据补全脚本
- artists: country, formed_year
- albums: release_company (label), duration
"""
import sqlite3
import urllib.request
import json
import time
import random
import re

DB_PATH = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
BASE_URL = 'https://musicbrainz.org/ws/2'
UA = 'AlbumTracker/1.0 (jim@example.com)'

def mb_get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read())

def search_artist(name):
    """搜索艺人，返回 (country, formed_year)"""
    q = urllib.parse.quote(name)
    url = f'{BASE_URL}/artist/?query=artist:{q}&fmt=json&limit=5'
    try:
        data = mb_get(url)
        for a in data.get('artists', []):
            # 名称归一化比对
            if a.get('name', '').lower().replace(' ', '') == name.lower().replace(' ', ''):
                country = a.get('country', '')
                ls = a.get('life-span', {})
                begin = ls.get('begin', '')[:4] if ls.get('begin') else ''
                mbid = a.get('id', '')
                return country, begin, mbid
        # 没精确匹配，返回第一个
        if data.get('artists'):
            a = data['artists'][0]
            country = a.get('country', '')
            ls = a.get('life-span', {})
            begin = ls.get('begin', '')[:4] if ls.get('begin') else ''
            mbid = a.get('id', '')
            return country, begin, mbid
    except Exception as e:
        print(f'    搜索艺人失败: {e}')
    return None, None, None

def search_release(album_name, artist_name):
    """搜索专辑 release-group，返回 (label, duration_ms)"""
    q = urllib.parse.quote(f'{album_name} {artist_name}')
    url = f'{BASE_URL}/release-group/?query={q}&fmt=json&limit=5'
    try:
        data = mb_get(url)
        for rg in data.get('release-groups', []):
            # 名称归一化
            rg_name = rg.get('title', '').lower().replace(' ', '').replace("'", "")
            target = album_name.lower().replace(' ', '').replace("'", "")
            if rg_name == target or target in rg_name or rg_name in target:
                # 获取该 release-group 下的具体 release（用于拿 label 和 media duration）
                rg_id = rg.get('id', '')
                # 取第一个 primary release
                rel_url = f'{BASE_URL}/release-group/{rg_id}?fmt=json&inc=releases'
                rel_data = mb_get(rel_url)
                releases = rel_data.get('releases', [])
                if releases:
                    rel = releases[0]
                    label = ''
                    for lbl in rel.get('label-info', []):
                        label = lbl.get('name', '')
                        if label:
                            break
                    # duration
                    dur_ms = rg.get('media', [{}])[0].get('format')  # 这里只有格式，没时长
                    # 时长从 recording 获取
                    dur_ms = None
                    # 尝试从 tracklist 获取
                    tracklist_url = f'{BASE_URL}/release/{rel.get("id")}?fmt=json&inc=recordings'
                    try:
                        tl_data = mb_get(tracklist_url)
                        tracks = tl_data.get('media', [{}])[0].get('track-list', [])
                        dur_ms = sum(t.get('length', 0) or 0 for t in tracks)
                    except:
                        pass
                    return label, dur_ms
                break
    except Exception as e:
        print(f'    搜索专辑失败: {e}')
    return None, None

def main():
    import urllib.parse
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ========== 1. 补全 artists 表 ==========
    print('=== 补全 artists 表 ===')
    cur.execute("SELECT artist_id, name FROM artists WHERE country IS NULL OR country = ''")
    artists = cur.fetchall()
    print(f'共 {len(artists)} 个艺人需补 country/formed_year')

    updated = 0
    for i, (artist_id, name) in enumerate(artists):
        print(f'  [{i+1}/{len(artists)}] {name}')
        country, formed_year, mbid = search_artist(name)
        if country or formed_year:
            cur.execute(
                'UPDATE artists SET country = ?, formed_year = ? WHERE artist_id = ?',
                (country or None, int(formed_year) if formed_year and formed_year.isdigit() else None, artist_id)
            )
            updated += 1
            print(f'    -> country={country}, formed_year={formed_year}, mbid={mbid[:8] if mbid else "N/A"}...')
        time.sleep(1.1)  # 尊重 rate limit
        if (i+1) % 50 == 0:
            conn.commit()
            print(f'  已提交 {i+1} 条')

    conn.commit()
    print(f'artists 更新完成: {updated} 条')

    # ========== 2. 补全 albums 表 (release_company) ==========
    print()
    print('=== 补全 albums release_company ===')
    cur.execute("SELECT album_id, album_name, artist FROM albums WHERE (release_company IS NULL OR release_company = '') AND album_name != ''")
    albums = cur.fetchall()
    print(f'共 {len(albums)} 张专辑需补 release_company')

    updated = 0
    for i, (album_id, album_name, artist) in enumerate(albums):
        print(f'  [{i+1}/{len(albums)}] {artist} - {album_name}')
        label, dur = search_release(album_name, artist)
        if label:
            cur.execute(
                'UPDATE albums SET release_company = ? WHERE album_id = ?',
                (label, album_id)
            )
            updated += 1
            print(f'    -> label={label}, dur={dur}')
        time.sleep(1.1)
        if (i+1) % 50 == 0:
            conn.commit()
            print(f'  已提交 {i+1} 条')

    conn.commit()
    print(f'albums 更新完成: {updated} 条')

    # ========== 3. 补全 albums duration ==========
    print()
    print('=== 补全 albums duration ===')
    cur.execute("SELECT album_id, album_name, artist FROM albums WHERE (duration IS NULL OR duration = '') AND album_name != ''")
    albums_dur = cur.fetchall()
    print(f'共 {len(albums_dur)} 张专辑需补 duration')

    updated = 0
    for i, (album_id, album_name, artist) in enumerate(albums_dur):
        print(f'  [{i+1}/{len(albums_dur)}] {artist} - {album_name}')
        label, dur_ms = search_release(album_name, artist)
        if dur_ms:
            dur_sec = round(dur_ms / 1000)
            dur_str = f'{dur_sec//60}:{dur_sec%60:02d}'
            cur.execute(
                'UPDATE albums SET duration = ? WHERE album_id = ?',
                (dur_str, album_id)
            )
            updated += 1
            print(f'    -> duration={dur_str}')
        time.sleep(1.1)

    conn.commit()
    print(f'duration 更新完成: {updated} 条')

    conn.close()
    print()
    print('=== 全部完成 ===')

if __name__ == '__main__':
    import urllib.parse
    main()
