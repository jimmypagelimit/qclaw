#!/usr/bin/env python3
"""
L 项目 - 英文歌词批量获取 v2
直接从 DB tracks 表取曲目，LRCLIB 逐首搜索
"""
import json, os, sys, time, sqlite3, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
BASE = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert'
LYRICS = os.path.join(BASE, "lyrics")
LRCLIB = "https://lrclib.net/api"
UA = "AlbumTracker/1.0 (jim@163.com)"
os.makedirs(LYRICS, exist_ok=True)

def safe(s):
    return "".join(c for c in s if c not in r'\/:*?"<>|').strip()[:120]

def has_lyrics(artist, album):
    d = os.path.join(LYRICS, safe(artist), safe(album))
    return os.path.exists(d) and any(f.endswith('.lrc') for f in os.listdir(d))

def save(artist, album, track, lrc, txt):
    d = os.path.join(LYRICS, safe(artist), safe(album))
    os.makedirs(d, exist_ok=True)
    fn = safe(track)[:80]
    r = []
    if lrc:
        p = os.path.join(d, fn + '.lrc')
        with open(p, 'w', encoding='utf-8') as f: f.write(lrc)
        r.append(p)
    if txt:
        p = os.path.join(d, fn + '.txt')
        with open(p, 'w', encoding='utf-8') as f: f.write(txt)
        r.append(p)
    return r

def is_cn(s):
    if not s: return False
    return sum(1 for c in s if '\u4e00' <= c <= '\u9fff') > 0

def fetch(artist, track):
    q = f'{artist} {track}'
    url = f'{LRCLIB}/search?q={urllib.parse.quote(q)}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        r = json.loads(urllib.request.urlopen(req, timeout=10).read())
        if r:
            return r[0].get('syncedLyrics', ''), r[0].get('plainLyrics', '')
    except: pass
    return '', ''

# 主流程
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("""
    SELECT a.album_id, a.artist, a.album_name,
           COALESCE((SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id), 0) as pc
    FROM albums a
    WHERE EXISTS (SELECT 1 FROM tracks t WHERE t.album_id = a.album_id)
    ORDER BY pc DESC
""")
all_albums = cur.fetchall()
conn.close()

# 过滤英文（非中文）
en_albums = [r for r in all_albums if not is_cn(r[1]) and not is_cn(r[2])]
print(f"英文专辑总数: {len(en_albums)}")

done = 0
EN_TOTAL = len(en_albums)
for idx, (aid, artist, album, pc) in enumerate(en_albums):
    if has_lyrics(artist, album):
        if (idx + 1) % 50 == 0:
            print(f"扫描进度: {idx+1}/{EN_TOTAL}")
        continue  # 跳过已有
    
    # 获取曲目
    conn2 = sqlite3.connect(DB)
    cur2 = conn2.cursor()
    cur2.execute("SELECT track_name FROM tracks WHERE album_id = ? ORDER BY disc_number, track_number", (aid,))
    tracks = [r[0] for r in cur2.fetchall()]
    conn2.close()
    
    print(f"\n[{done+1}] [{aid}] {artist} - {album} ({len(tracks)} tracks, {pc} listens)")
    
    ok = fail = files = 0
    for tname in tracks:
        lrc, txt = fetch(artist, tname)
        if lrc or txt:
            saved = save(artist, album, tname, lrc, txt)
            files += len(saved)
            ok += 1
        else:
            fail += 1
        time.sleep(0.3)
    
    print(f"  OK={ok} FAIL={fail} FILES={files}")
    done += 1
    
    # 每15张停一下
    if done % 15 == 0:
        print(f"\n--- 已处理 {done} 张，暂停5秒 ---")
        time.sleep(5)

print(f"\n=== 完成！本次处理 {done} 张 ===")
