#!/usr/bin/env python3
"""RYM 数据库回填管道"""
import sqlite3, json, subprocess, re, sys, time
from pathlib import Path

DB_PATH = Path(r"C:\Users\qujt\.qclaw\workspace\_music_latest.db")
RYM_TOOL = Path(r"C:\Users\qujt\.qclaw\workspace\rym_tool.py")

def search_rym(album, artist):
    """调用 rym_tool.py 搜索"""
    cmd = [r"C:\Python311\python.exe", str(RYM_TOOL), album, artist]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    
    # 查找 JSON 输出文件
    json_file = Path(f"rym_{artist.replace(' ', '_')}_{album.replace(' ', '_')}.json")
    if json_file.exists():
        data = json.loads(json_file.read_text(encoding='utf-8'))
        json_file.unlink()  # 清理
        return data
    return None

def fill_database(limit=50, dry_run=False):
    """回填数据库"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # 查询无 RYM 评分的专辑
    rows = conn.execute("""
        SELECT album_id, album_name, artist
        FROM albums
        WHERE rym_rating IS NULL
        ORDER BY album_id DESC
        LIMIT ?
    """, (limit,)).fetchall()
    
    print(f"[RYM DB] 待回填: {len(rows)} 张专辑")
    
    hits = 0
    for i, r in enumerate(rows):
        artist = r['artist']
        album = r['album_name']
        print(f"  [{i+1}/{len(rows)}] {artist[:20]:20s} — {album[:30]:30s}", end="", flush=True)
        
        if dry_run:
            print(" (dry-run)")
            continue
        
        result = search_rym(album, artist)
        if result and 'rating' in result and result['rating'] != 'N/A':
            try:
                rating = float(result['rating'])
                ratings_count = result.get('num_ratings', '').replace(',', '')
                ratings_count = int(ratings_count) if ratings_count.isdigit() else None
                
                conn.execute("""
                    UPDATE albums
                    SET rym_rating = ?, rym_ratings_count = ?, rym_url = ?
                    WHERE album_id = ?
                """, (rating, ratings_count, result.get('url', ''), r['album_id']))
                conn.commit()
                hits += 1
                print(f" RYM={rating}")
            except:
                print(" 解析失败")
        else:
            print(" not-found")
        
        # 清理截图
        for f in ["rym_search.png", "rym_album.png"]:
            if Path(f).exists():
                Path(f).unlink()
        
        time.sleep(1)
    
    conn.close()
    print(f"[RYM DB] 完成: {hits}/{len(rows)}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    fill_database(limit=args.limit, dry_run=args.dry_run)
