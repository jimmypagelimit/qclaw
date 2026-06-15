"""
MusicBrainz 艺人信息补全（Playwright版）
- artists: country, formed_year
"""
import subprocess
import sys
import time
import re

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

def get_unfilled_artists():
    import sqlite3
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT artist_id, name FROM artists WHERE country IS NULL OR country = '' OR country = 'XW'")
    result = [(row[0], row[1]) for row in cur.fetchall()]
    conn.close()
    return result

def update_artist(artist_id, country, formed_year):
    import sqlite3
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        'UPDATE artists SET country = ?, formed_year = ? WHERE artist_id = ?',
        (country or None, int(formed_year) if formed_year and formed_year.isdigit() else None, artist_id)
    )
    conn.commit()
    conn.close()

def search_mb_artist(name):
    """用 subprocess + curl 尝试（SSL不稳定，加重试）"""
    import subprocess, json, time
    for attempt in range(3):
        try:
            url = f'https://musicbrainz.org/ws/2/artist/?query=artist:{subprocess.list2cmdline([name]).strip()}&fmt=json&limit=3'
            # 用 curl（系统curl，SSL实现不同）
            result = subprocess.run(
                ['curl', '-s', '-A', 'AlbumTracker/1.0', '-m', '10', url],
                capture_output=True, timeout=15
            )
            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)
                for a in data.get('artists', []):
                    if a.get('name', '').lower().replace(' ', '') == name.lower().replace(' ', ''):
                        country = a.get('country', '')
                        ls = a.get('life-span', {})
                        begin = ls.get('begin', '')[:4] if ls.get('begin') else ''
                        return country, begin
                # 无精确匹配，取第一个
                if data.get('artists'):
                    a = data['artists'][0]
                    return a.get('country', ''), (a.get('life-span', {}).get('begin', '') or '')[:4]
            time.sleep(2)
        except Exception as e:
            print(f'    重试 {attempt+1}: {e}')
            time.sleep(3)
    return None, None

def main():
    artists = get_unfilled_artists()
    print(f'需补全 {len(artists)} 个艺人')
    
    updated = 0
    for i, (artist_id, name) in enumerate(artists):
        print(f'[{i+1}/{len(artists)}] {name}', end='')
        country, formed_year = search_mb_artist(name)
        if country or formed_year:
            update_artist(artist_id, country, formed_year)
            updated += 1
            print(f' -> country={country}, formed_year={formed_year}')
        else:
            print(' -> 未找到')
        
        time.sleep(1.5)  # 避免请求过快
    
    print(f'完成，更新 {updated} 条')

if __name__ == '__main__':
    main()
