#!/usr/bin/env python3
"""
L项目 - 歌词计划推进报告
1. 统计当前进度
2. 识别缺失/不完整的专辑
3. 生成下一步行动建议
"""
import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
LYRICS_DIR = BASE_DIR / "lyrics"
TRACKLISTS_DIR = BASE_DIR / "tracklists"
DB_PATH = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"

def count_lyrics(artist, album):
    """统计专辑的歌词文件数"""
    safe_artist = "".join(c for c in artist if c not in r'\\/:*?"<>|').strip()
    safe_album = "".join(c for c in album if c not in r'\\/:*?"<>|').strip()
    path = LYRICS_DIR / safe_artist / safe_album
    if not path.exists():
        return -1  # 目录不存在
    return len(list(path.glob("*.*")))

def main():
    print("=== L项目 - 歌词计划进度报告 ===\n")
    
    # 1. 数据库统计
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM albums")
    total_albums = cursor.fetchone()[0]
    print(f"📀 数据库专辑总数: {total_albums}")
    
    # 2. 歌词目录统计
    if LYRICS_DIR.exists():
        artists = [d for d in LYRICS_DIR.iterdir() if d.is_dir()]
        processed = 0
        incomplete = []
        no_lyrics = []
        
        for artist_dir in artists:
            for album_dir in artist_dir.iterdir():
                if not album_dir.is_dir():
                    continue
                processed += 1
                files = list(album_dir.glob("*.*"))
                # 检查是否有.lrc或.txt文件
                has_content = any(f.suffix in ['.lrc', '.txt'] for f in files)
                if not has_content or len(files) == 0:
                    incomplete.append((artist_dir.name, album_dir.name, len(files)))
        
        print(f"✅ 已处理专辑数: {processed}")
        print(f"⚠️  不完整专辑数: {len(incomplete)}")
        print(f"📂 歌词文件总数: {sum(len(list(p.glob('*.*'))) for p in LYRICS_DIR.rglob('*') if p.is_file())}")
        
        if incomplete:
            print(f"\n⚠️  不完整专辑 (前10张):")
            for artist, album, count in incomplete[:10]:
                print(f"  - {artist} / {album} ({count} files)")
    else:
        print("[X] lyrics目录不存在")
    
    # 3. 识别未处理专辑
    print(f"\n{'='*50}")
    print("📋 未处理专辑识别中...")
    
    cursor.execute("SELECT album_name, artist FROM albums")
    all_albums = cursor.fetchall()
    
    processed_set = set()
    if LYRICS_DIR.exists():
        for artist_dir in LYRICS_DIR.iterdir():
            if not artist_dir.is_dir():
                continue
            artist = artist_dir.name
            for album_dir in artist_dir.iterdir():
                if album_dir.is_dir():
                    processed_set.add((album_dir.name, artist))
    
    unprocessed = []
    for album_name, artist in all_albums:
        if (album_name, artist) not in processed_set:
            unprocessed.append((album_name, artist))
    
    print(f"✅ 未处理专辑数: {len(unprocessed)}")
    
    if unprocessed:
        print(f"\n📝 未处理专辑 (前20张):")
        for i, (album, artist) in enumerate(unprocessed[:20], 1):
            print(f"  {i}. {artist} - {album}")
        
        # 保存完整列表
        output_file = BASE_DIR.parent / "unprocessed_albums_v2.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"未处理专辑总数: {len(unprocessed)}\n\n")
            for i, (album, artist) in enumerate(unprocessed, 1):
                f.write(f"{i}. {artist} - {album}\n")
        print(f"\n💾 完整列表已保存: {output_file}")
    
    # 4. 建议
    print(f"\n{'='*50}")
    print("🎯 下一步建议:")
    print("  1. 手动运行 lyrics_pipeline.py 处理高优先级专辑")
    print("  2. 对于中文专辑，接入网易云歌词API")
    print("  3. 对于LRCLIB未命中的，尝试LyricsTranslate")
    print(f"  4. 建议每次处理5-10张，避免被限流")
    
    conn.close()

if __name__ == "__main__":
    main()
