import sqlite3
import urllib.request
import urllib.parse
import json
import os
import time

LRCLIB_BASE = "https://lrclib.net/api"
UA = "AlbumTracker/1.0 (jim@example.com)"
LYRICS_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics"

def lrclib_search(artist, track, timeout=15):
    """搜索歌词"""
    params = urllib.parse.urlencode({'q': f'{artist} {track}'})
    url = f"{LRCLIB_BASE}/search?{params}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"      LRCLIB搜索失败: {e}")
        return []

def lrclib_get(lrc_id, timeout=15):
    """获取歌词内容"""
    url = f"{LRCLIB_BASE}/get/{lrc_id}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"      LRCLIB获取失败: {e}")
        return None

def save_lyrics(artist, album, track_name, lrc_text, plain_text):
    """保存歌词文件"""
    safe_artist = "".join(c for c in artist if c not in r'\\/:*?"<>|').strip()
    safe_album = "".join(c for c in album if c not in r'\\/:*?"<>|').strip()
    safe_track = "".join(c for c in track_name if c not in r'\\/:*?"<>|').strip()
    
    base = os.path.join(LYRICS_DIR, safe_artist, safe_album)
    os.makedirs(base, exist_ok=True)
    
    saved = []
    if lrc_text:
        path = os.path.join(base, f"{safe_track}.lrc")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(lrc_text)
        saved.append(path)
    if plain_text:
        path = os.path.join(base, f"{safe_track}.txt")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(plain_text)
        saved.append(path)
    return saved

def process_album(artist, album):
    """处理一张专辑"""
    print(f"\n{'='*60}")
    print(f"处理: {artist} - {album}")
    print(f"{'='*60}")
    
    # 从数据库获取曲目列表
    db_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询曲目
    cursor.execute("""
        SELECT track_name, duration_ms 
        FROM tracks 
        WHERE album_name = ? AND artist = ?
        ORDER BY track_number
    """, (album, artist))
    
    tracks = cursor.fetchall()
    conn.close()
    
    if not tracks:
        print(f"  [X] 数据库中未找到曲目")
        return None
    
    print(f"  找到 {len(tracks)} 首曲目")
    
    # 获取歌词
    ok = fail = no_lyrics = 0
    
    for i, (track_name, duration_ms) in enumerate(tracks, 1):
        print(f"  [{i:2d}] {track_name}")
        
        try:
            results = lrclib_search(artist, track_name)
            if not results:
                print(f"      -- 无结果")
                no_lyrics += 1
                time.sleep(1)
                continue
            
            # 获取第一首匹配的歌词
            full = lrclib_get(results[0]['id'])
            if not full:
                fail += 1
                time.sleep(1)
                continue
            
            lrc = full.get('syncedLyrics', '')
            plain = full.get('plainLyrics', '')
            
            if not lrc and not plain:
                print(f"      -- 无歌词内容")
                no_lyrics += 1
                time.sleep(1)
                continue
            
            saved = save_lyrics(artist, album, track_name, lrc, plain)
            print(f"      OK: {len(saved)} 个文件")
            ok += 1
            
        except Exception as e:
            print(f"      ERR: {e}")
            fail += 1
        
        time.sleep(1)  # 避免请求过快
    
    print(f"\n{'='*60}")
    print(f"结果: OK={ok} FAIL={fail} NONE={no_lyrics} TOTAL={len(tracks)}")
    print(f"{'='*60}")
    
    return {'ok': ok, 'fail': fail, 'no_lyrics': no_lyrics, 'total': len(tracks)}

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) >= 3:
        artist = sys.argv[1]
        album = " ".join(sys.argv[2:])
    else:
        print("用法: python simple_lyrics.py <艺人> <专辑>")
        sys.exit(1)
    
    process_album(artist, album)
