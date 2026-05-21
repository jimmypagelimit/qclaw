#!/usr/bin/env python3
"""
从 Markdown 文件解析 2026 年听歌记录并入库到 SQLite 数据库。
双表同步：写入 albums_2026 + albums 总表。

用法: python import_2026.py
"""

import re
import os
import glob
import sqlite3
import sys
import io

# Windows 终端 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DB_PATH = r"G:\原创计划\music"

# ==================== Markdown 解析 ====================

def parse_markdown_files(directory, category):
    """解析目录下所有月份 Markdown 文件，返回专辑列表"""
    albums = []
    
    for filepath in sorted(glob.glob(os.path.join(directory, "*.md"))):
        filename = os.path.basename(filepath)
        month_match = re.search(r'(\d+)月', filename)
        if not month_match:
            continue
        month = int(month_match.group(1))
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析专辑条目
        # 格式: * 《专辑名》 - 艺术家 数字
        # 也可能有 ## * 或 # * 等变体
        # 数字可能是收听次数（整数）或 RYM 评分（小数）
        current_album = None
        current_rym_info = {}
        
        lines = content.split('\n')
        for line in lines:
            line_stripped = line.strip()
            
            # 匹配专辑行：* 《专辑名》 - 艺术家 数字
            # 支持变体: * / ## * / # * / ### * / #### *
            match = re.match(
                r'^[#*\s]*[*]\s*《(.+?)》\s*[-–—]\s*(.+?)\s+(\d+(?:\.\d+)?)\s*$',
                line_stripped
            )
            if match:
                # 如果上一个专辑有 RYM 信息，保存
                if current_album and current_rym_info:
                    current_album.update(current_rym_info)
                    current_rym_info = {}
                
                album_name = match.group(1).strip()
                artist = match.group(2).strip()
                number = float(match.group(3))
                
                # 判断数字是收听次数还是 RYM 评分
                # 收听次数通常是 1-20 的整数，RYM 评分是 1.0-5.0 的小数
                if number <= 5 and '.' in match.group(3):
                    # 这是 RYM 评分，收听次数默认 1
                    listen_count = 1
                    rym_rating = number
                else:
                    listen_count = int(number)
                    rym_rating = None
                
                current_album = {
                    'album_name': album_name,
                    'artist': artist,
                    'total_listen_count': listen_count,
                    'first_listen_date': f'2026-{month:02d}',
                    'category': category,  # 华语旧 / 外语旧
                }
                if rym_rating is not None:
                    current_album['rym_rating'] = rym_rating
                
                albums.append(current_album)
                continue
            
            # 解析 RYM 信息块（以 > 或空格+> 开头）
            if line_stripped.startswith('>') or (line_stripped and current_album and line.startswith('    ')):
                rym_line = line_stripped.lstrip('>').strip()
                
                # Genres
                genre_match = re.search(r'Genres?\s+(.+)', rym_line)
                if genre_match:
                    genres_str = genre_match.group(1).strip()
                    # 取第一个 genre 作为主 genre
                    genres = [g.strip() for g in re.split(r'[,，]\s*', genres_str) if g.strip()]
                    if genres:
                        current_rym_info['genre'] = genres[0]
                        if len(genres) > 1:
                            current_rym_info['style'] = genres[1] if len(genres) > 1 else None
                
                # Released - 保留完整日期（精确到日）
                release_match = re.search(r'Released\s+(.+)', rym_line)
                if release_match:
                    release_str = release_match.group(1).strip()
                    # 解析完整日期，格式如: "24 April 2026", "1 May 2026"
                    date_match = re.match(r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})', release_str)
                    if date_match:
                        day = date_match.group(1)
                        month_name = date_match.group(2)
                        year = date_match.group(3)
                        months = {'January':'01','February':'02','March':'03','April':'04','May':'05','June':'06','July':'07','August':'08','September':'09','October':'10','November':'11','December':'12'}
                        current_rym_info['release_year'] = f"{year}-{months[month_name]}-{int(day):02d}"
                    else:
                        # 回退：只提取年份
                        year_match = re.search(r'(\d{4})', release_str)
                        if year_match:
                            current_rym_info['release_year'] = year_match.group(1)
                
                # Type
                type_match = re.search(r'Type\s+(.+)', rym_line)
                if type_match:
                    album_type = type_match.group(1).strip()
                    if album_type == 'Compilation':
                        current_rym_info['is_compilation'] = 1
                
                # RYM Rating
                rating_match = re.search(r'RYM Rating\s+([\d.]+)', rym_line)
                if rating_match and current_album:
                    try:
                        current_rym_info['overall_score'] = float(rating_match.group(1))
                    except ValueError:
                        pass
                
                # Language
                lang_match = re.search(r'Language?s?\s+(.+)', rym_line)
                if lang_match and current_album:
                    lang = lang_match.group(1).strip()
                    # 推断国家/地区
                    if lang == 'Chinese':
                        if category == '华语旧':
                            current_rym_info['country'] = '中国'
                    elif lang == 'Spanish':
                        current_rym_info['country'] = '墨西哥'
                    elif lang == 'English':
                        current_rym_info['country'] = '美国'
        
        # 处理最后一个专辑的 RYM 信息
        if current_album and current_rym_info:
            current_album.update(current_rym_info)
    
    return albums


def merge_duplicate_listens(albums):
    """合并同一专辑在不同月份的收听记录"""
    merged = {}
    for a in albums:
        key = (a['album_name'], a['artist'])
        if key in merged:
            # 收听次数累加
            merged[key]['total_listen_count'] += a['total_listen_count']
            # 保留最早的月份
            if a['first_listen_date'] < merged[key]['first_listen_date']:
                merged[key]['first_listen_date'] = a['first_listen_date']
            # 合并 RYM 信息（以有信息的为准）
            for k, v in a.items():
                if k not in ('total_listen_count', 'first_listen_date') and v is not None:
                    if k not in merged[key] or merged[key][k] is None:
                        merged[key][k] = v
        else:
            merged[key] = a.copy()
    return list(merged.values())


# ==================== 数据库操作 ====================

def import_to_db(albums):
    """将专辑数据导入到 albums_2026 和 albums 表"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    stats = {
        'year_inserted': 0,
        'year_updated': 0,
        'total_inserted': 0,
        'total_updated': 0,
        'skipped': 0,
    }
    
    for album in albums:
        album_name = album['album_name']
        artist = album['artist']
        listen_count = album['total_listen_count']
        first_listen = album.get('first_listen_date', '2026-01')
        genre = album.get('genre')
        style = album.get('style')
        country = album.get('country')
        release_year = album.get('release_year')
        is_compilation = album.get('is_compilation', 0)
        overall_score = album.get('overall_score')
        rym_rating = album.get('rym_rating')
        
        # 如果有 RYM 评分但没 overall_score，用 rym_rating
        if overall_score is None and rym_rating is not None:
            overall_score = rym_rating
        
        # ---- 1. 写入 albums_2026 ----
        cur.execute(
            "SELECT album_id, total_listen_count FROM albums_2026 WHERE album_name = ? AND artist = ?",
            (album_name, artist)
        )
        row = cur.fetchone()
        
        if row:
            # 已存在，累加收听次数
            new_count = row['total_listen_count'] + listen_count
            cur.execute(
                "UPDATE albums_2026 SET total_listen_count = ? WHERE album_id = ?",
                (new_count, row['album_id'])
            )
            stats['year_updated'] += 1
        else:
            # 新增
            cur.execute("""
                INSERT INTO albums_2026 
                (album_name, artist, country, region, genre, style, release_year,
                 is_compilation, first_listen_date, total_listen_count, overall_score,
                 release_company, cover_image_url, duration, description,
                 composition_score, lyrics_meaning_score, creativity_score,
                 arrangement_score, vocal_performance_score, instrumental_performance_score,
                 sincerity_score, subjective_score, producer)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                album_name, artist, country, None, genre, style, release_year,
                is_compilation, first_listen, listen_count, overall_score,
                None, None, None, None,
                None, None, None, None, None, None, None, None, None
            ))
            stats['year_inserted'] += 1
        
        # ---- 2. 写入 albums 总表 ----
        cur.execute(
            "SELECT album_id, total_listen_count FROM albums WHERE album_name = ? AND artist = ?",
            (album_name, artist)
        )
        row = cur.fetchone()
        
        if row:
            # 已存在，累加收听次数
            new_count = row['total_listen_count'] + listen_count
            cur.execute(
                "UPDATE albums SET total_listen_count = ? WHERE album_id = ?",
                (new_count, row['album_id'])
            )
            stats['total_updated'] += 1
        else:
            # 新增
            cur.execute("""
                INSERT INTO albums 
                (album_name, artist, country, region, genre, style, release_year,
                 is_compilation, first_listen_date, total_listen_count, overall_score,
                 release_company, cover_image_url, duration, description,
                 composition_score, lyrics_meaning_score, creativity_score,
                 arrangement_score, vocal_performance_score, instrumental_performance_score,
                 sincerity_score, subjective_score, producer)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                album_name, artist, country, None, genre, style, release_year,
                is_compilation, first_listen, listen_count, overall_score,
                None, None, None, None,
                None, None, None, None, None, None, None, None, None
            ))
            stats['total_inserted'] += 1
    
    conn.commit()
    conn.close()
    return stats


# ==================== 主流程 ====================

def main():
    print("=" * 60)
    print("2026 年听歌记录入库")
    print("=" * 60)
    
    base_dir = r"G:\diary-content\history\music\2026"
    
    all_albums = []
    
    # 从命令行参数判断要导入哪些分类
    # 默认导入华语新+外语新（华语旧和外语旧已入库清空）
    if '--all' in sys.argv:
        categories = [
            ("华语旧", "华语旧"),
            ("外语旧", "外语旧"),
            ("华语新", "华语新"),
            ("外语新", "外语新"),
        ]
    else:
        categories = [
            ("华语新", "华语新"),
            ("外语新", "外语新"),
        ]
    
    for dir_name, cat_name in categories:
        cat_dir = os.path.join(base_dir, dir_name)
        if os.path.isdir(cat_dir):
            cat_albums = parse_markdown_files(cat_dir, cat_name)
            print(f"[{dir_name}] 解析到 {len(cat_albums)} 条记录")
            all_albums.extend(cat_albums)
        else:
            print(f"[{dir_name}] 目录不存在，跳过")
    
    # 合并同一专辑的跨月收听
    merged = merge_duplicate_listens(all_albums)
    print(f"\n[合并] {len(merged)} 张唯一专辑 (原 {len(all_albums)} 条)")
    
    # 预览
    print("\n" + "-" * 60)
    print("前 10 张专辑预览:")
    print("-" * 60)
    for a in merged[:10]:
        listen = a['total_listen_count']
        month = a.get('first_listen_date', '?')
        genre = a.get('genre', '-')
        country = a.get('country', '-')
        print(f"  《{a['album_name']}》 - {a['artist']}  [{listen}次] {month} {genre} {country}")
    
    if len(merged) > 10:
        print(f"  ... 还有 {len(merged) - 10} 张\n")
    
    # 确认
    print(f"\n即将导入 {len(merged)} 张专辑到 albums_2026 和 albums 表")
    if '--yes' not in sys.argv and '-y' not in sys.argv:
        confirm = input("确认导入？(y/N) ").strip().lower()
        if confirm != 'y':
            print("已取消")
            return
    else:
        print("[自动确认]")
    
    # 导入
    stats = import_to_db(merged)
    
    print("\n" + "=" * 60)
    print("导入完成！")
    print("=" * 60)
    print(f"  albums_2026: 新增 {stats['year_inserted']} 条, 更新 {stats['year_updated']} 条")
    print(f"  albums 总表: 新增 {stats['total_inserted']} 条, 更新 {stats['total_updated']} 条")


if __name__ == '__main__':
    main()
