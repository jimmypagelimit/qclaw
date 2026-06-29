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
        return []

def lrclib_get(lrc_id, timeout=15):
    """获取歌词内容"""
    url = f"{LRCLIB_BASE}/get/{lrc_id}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return None

def save_lyrics(artist, album, track_name, lrc_text, plain_text):
    """保存歌词文件"""
    safe_artist = "".join(c for c in artist if c not in r'\\/:*?"<>|').strip()
    safe_album = "".join(c for c in album if c not in r'\\/:*?"<>|').strip()
    safe_track = "".join(c for c in track_name if c not in r'\\/:*?"<>|').strip()
    
    base = os.path.join(LYRICS_DIR, safe_artist, safe_album)
    os.makedirs(base, exist_ok=True)
    
    lrc_path = None
    txt_path = None
    
    if lrc_text:
        lrc_path = os.path.join(base, f"{safe_track}.lrc")
        with open(lrc_path, 'w', encoding='utf-8') as f:
            f.write(lrc_text)
    
    if plain_text:
        txt_path = os.path.join(base, f"{safe_track}.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(plain_text)
    
    return lrc_path, txt_path

def process_album(artist, album, conn, dry_run=False):
    """处理一张专辑的缺失歌词"""
    print(f"\n{'='*60}")
    print(f"处理: {artist} - {album}")
    print(f"{'='*60}")
    
    cursor = conn.cursor()
    
    # 查询缺少歌词的曲目（需要JOIN albums表）
    cursor.execute("""
        SELECT t.id, t.track_number, t.track_name 
        FROM tracks t
        JOIN albums a ON t.album_id = a.id
        WHERE a.album_name = ? AND a.artist = ?
        AND (t.lyrics_text_path IS NULL OR t.lyrics_lrc_path IS NULL)
        ORDER BY t.track_number
    """, (album, artist))
    
    tracks = cursor.fetchall()
    
    if not tracks:
        print(f"  [√] 所有曲目已有歌词")
        return {'ok': 0, 'fail': 0, 'no_lyrics': 0, 'total': 0, 'skipped': len(tracks)}
    
    print(f"  需要获取 {len(tracks)} 首曲目歌词")
    
    # 获取歌词
    ok = fail = no_lyrics = 0
    
    for track_id, track_number, track_name in tracks:
        print(f"  [{track_number:2d}] {track_name}")
        
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
            
            if dry_run:
                print(f"      [DRY RUN] 将保存歌词")
                ok += 1
            else:
                lrc_path, txt_path = save_lyrics(artist, album, track_name, lrc, plain)
                
                # 更新数据库
                cursor.execute("""
                    UPDATE tracks 
                    SET lyrics_text_path = ?, lyrics_lrc_path = ?
                    WHERE id = ?
                """, (txt_path, lrc_path, track_id))
                
                print(f"      OK: {txt_path}")
                ok += 1
            
        except Exception as e:
            print(f"      ERR: {e}")
            fail += 1
        
        time.sleep(1)  # 避免请求过快
    
    if not dry_run:
        conn.commit()
    
    print(f"\n{'='*60}")
    print(f"结果: OK={ok} FAIL={fail} NONE={no_lyrics} TOTAL={len(tracks)}")
    print(f"{'='*60}")
    
    return {'ok': ok, 'fail': fail, 'no_lyrics': no_lyrics, 'total': len(tracks)}

def main():
    import sys
    
    dry_run = '--dry-run' in sys.argv
    
    if dry_run:
        print("[DRY RUN 模式 - 不会实际保存]")
        sys.argv.remove('--dry-run')
    
    if len(sys.argv) >= 3:
        artist = sys.argv[1]
        album = " ".join(sys.argv[2:])
        
        db_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
        conn = sqlite3.connect(db_path)
        
        try:
            process_album(artist, album, conn, dry_run=dry_run)
        finally:
            conn.close()
    else:
        print("用法: python simple_lyrics_v2.py [--dry-run] <艺人> <专辑>")
        print("例如: python simple_lyrics_v2.py \"Supertramp\" \"Crisis? What Crisis?\"")
        sys.exit(1)

if __name__ == '__main__':
    main()
