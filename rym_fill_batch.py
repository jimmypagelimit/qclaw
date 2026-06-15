#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RYM 批量回填管道 v1
用法: python rym_fill_batch.py [--limit N] [--start-id ID]
"""

import sys
import time
import json
import re
import sqlite3
import subprocess

DB_PATH = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
RYM_TOOL = r'C:\Users\qujt\.qclaw\workspace\rym_tool.py'


def is_chinese(text):
    """检查是否包含中文"""
    return bool(re.search(r'[\u4e00-\u9fa5]', text or ''))


def get_albums_to_fill(limit=10, start_id=None):
    """获取待回填的专辑（优先非中文）"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    query = '''
        SELECT album_id, album_name, artist
        FROM albums
        WHERE rym_rating IS NULL
    '''
    if start_id:
        query += f' AND album_id >= {start_id}'
    query += f' ORDER BY album_id LIMIT {limit * 5}'  # 多取一些，过滤中文后取前N个
    
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    
    # 过滤中文艺人
    non_chinese = [r for r in rows if not is_chinese(r[2])]
    return non_chinese[:limit]


def update_db(album_id, data):
    """更新数据库中的 RYM 字段"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute('''
        UPDATE albums
        SET rym_rating = ?,
            rym_ratings_count = ?,
            rym_url = ?
        WHERE album_id = ?
    ''', (
        data.get('rating'),
        data.get('ratings_count'),
        data.get('url'),
        album_id
    ))
    
    conn.commit()
    conn.close()
    print(f'  -> DB updated: album_id={album_id}')


def fetch_rym(album_name, artist):
    """调用 rym_tool.py 抓取"""
    cmd = [r'C:\Python311\python.exe', RYM_TOOL, album_name, artist]
    print(f'  Running: rym_tool.py "{album_name}" "{artist}"')
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, encoding='utf-8', errors='replace')
        if result.returncode != 0:
            print(f'  ERROR: {result.stderr}')
            return None
        
        # 读取输出 JSON
        json_file = f'rym_{artist.replace(" ", "_")}_{album_name.replace(" ", "_")}.json'
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f'  JSON not found: {json_file}')
            return None
            
    except subprocess.TimeoutExpired:
        print('  ERROR: Timeout (>120s)')
        return None


def main():
    limit = 10
    start_id = None
    
    # 解析参数
    args = sys.argv[1:]
    if '--limit' in args:
        idx = args.index('--limit')
        limit = int(args[idx + 1])
    if '--start-id' in args:
        idx = args.index('--start-id')
        start_id = int(args[idx + 1])
    
    print(f'=== RYM Batch Fill (limit={limit}) ===\n')
    
    albums = get_albums_to_fill(limit, start_id)
    print(f'Found {len(albums)} albums to fill\n')
    
    success = 0
    failed = 0
    
    for i, (album_id, album_name, artist) in enumerate(albums, 1):
        print(f'[{i}/{len(albums)}] {album_name} - {artist} (id={album_id})')
        
        data = fetch_rym(album_name, artist)
        if data and data.get('rating'):
            update_db(album_id, data)
            success += 1
        else:
            print('  -> SKIP (no rating)')
            failed += 1
        
        # 间隔避免被 ban
        if i < len(albums):
            print('  Waiting 5s...\n')
            time.sleep(5)
    
    print(f'\n=== Done: {success} success, {failed} failed ===')


if __name__ == '__main__':
    main()
