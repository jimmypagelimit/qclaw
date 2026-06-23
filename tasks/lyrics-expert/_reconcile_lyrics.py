#!/usr/bin/env python3
"""
歌词对账 + 抓取脚本
1. 扫描磁盘 lyrics/ 目录，建立 {artist}/{album}/{track}.txt → 真实路径 映射
2. 对每个 lyrics_text_path 为 NULL/空 的 track：
   a. 尝试从磁盘匹配（英文艺人名）
   b. 如果磁盘也没有，从 LRCLIB 抓取
3. 统计真实缺口
"""
import os, sqlite3, json, time, urllib.request, urllib.parse, re
from collections import defaultdict

# ===== Config =====
DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_BASE = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'
UA = "AlbumTracker/1.0 (jim@example.com)"
LRCLIB_BASE = "https://lrclib.net/api"

os.makedirs(LYRICS_BASE, exist_ok=True)

# ===== Step 1: 建立磁盘歌词索引 =====
# disk_index: {(artist_lower, album_lower, track_lower): absolute_path}
disk_index = {}
disk_count = 0

for artist_dir in os.listdir(LYRICS_BASE):
    artist_path = os.path.join(LYRICS_BASE, artist_dir)
    if not os.path.isdir(artist_path):
        continue
    for album_dir in os.listdir(artist_path):
        album_path = os.path.join(artist_path, album_dir)
        if not os.path.isdir(album_path):
            continue
        for fname in os.listdir(album_path):
            if not fname.endswith(('.txt', '.lrc')):
                continue
            track_name = os.path.splitext(fname)[0]
            key = (artist_dir.lower(), album_dir.lower(), track_name.lower())
            fpath = os.path.join(album_path, fname)
            # 存第一个（.txt优先）
            if key not in disk_index:
                disk_index[key] = fpath
                disk_count += 1

print(f"[1] 磁盘歌词索引: {len(disk_index)} 个唯一 (artist/album/track) 组合, {disk_count} 文件")

# ===== Step 2: 数据库扫描，找缺失的 track =====
conn = sqlite3.connect(DB)
cur = conn.cursor()

# 找 lyrics_text_path 为 NULL 或 '' 的 tracks
cur.execute('''
SELECT t.id, t.album_id, t.track_name, a.artist, a.album_name
FROM tracks t
JOIN albums a ON t.album_id = a.album_id
WHERE t.lyrics_text_path IS NULL OR t.lyrics_text_path = ''
ORDER BY a.artist, a.album_name, t.track_name
''')
missing_tracks = cur.fetchall()
print(f"[2] DB中 lyrics_text_path 为空的 tracks: {len(missing_tracks)}")

# ===== Step 3: 尝试从磁盘匹配（仅英文艺人名，避免中文GBK问题）=====
fixed_from_disk = 0
to_fetch = []

# 判断是否像乱码（GBK decode失败说明是乱码路径）
def looks_garbled(s):
    if s is None:
        return True
    try:
        s.encode('utf-8').decode('utf-8')
        # 检查是否含常见乱码模式
        return '\ufffd' in s or ('�' in s)
    except:
        return True

for track_id, album_id, track_name, artist, album_name in missing_tracks:
    # 尝试在磁盘索引中查找
    # 清理 track_name（去掉末尾的 . 和编号）
    clean_track = re.sub(r'[\.。]+$', '', track_name.strip())
    # 尝试多个匹配key
    candidates = [
        (artist.lower().strip(), album_name.lower().strip(), clean_track.lower().strip()),
        (artist.lower().strip(), album_name.lower().strip(), track_name.lower().strip()),
    ]
    
    matched = None
    for key in candidates:
        if key in disk_index:
            matched = disk_index[key]
            break
    
    if matched:
        # 更新 DB path（用磁盘真实路径）
        cur.execute('UPDATE tracks SET lyrics_text_path=? WHERE id=?', (matched, track_id))
        fixed_from_disk += 1

print(f"[3] 从磁盘匹配并修复: {fixed_from_disk} 条")

# ===== Step 4: 对剩余缺失的 track 尝试 LRCLIB =====
conn.commit()

# 重新查剩余缺失
cur.execute('''
SELECT t.id, t.album_id, t.track_name, a.artist, a.album_name
FROM tracks t
JOIN albums a ON t.album_id = a.album_id
WHERE t.lyrics_text_path IS NULL OR t.lyrics_text_path = ''
''')
remaining = cur.fetchall()
print(f"[4] 剩余无法从磁盘匹配的缺失 tracks: {len(remaining)}")

# 分类：英文 vs 其他
english_remaining = []
other_remaining = []
for row in remaining:
    artist = row[3]
    # 简单判断是否全ASCII
    try:
        artist.encode('ascii')
        english_remaining.append(row)
    except UnicodeEncodeError:
        other_remaining.append(row)

print(f"    其中英文艺人: {len(english_remaining)}")
print(f"    其中非英文艺人（含中文/其他）: {len(other_remaining)}")

# ===== Step 5: 从 LRCLIB 抓取英文艺人缺失歌词 =====
LRCLIB_DIR = LYRICS_BASE

def lrclib_search(artist, track, timeout=15):
    params = urllib.parse.urlencode({'q': f'{artist} {track}'})
    url = f"{LRCLIB_BASE}/search?{params}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            results = json.loads(resp.read())
        # 过滤掉 instrumental=true 的
        results = [r for r in results if not r.get('instrumental', False)]
        return results
    except Exception as e:
        return []

def save_lyrics(artist, album, track_name, lrc_text, plain_text):
    safe = lambda s: "".join(c for c in s if c not in r'\/:*?"<>|').strip()
    base = os.path.join(LRCLIB_DIR, safe(artist), safe(album))
    os.makedirs(base, exist_ok=True)
    saved = []
    if lrc_text:
        p = os.path.join(base, f"{safe(track_name)}.lrc")
        with open(p, 'w', encoding='utf-8') as f:
            f.write(lrc_text)
        saved.append(p)
    if plain_text:
        p = os.path.join(base, f"{safe(track_name)}.txt")
        with open(p, 'w', encoding='utf-8') as f:
            f.write(plain_text)
        saved.append(p)
    return saved

# 对英文缺失 track，尝试 LRCLIB（前20首测试）
lrclib_ok = 0
lrclib_none = 0
lrclib_instrumental = 0

print(f"\n[5] LRCLIB 抓取测试（前 {min(20, len(english_remaining))} 首英文缺失track）...")
for i, (track_id, album_id, track_name, artist, album_name) in enumerate(english_remaining[:20]):
    print(f"  [{i+1}/20] {artist} - {track_name}")
    results = lrclib_search(artist, track_name)
    if not results:
        lrclib_none += 1
        print(f"      -> 无结果")
        time.sleep(0.5)
        continue
    
    # 取第一个结果
    best = results[0]
    # get full lyrics
    lrc_url = f"{LRCLIB_BASE}/get/{best['id']}"
    try:
        req = urllib.request.Request(lrc_url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=15) as resp:
            full = json.loads(resp.read())
    except:
        lrclib_none += 1
        time.sleep(0.5)
        continue
    
    lrc_text = full.get('syncedLyrics', '')
    plain_text = full.get('plainLyrics', '')
    
    if not lrc_text and not plain_text:
        lrclib_instrumental += 1
        print(f"      -> 纯器乐（无歌词）")
        time.sleep(0.5)
        continue
    
    saved = save_lyrics(artist, album_name, track_name, lrc_text, plain_text)
    if saved:
        # 更新 DB
        cur.execute('UPDATE tracks SET lyrics_text_path=? WHERE id=?', (saved[0], track_id))
        conn.commit()
        lrclib_ok += 1
        print(f"      -> 成功: {saved[0]}")
    
    time.sleep(1)

print(f"\n[6] LRCLIB 结果: 成功={lrclib_ok}, 无结果={lrclib_none}, 纯器乐={lrclib_instrumental}")

# ===== Summary =====
cur.execute('SELECT COUNT(*) FROM tracks WHERE lyrics_text_path IS NULL OR lyrics_text_path = ?', ('',))
still_missing = cur.fetchone()[0]
cur.execute('SELECT COUNT(*) FROM tracks')
total = cur.fetchone()[0]

print(f"\n=== 总结 ===")
print(f"总 tracks: {total}")
print(f"有 lyrics_text_path: {total - still_missing}")
print(f"仍缺失: {still_missing}")
print(f"  - 其中英文艺人: {len(english_remaining) - lrclib_ok} (LRCLIB无可用歌词)")
print(f"  - 其中非英文艺人: {len(other_remaining)} (需单独处理)")

conn.close()
