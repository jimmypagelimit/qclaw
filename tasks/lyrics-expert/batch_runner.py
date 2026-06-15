#!/usr/bin/env python3
"""
L 项目 - 批量歌词获取
支持双源：英文 → LRCLIB | 中文 → 网易云
用法: python batch_runner.py --limit 10 --source wangyiyun|lrclib|both
"""
import json, sys, os, time, sqlite3, urllib.request, urllib.parse, random

# ========== 配置 ==========
DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
BASE_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert'
LYRICS_DIR = os.path.join(BASE_DIR, "lyrics")
TRACKLISTS_DIR = os.path.join(BASE_DIR, "tracklists")
LRCLIB_BASE = "https://lrclib.net/api"
UA = "AlbumTracker/1.0 (jim@example.com)"

os.makedirs(LYRICS_DIR, exist_ok=True)
os.makedirs(TRACKLISTS_DIR, exist_ok=True)

WY_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://music.163.com'
}

# ========== 工具函数 ==========
def is_chinese(text):
    chinese = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    return chinese > len(text) * 0.3

def safe_filename(s):
    return "".join(c for c in s if c not in r'\/:*?"<>|').strip()

# ========== 网易云 ==========
def wy_search(query):
    url = f'https://music.163.com/api/search/get?s={urllib.parse.quote(query)}&type=1&limit=3'
    try:
        req = urllib.request.Request(url, headers=WY_HEADERS)
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        songs = data.get('result', {}).get('songs', [])
        if songs:
            return songs[0]['id'], songs[0].get('name', '')
    except:
        pass
    return None, None

def wy_lyric(song_id):
    url = f'https://music.163.com/api/song/lyric?id={song_id}&lv=1&tv=1'
    try:
        req = urllib.request.Request(url, headers=WY_HEADERS)
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        lrc = data.get('lrc', {}).get('lyric', '')
        t_lrc = data.get('tlyric', {}).get('lyric', '')
        return lrc or '', t_lrc or ''
    except:
        return '', ''

# ========== LRCLIB ==========
def lrclib_search(artist, track):
    q = f'{artist} {track}'
    url = f'{LRCLIB_BASE}/search?q={urllib.parse.quote(q)}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        resp = urllib.request.urlopen(req, timeout=10)
        results = json.loads(resp.read())
        if results:
            return results[0].get('syncedLyrics', ''), results[0].get('plainLyrics', '')
    except:
        pass
    return '', ''

# ========== 网易云搜索曲目列表 ==========
def wy_get_tracklist(artist, album):
    """从网易云搜索获取专辑曲目列表"""
    # 优先用专辑名+艺人搜索
    results = []
    queries = [f'{artist} {album}', album, artist]
    
    for q in queries:
        url = f'https://music.163.com/api/search/get?s={urllib.parse.quote(q)}&type=1&limit=10'
        try:
            req = urllib.request.Request(url, headers=WY_HEADERS)
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read())
            songs = data.get('result', {}).get('songs', [])
            for s in songs:
                name = s.get('name', '')
                aid = s.get('album', {}).get('name', '') if isinstance(s.get('album'), dict) else ''
                if aid and (album.lower() in aid.lower() or album.lower() in name.lower()):
                    results.append({'song_id': s['id'], 'name': name, 'album': aid})
        except:
            pass
        time.sleep(0.5)
    
    # 去重，按专辑名匹配度排序
    seen = set()
    unique = []
    for r in results:
        if r['song_id'] not in seen:
            seen.add(r['song_id'])
            unique.append(r)
    return unique

# ========== 保存 ==========
def save_lyrics(artist, album, tracks_with_lyrics, source='lrclib'):
    """保存歌词文件"""
    base = os.path.join(LYRICS_DIR, safe_filename(artist), safe_filename(album))
    os.makedirs(base, exist_ok=True)
    saved = 0
    
    for item in tracks_with_lyrics:
        num = item.get('position', 0)
        title = item['title']
        fname = safe_filename(title)
        
        # LRC
        if item.get('lrc'):
            path = os.path.join(base, f'{num:02d}. {fname}.lrc')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(item['lrc'])
            saved += 1
        
        # 纯文本
        if item.get('plain'):
            path = os.path.join(base, f'{num:02d}. {fname}.txt')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(item['plain'])
        
        # 翻译（网易云）
        if item.get('trans_lrc'):
            path = os.path.join(base, f'{num:02d}. {fname}_zh.lrc')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(item['trans_lrc'])
    
    return saved

# ========== MB 曲目获取（简化版，不依赖 Playwright） ==========
def mb_get_tracklist_simple(artist, album):
    """用 HTTP 直接从 MB 搜索获取曲目（不用 Playwright）"""
    # 搜索 release-group
    q = urllib.parse.quote(f'{artist} {album}')
    url = f'https://musicbrainz.org/ws/2/release-group/?query={q}&type=album&method=indexed&fmt=json&limit=5'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        rgs = data.get('release-groups', [])
        if not rgs:
            return []
        
        # 选最佳匹配
        best_rg = None
        for rg in rgs:
            if album.lower() in rg.get('name', '').lower():
                best_rg = rg
                break
        if not best_rg:
            best_rg = rgs[0]
        
        rg_id = best_rg['id']
        
        # 获取 tracklist
        url2 = f'https://musicbrainz.org/ws/2/release/?query=rgid:{rg_id}&fmt=json&limit=5'
        req2 = urllib.request.Request(url2, headers={'User-Agent': UA})
        resp2 = urllib.request.urlopen(req2, timeout=15)
        data2 = json.loads(resp2.read())
        releases = data2.get('releases', [])
        if not releases:
            return []
        
        # 取第一个 release 的 id
        rel_id = releases[0]['id']
        
        # 获取曲目
        url3 = f'https://musicbrainz.org/ws/2/release/{rel_id}?fmt=json&inc=recordings'
        req3 = urllib.request.Request(url3, headers={'User-Agent': UA})
        resp3 = urllib.request.urlopen(req3, timeout=15)
        data3 = json.loads(resp3.read())
        
        tracks = []
        for med in data3.get('media', []):
            for t in med.get('tracks', []):
                tracks.append({
                    'position': t.get('position', 0),
                    'title': t.get('title', ''),
                    'duration_ms': t.get('length', 0)
                })
        return tracks
    except Exception as e:
        print(f'    MB HTTP fail: {e}')
        return []

# ========== 主处理 ==========
def process_album(artist, album, source='both'):
    """处理单张专辑"""
    album_dir = os.path.join(LYRICS_DIR, safe_filename(artist), safe_filename(album))
    
    # 检查是否已有歌词
    if os.path.exists(album_dir):
        existing = [f for f in os.listdir(album_dir) if f.endswith('.lrc')]
        if existing:
            return {'skipped': True, 'reason': 'already_exists', 'count': len(existing)}
    
    chinese = is_chinese(album) or is_chinese(artist)
    print(f'  -> {"中文" if chinese else "英文"}专辑')
    
    # 获取曲目
    tracks = []
    if chinese:
        tracks_data = wy_get_tracklist(artist, album)
        tracks = [{'position': i+1, 'title': t['name'], 'song_id': t['song_id']} for i, t in enumerate(tracks_data)]
    else:
        tracks = mb_get_tracklist_simple(artist, album)
    
    if not tracks:
        print(f'    [X] 无法获取曲目')
        return {'ok': 0, 'fail': 0, 'no_lyrics': 0}
    
    print(f'    曲目: {len(tracks)}首')
    
    ok = fail = 0
    results = []
    
    for t in tracks:
        title = t['title']
        num = t['position']
        song_id = t.get('song_id')
        lrc = plain = trans_lrc = ''
        
        if chinese and song_id:
            # 网易云
            lrc, trans_lrc = wy_lyric(song_id)
            plain = lrc
            if lrc:
                ok += 1
                print(f'      {num:2d}. {title[:40]} [WY OK]')
            else:
                fail += 1
                print(f'      {num:2d}. {title[:40]} [WY FAIL]')
        else:
            # LRCLIB
            lrc, plain = lrclib_search(artist, title)
            if lrc:
                ok += 1
                print(f'      {num:2d}. {title[:40]} [LRCLIB OK]')
            else:
                fail += 1
                print(f'      {num:2d}. {title[:40]} [LRCLIB FAIL]')
        
        results.append({
            'position': num, 'title': title,
            'lrc': lrc, 'plain': plain, 'trans_lrc': trans_lrc
        })
        time.sleep(0.8)
    
    # 保存
    saved = save_lyrics(artist, album, results)
    print(f'    保存: {saved}个LRC文件')
    return {'ok': ok, 'fail': fail, 'total': len(tracks), 'saved': saved}

# ========== 主入口 ==========
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=10)
    parser.add_argument('--source', default='both')  # wangyiyun|lrclib|both
    parser.add_argument('--album-id', type=int, default=None)
    args = parser.parse_args()
    
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    if args.album_id:
        cur.execute("SELECT album_id, artist, album_name FROM albums WHERE album_id = ?", (args.album_id,))
        rows = cur.fetchall()
    else:
        # 按播放次数排序，取未处理的
        cur.execute("""
            SELECT a.album_id, a.artist, a.album_name,
                   (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as pc
            FROM albums a
            WHERE a.album_name != ''
            ORDER BY pc DESC
            LIMIT ?
        """, (args.limit * 2,))
        rows = cur.fetchall()
    
    conn.close()
    
    print(f'待处理: {len(rows)}张专辑\n')
    
    total_ok = total_fail = 0
    for album_id, artist, album, *rest in rows:
        print(f'\n=== {artist} - {album} (id={album_id}) ===')
        result = process_album(artist, album, args.source)
        if result.get('skipped'):
            print(f'  跳过: {result["reason"]} ({result["count"]}个LRC)')
        else:
            total_ok += result.get('ok', 0)
            total_fail += result.get('fail', 0)
        time.sleep(1)
    
    print(f'\n总计: OK={total_ok} FAIL={total_fail}')

if __name__ == '__main__':
    main()