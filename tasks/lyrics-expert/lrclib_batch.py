#!/usr/bin/env python3
"""
L 项目 - 英文歌词批量获取（LRCLIB 直接搜索）
不走 MusicBrainz，直接用 artist+track 搜索 LRCLIB
用法: python lrclib_batch.py --limit 20
"""
import json, os, sys, io, time, sqlite3, urllib.request, urllib.parse

# 修复 GBK 输出编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
BASE_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert'
LYRICS_DIR = os.path.join(BASE_DIR, "lyrics")
LRCLIB_BASE = "https://lrclib.net/api"
UA = "AlbumTracker/1.0 (jim@example.com)"

os.makedirs(LYRICS_DIR, exist_ok=True)

def safe_fn(s):
    s = s.replace('\x00', '').replace('\u0000', '').strip()
    return "".join(c for c in s if c not in r'\/:*?"<>|' and ord(c) > 31).strip()

def is_chinese(text):
    return sum(1 for c in text if '\u4e00' <= c <= '\u9fff') > len(text) * 0.3

def lrclib_search(artist, track):
    """搜索 LRCLIB，返回 (syncedLyrics, plainLyrics, albumName)"""
    q = f'{artist} {track}'
    url = f'{LRCLIB_BASE}/search?q={urllib.parse.quote(q)}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        resp = urllib.request.urlopen(req, timeout=10)
        results = json.loads(resp.read())
        if not results:
            return '', '', ''
        # 取第一个结果
        r = results[0]
        return r.get('syncedLyrics', ''), r.get('plainLyrics', ''), r.get('albumName', '')
    except Exception as e:
        return '', '', ''

def save_lyrics(artist, album, track_title, lrc_text, plain_text):
    base = os.path.join(LYRICS_DIR, safe_fn(artist), safe_fn(album))
    os.makedirs(base, exist_ok=True)
    fname = safe_fn(track_title)
    saved = []
    if lrc_text:
        p = os.path.join(base, f'{fname}.lrc')
        with open(p, 'w', encoding='utf-8') as f:
            f.write(lrc_text)
        saved.append(p)
    if plain_text:
        p = os.path.join(base, f'{fname}.txt')
        with open(p, 'w', encoding='utf-8') as f:
            f.write(plain_text)
        saved.append(p)
    return saved

def process_album(artist, album):
    """用 LRCLIB 逐首搜索歌词"""
    # 检查是否已有
    album_dir = os.path.join(LYRICS_DIR, safe_fn(artist), safe_fn(album))
    if os.path.exists(album_dir):
        existing = [f for f in os.listdir(album_dir) if f.endswith('.lrc')]
        if existing:
            return {'skipped': True, 'count': len(existing)}
    
    if is_chinese(album) or is_chinese(artist):
        print(f'  [SKIP] 中文专辑，跳过（走网易云）')
        return {'skipped': True, 'reason': 'chinese'}
    
    print(f'  处理中...')
    ok = fail = 0
    
    # LRCLIB 支持按专辑搜索，但用逐首搜索更精确
    # 先搜索专辑看有没有
    album_q = f'{artist} {album}'
    album_url = f'{LRCLIB_BASE}/search?q={urllib.parse.quote(album_q)}'
    album_results = []
    try:
        req = urllib.request.Request(album_url, headers={'User-Agent': UA})
        resp = urllib.request.urlopen(req, timeout=10)
        album_results = json.loads(resp.read())
    except:
        pass
    
    # 找专辑匹配的记录
    matched_results = []
    for r in album_results:
        if r.get('albumName', '').lower() == album.lower():
            matched_results.append(r)
    if not matched_results:
        # 放宽匹配：专辑名包含
        for r in album_results:
            if album.lower() in r.get('albumName', '').lower():
                matched_results.append(r)
    
    if matched_results:
        # 有专辑结果，提取所有曲目
        print(f'  找到专辑匹配: {len(matched_results)}条记录')
        saved_total = 0
        seen_tracks = set()
        for r in matched_results:
            track_title = r.get('trackName', '')
            if track_title in seen_tracks:
                continue
            seen_tracks.add(track_title)
            lrc = r.get('syncedLyrics', '')
            plain = r.get('plainLyrics', '')
            if lrc or plain:
                saved = save_lyrics(artist, album, track_title, lrc, plain)
                saved_total += len(saved)
                ok += 1
                print(f'    + {track_title}')
            else:
                fail += 1
        if saved_total > 0:
            print(f'  保存: {saved_total}个文件')
            return {'ok': ok, 'fail': fail, 'saved': saved_total}
    
    # 没有专辑结果，用专辑+艺人搜索尝试获取单一结果
    print(f'  专辑无结果，尝试单轨搜索...')
    # 用第一首热门歌曲来确认专辑
    ok_artist = artist
    ok_album = album
    
    # 直接保存当前专辑记录（即使没有曲目）
    # 尝试按 "artist - album" 精确搜索
    exact_q = f'{artist} {album}'
    exact_url = f'{LRCLIB_BASE}/search?q={urllib.parse.quote(exact_q)}'
    try:
        req = urllib.request.Request(exact_url, headers={'User-Agent': UA})
        resp = urllib.request.urlopen(req, timeout=10)
        exact_results = json.loads(resp.read())
        if exact_results:
            r = exact_results[0]
            lrc = r.get('syncedLyrics', '')
            plain = r.get('plainLyrics', '')
            if lrc:
                # 把这首歌保存为"代表曲目"
                track = r.get('trackName', album)
                save_lyrics(artist, album, track, lrc, plain)
                ok += 1
                print(f'  单曲命中: {track}')
    except:
        pass
    
    if ok == 0:
        print(f'  无结果')
        return {'ok': 0, 'fail': 0}
    
    return {'ok': ok, 'fail': fail, 'saved': ok}

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--album-id', type=int, default=None)
    args = parser.parse_args()
    
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    if args.album_id:
        cur.execute("SELECT album_id, artist, album_name FROM albums WHERE album_id = ?", (args.album_id,))
    else:
        cur.execute("""
            SELECT a.album_id, a.artist, a.album_name,
                   (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as pc
            FROM albums a
            WHERE a.album_name != ''
            ORDER BY pc DESC
            LIMIT ?
        """, (args.limit,))
    
    rows = cur.fetchall()
    conn.close()
    
    print(f'待处理: {len(rows)}张专辑\n')
    total_ok = total_fail = total_skip = 0
    
    for album_id, artist, album, *_ in rows:
        print(f'=== {artist} - {album} (id={album_id}) ===')
        result = process_album(artist, album)
        if result.get('skipped'):
            print(f'  跳过: {result.get("reason", "already_exists")}')
            total_skip += 1
        else:
            total_ok += result.get('ok', 0)
            total_fail += result.get('fail', 0)
        time.sleep(1)
    
    print(f'\n=== 总计: OK={total_ok} FAIL={total_fail} SKIP={total_skip} ===')

if __name__ == '__main__':
    main()