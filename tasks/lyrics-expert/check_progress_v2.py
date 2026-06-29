#!/usr/bin/env python3
"""
L项目 - 歌词计划进度报告 (简化版，无Unicode)
"""
import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
LYRICS_DIR = BASE_DIR / "lyrics"
DB_PATH = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"

def main():
    report_lines = []
    report_lines.append("=" * 50)
    report_lines.append("L项目 - 歌词计划进度报告")
    report_lines.append("=" * 50)
    report_lines.append("")
    
    # 1. 数据库统计
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM albums")
    total_albums = cursor.fetchone()[0]
    report_lines.append(f"[1] 数据库专辑总数: {total_albums}")
    
    # 2. 歌词目录统计
    if LYRICS_DIR.exists():
        artists = [d for d in LYRICS_DIR.iterdir() if d.is_dir()]
        processed_count = 0
        total_files = 0
        
        for artist_dir in artists:
            for album_dir in artist_dir.iterdir():
                if not album_dir.is_dir():
                    continue
                processed_count += 1
                files = list(album_dir.glob("*.*"))
                total_files += len(files)
        
        report_lines.append(f"[2] 已处理专辑数: {processed_count}")
        report_lines.append(f"[3] 歌词文件总数: {total_files}")
        report_lines.append(f"[4] 涉及艺人目录: {len(artists)}")
        
        # 计算进度
        progress = (processed_count / total_albums * 100) if total_albums > 0 else 0
        report_lines.append(f"[5] 完成进度: {progress:.1f}%")
    else:
        report_lines.append("[X] lyrics目录不存在")
    
    # 3. 识别未处理专辑
    report_lines.append("")
    report_lines.append("=" * 50)
    report_lines.append("[6] 未处理专辑识别中...")
    
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
    
    report_lines.append(f"[7] 未处理专辑数: {len(unprocessed)}")
    
    if unprocessed:
        report_lines.append("")
        report_lines.append("[8] 未处理专辑 (前15张):")
        for i, (album, artist) in enumerate(unprocessed[:15], 1):
            report_lines.append(f"  {i}. {artist} - {album}")
    
    # 4. 建议
    report_lines.append("")
    report_lines.append("=" * 50)
    report_lines.append("[9] 下一步建议:")
    report_lines.append("  a) 优先处理西方艺人专辑 (LRCLIB命中率高)")
    report_lines.append("  b) 中文专辑接入网易云API")
    report_lines.append("  c) 批量处理建议: 每次5-10张")
    report_lines.append("  d) 当前瓶颈: Playwright自动化需要调试")
    
    # 保存报告
    output_file = Path(__file__).parent.parent / "lyrics_plan_report.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    # 打印到控制台 (ASCII only)
    print('\n'.join(report_lines))
    print(f"\n[OK] 报告已保存: {output_file}")
    
    conn.close()

if __name__ == "__main__":
    main()
