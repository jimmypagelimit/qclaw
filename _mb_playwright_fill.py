"""
MusicBrainz 数据补全 - Playwright版
策略：批量爬 MusicBrainz search 页面，正则提取 country + formed_year
"""
import subprocess
import sys
import time
import re
import sqlite3
import json

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
PY = r'C:\Python311\python.exe'
WORKDIR = r'C:\Users\qujt\.qclaw\workspace'

def get_unfilled_artists(limit=None):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT artist_id, name FROM artists 
        WHERE country IS NULL OR country = '' OR country = 'XW'
        OR formed_year IS NULL
    """)
    result = [(row[0], row[1]) for row in cur.fetchall()]
    conn.close()
    return result[:limit] if limit else result

def update_artist(artist_id, country, formed_year, mbid=None):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        'UPDATE artists SET country = ?, formed_year = ? WHERE artist_id = ?',
        (country or None, int(formed_year) if formed_year and formed_year.isdigit() else None, artist_id)
    )
    conn.commit()
    conn.close()

def get_playwright_page(url, wait=5):
    """用 opencli CDP 获取页面内容"""
    script = f'''
import subprocess, json

# 打开 URL
r = subprocess.run(
    ['opencli', 'browser', 'work', 'open', '{url}'],
    capture_output=True, text=True, timeout=30
)
print(r.stdout)
time.sleep({wait})

# 提取内容
r = subprocess.run(
    ['opencli', 'browser', 'work', 'extract'],
    capture_output=True, text=True, timeout=20
)
print(r.stdout[:3000])
'''
    result = subprocess.run([PY, '-c', script], capture_output=True, text=True, timeout=60)
    return result.stdout

def search_artist_mb(name):
    """通过 MusicBrainz HTML 搜索页面提取艺人信息"""
    import urllib.parse
    encoded = urllib.parse.quote(name)
    url = f'https://musicbrainz.org/search?query={encoded}&type=artist&limit=5&view=json'
    
    # 用 curl（Windows curl 用 Schannel，可能能通）
    import subprocess
    result = subprocess.run(
        ['curl.exe', '-s', '-L', '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
         '-m', '15', url],
        capture_output=True, timeout=20
    )
    content = result.stdout
    
    if not content:
        return None, None, None
    
    # 尝试 JSON 解析
    try:
        data = json.loads(content)
        results = data.get('results', [])
        for r in results:
            if r.get('name', '').lower().replace(' ','') == name.lower().replace(' ',''):
                # 找最小的 score
                best = r
                break
        else:
            best = results[0] if results else None
        if best:
            # JSON API 返回的是 search endpoint，不是标准 WS2
            return None, None, None
    except:
        pass
    
    # 正则从 HTML 提取
    # 找 artist 搜索结果中的信息
    patterns = [
        r'href="/artist/([a-f0-9-]+)"[^>]*>([^<]+)</a>.*?country.*?class="iso-3166-1">([A-Z]{{2}})',
        r'class="country"[^>]*>([^<]+)<',
    ]
    
    mbid_match = re.search(r'/artist/([a-f0-9]{36})', content)
    country_match = re.search(r'class="country"[^>]*>([^<]+)<', content)
    begin_match = re.search(r'life-span[^>]*>(\d{{4}})', content)
    
    mbid = mbid_match.group(1) if mbid_match else None
    country = country_match.group(1).strip() if country_match else None
    formed_year = begin_match.group(1) if begin_match else None
    
    return country, formed_year, mbid

def playwright_search(name):
    """用 Playwright/CDP 通过浏览器访问 MB 搜索页"""
    import urllib.parse
    encoded = urllib.parse.quote(name)
    # MusicBrainz HTML search
    url = f'https://musicbrainz.org/search?query={encoded}&type=artist&limit=5'
    
    # 用 opencli 打开页面
    try:
        r = subprocess.run(
            ['opencli', 'browser', 'work', 'open', url],
            capture_output=True, text=True, timeout=30
        )
        time.sleep(6)  # 等待页面加载
        
        # 提取内容
        r = subprocess.run(
            ['opencli', 'browser', 'work', 'extract'],
            capture_output=True, text=True, timeout=20
        )
        html = r.stdout
        
        # 解析 HTML
        mbid = None
        country = None
        formed = None
        
        # 找第一个艺人结果
        m = re.search(r'href="/artist/([a-f0-9]{36})"', html)
        if m:
            mbid = m.group(1)
        
        # country 和 life-span
        m = re.search(r'class="country"[^>]*>([^<]+)<', html)
        if m:
            country = m.group(1).strip()
        
        m = re.search(r'(?:begin|life-span)[^>]*>(\d{4})', html)
        if m:
            formed = m.group(1)
        
        return country, formed, mbid
    except Exception as e:
        print(f'Playwright error: {e}')
        return None, None, None

def main():
    artists = get_unfilled_artists()
    print(f'需补全 {len(artists)} 个艺人')
    print('策略: 先试 curl(快)，失败则用 Playwright')
    
    updated = 0
    failed = 0
    
    for i, (artist_id, name) in enumerate(artists):
        print(f'[{i+1}/{len(artists)}] {name}', end='', flush=True)
        
        # 尝试 curl（Python urllib 不通但 curl 可能通）
        country, formed_year, mbid = None, None, None
        
        import subprocess, urllib.parse, json
        encoded = urllib.parse.quote(name)
        url = f'https://musicbrainz.org/ws/2/artist/?query={encoded}&fmt=json&limit=3'
        
        try:
            result = subprocess.run(
                ['curl.exe', '-s', '-L', '-A', 'AlbumTracker/1.0', '-m', '12', url],
                capture_output=True, timeout=15
            )
            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)
                for a in data.get('artists', []):
                    aname = a.get('name', '').lower().replace(' ','')
                    if aname == name.lower().replace(' ',''):
                        country = a.get('country', '')
                        ls = a.get('life-span', {})
                        begin = ls.get('begin', '')[:4] if ls.get('begin') else ''
                        formed_year = begin
                        break
                else:
                    if data.get('artists'):
                        a = data['artists'][0]
                        country = a.get('country', '')
                        formed_year = (a.get('life-span', {}).get('begin', '') or '')[:4]
        except Exception as e:
            pass
        
        if not country and not formed_year:
            # fallback: Playwright
            country, formed_year, mbid = playwright_search(name)
        
        if country or formed_year:
            update_artist(artist_id, country, formed_year)
            updated += 1
            print(f' -> country={country}, formed_year={formed_year}')
        else:
            failed += 1
            print(' -> 未找到')
        
        time.sleep(1.2)
        
        if (i+1) % 20 == 0:
            print(f'  进度: {i+1}/{len(artists)}, 已更新 {updated}, 失败 {failed}')
    
    print(f'\\n完成: 更新 {updated} 条, 失败 {failed} 条')

if __name__ == '__main__':
    main()
