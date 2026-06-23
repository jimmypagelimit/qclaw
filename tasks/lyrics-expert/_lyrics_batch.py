#!/usr/bin/env python3
"""
L 项目 v3 - 歌词批量获取（基于 DB tracks 表）
流程：tracks表 → LRCLIB（英文）/ 网易云（中文）→ 本地保存

用法：
  python _lyrics_batch.py --limit 20         # 处理前20张（最多收听）
  python _lyrics_batch.py --album-id 29      # 处理指定专辑
  python _lyrics_batch.py --english-only      # 只处理英文
  python _lyrics_batch.py --chinese-only      # 只处理中文
"""
import json, os, sys, time, sqlite3, urllib.request, urllib.parse, re

# 编码修复
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
BASE_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert'
LYRICS_DIR = os.path.join(BASE_DIR, "lyrics")
LRCLIB_BASE = "https://lrclib.net/api"
WY_API = "https://music.163.com/api"
UA = "AlbumTracker/1.0 (jim@163.com)"
os.makedirs(LYRICS_DIR, exist_ok=True)

def safe_fn(s):
    return "".join(c for c in s if c not in r'\/:*?"<>|').strip()[:120]

def is_chinese(text):
    if not text: return False
    cn = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    return cn > len(text.strip()) * 0.2

def has_lyrics_dir(artist, album):
    d = os.path.join(LYRICS_DIR, safe_fn(artist), safe_fn(album))
    if os.path.exists(d):
        lrcs = [f for f in os.listdir(d) if f.endswith('.lrc')]
        return len(lrcs) > 0
    return False

def save_lyrics(artist, album, track_title, lrc_text, plain_text, suffix=''):
    """suffix: '' for original, '_zh' for Chinese translation"""
    base = os.path.join(LYRICS_DIR, safe_fn(artist), safe_fn(album))
    os.makedirs(base, exist_ok=True)
    fname = safe_fn(track_title)[:80]
    saved = []
    if lrc_text:
        p = os.path.join(base, f'{fname}{suffix}.lrc')
        with open(p, 'w', encoding='utf-8') as f:
            f.write(lrc_text)
        saved.append(p)
    if plain_text:
        p = os.path.join(base, f'{fname}{suffix}.txt')
        with open(p, 'w', encoding='utf-8') as f:
            f.write(plain_text)
        saved.append(p)
    return saved

# ===== LRCLIB (英文) =====
def lrclib_get(artist, track):
    """LRCLIB 搜索单曲歌词"""
    q = f'{artist} {track}'
    url = f'{LRCLIB_BASE}/search?q={urllib.parse.quote(q)}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        resp = urllib.request.urlopen(req, timeout=10)
        results = json.loads(resp.read())
        if not results:
            return None
        r = results[0]
        return {
            'synced': r.get('syncedLyrics', ''),
            'plain': r.get('plainLyrics', ''),
            'album': r.get('albumName', ''),
            'track': r.get('trackName', '')
        }
    except:
        return None

def process_english_album(artist, album, tracks):
    """LRCLIB 逐首获取英文歌词"""
    results = {'ok': 0, 'fail': 0, 'files': 0, 'skipped': 0}
    for tn, tname in tracks:
        data = lrclib_get(artist, tname)
        if data and (data['synced'] or data['plain']):
            saved = save_lyrics(artist, album, tname, data['synced'], data['plain'])
            results['ok'] += 1
            results['files'] += len(saved)
        else:
            results['fail'] += 1
        time.sleep(0.3)
    return results

# ===== 网易云（中文） =====
def netease_search(track, artist):
    """网易云搜索单曲"""
    url = f'{WY_API}/search/get?s={urllib.parse.quote(f"{track} {artist}")}&type=1&limit=5'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://music.163.com'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        songs = data.get('result', {}).get('songs', [])
        if not songs:
            return None
        s = songs[0]
        return {'id': s['id'], 'name': s['name'], 'artist': s['artists'][0]['name'] if s.get('artists') else ''}
    except:
        return None

def netease_lyrics(song_id):
    """获取网易云歌词（含翻译）"""
    url = f'{WY_API}/song/lyric?id={song_id}&lv=1&tv=1'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://music.163.com'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        lrc = (data.get('lrc') or {}).get('lyric', '')
        tlrc = (data.get('tlyric') or {}).get('lyric', '')
        return lrc, tlrc
    except:
        return '', ''

def process_chinese_album(artist, album, tracks):
    """网易云逐首获取中文歌词（含翻译）"""
    results = {'ok': 0, 'fail': 0, 'files': 0, 'skipped': 0}
    for tn, tname in tracks:
        info = netease_search(tname, artist)
        if info:
            lrc, tlrc = netease_lyrics(info['id'])
            if lrc:
                saved = save_lyrics(artist, album, tname, lrc, '')
                results['files'] += len(saved)
                results['ok'] += 1
                if tlrc:
                    saved2 = save_lyrics(artist, album, tname, tlrc, '', '_zh')
                    results['files'] += len(saved2)
            else:
                results['fail'] += 1
        else:
            results['fail'] += 1
        time.sleep(0.5)  # 网易云限流更严
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=20, help='处理专辑数量')
    parser.add_argument('--album-id', type=int, default=None)
    parser.add_argument('--english-only', action='store_true')
    parser.add_argument('--chinese-only', action='store_true')
    parser.add_argument('--skip-existing', action='store_true', default=False)
    args = parser.parse_args()

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    if args.album_id:
        cur.execute("""
            SELECT a.album_id, a.artist, a.album_name,
                   (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as pc
            FROM albums a WHERE a.album_id = ?
        """, (args.album_id,))
    else:
        # 按收听次数排序
        cur.execute("""
            SELECT a.album_id, a.artist, a.album_name, 
                   COALESCE((SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id), 0) as pc,
                   (SELECT COUNT(*) FROM tracks t2 WHERE t2.album_id = a.album_id AND t2.lyrics_lrc_path IS NULL AND t2.lyrics_text_path IS NULL) as missing_count
            FROM albums a
            WHERE a.album_name != '' AND EXISTS (SELECT 1 FROM tracks t WHERE t.album_id = a.album_id)
            ORDER BY missing_count DESC, pc DESC
        """)
    rows = cur.fetchall()
    conn.close()

    # 过滤中文/英文
    if args.english_only:
        rows = [r for r in rows if not is_chinese(r[1]) and not is_chinese(r[2])]
    elif args.chinese_only:
        rows = [r for r in rows if is_chinese(r[1]) or is_chinese(r[2])]

    to_process = rows[:args.limit]
    print(f'待处理: {len(to_process)} 张专辑\n')

    total_ok = total_fail = total_files = total_skip = 0

    for row in to_process:
        # Handle both 4-col (single album) and 5-col (batch) queries
        album_id = row[0]
        artist = row[1]
        album = row[2]
        pc = row[3]
        print(f'=== [{album_id}] {artist} - {album} (收听{pc}次) ===')

        if args.skip_existing and has_lyrics_dir(artist, album):
            continue  # 跳过已有歌词，继续下一个

        # 获取曲目表
        conn2 = sqlite3.connect(DB)
        cur2 = conn2.cursor()
        cur2.execute("""
            SELECT track_number, track_name FROM tracks 
            WHERE album_id = ? ORDER BY disc_number, track_number
        """, (album_id,))
        tracks = cur2.fetchall()
        conn2.close()

        if not tracks:
            print(f'  [SKIP] 无曲目')
            total_skip += 1
            continue
        print(f'  曲目: {len(tracks)} 首')

        # 判断语言
        lang_cn = is_chinese(album) or is_chinese(artist)
        if args.chinese_only:
            lang_cn = True
        elif args.english_only:
            lang_cn = False

        if lang_cn:
            result = process_chinese_album(artist, album, tracks)
        else:
            result = process_english_album(artist, album, tracks)

        total_ok += result['ok']
        total_fail += result['fail']
        total_files += result['files']

        print(f'  OK={result["ok"]} FAIL={result["fail"]} FILES={result["files"]}')
        time.sleep(0.5)

    print(f'\n=== 总计: OK={total_ok} FAIL={total_fail} FILES={total_files} SKIP={total_skip} ===')

if __name__ == '__main__':
    main()
