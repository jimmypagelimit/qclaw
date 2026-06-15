#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RYM 批量回填管道 v2 - 单会话版
用法: python rym_fill_session.py [--limit N]
"""

import sys
import time
import json
import re
import sqlite3
from cloakbrowser import launch

DB_PATH = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
BASE_URL = "https://rateyourmusic.com"


def is_chinese(text):
    """检查是否包含中文"""
    return bool(re.search(r'[\u4e00-\u9fa5]', text or ''))


def get_albums_to_fill(limit=10):
    """获取待回填的专辑（优先非中文）"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute('''
        SELECT album_id, album_name, artist
        FROM albums
        WHERE rym_rating IS NULL
        ORDER BY album_id
        LIMIT 100
    ''')
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


def search_album(page, query):
    """搜索专辑"""
    try:
        search_box = page.locator("#ui_search_input_main_search").first
        search_box.click(timeout=5000)
        time.sleep(0.3)
        search_box.fill("")
        time.sleep(0.2)
        search_box.type(query, delay=50)
        time.sleep(0.3)
        search_box.press("Enter")
        time.sleep(10)
        return True
    except Exception as e:
        print(f'  Search error: {e}')
        return False


def click_first_album(page):
    """点击第一个专辑链接"""
    js = """() => {
        const links = document.querySelectorAll('a[href*="/release/"]');
        if (links.length > 0) {
            links[0].click();
            return true;
        }
        return false;
    }"""
    page.evaluate(js)
    time.sleep(12)
    return True


def extract_album_info(page):
    """从 HTML 提取专辑信息"""
    import re
    html = page.content()
    info = {}
    
    # 专辑名
    m = re.search(r'<title>(.*?)\s+by\s+', html, re.DOTALL)
    info['title'] = m.group(1).strip() if m else "N/A"
    
    # 艺人名
    m = re.search(r'class="artist"[^>]*>(.*?)</(?:a|span)', html, re.DOTALL)
    if m:
        artist_clean = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        info['artist'] = artist_clean
    else:
        info['artist'] = "N/A"
    
    # 评分
    m = re.search(r'avg_rating"\s*:\s*([\d.]+)', html)
    info['rating'] = float(m.group(1)) if m else None
    
    # 评价数
    m = re.search(r'rating_count"\s*:\s*(\d+)', html)
    info['ratings_count'] = int(m.group(1)) if m else 0
    
    # URL
    m = re.search(r'"url"\s*:\s*"(/release/[^"]+)"', html)
    info['url'] = BASE_URL + m.group(1) if m else None
    
    return info


def main():
    limit = 10
    if '--limit' in sys.argv:
        idx = sys.argv.index('--limit')
        limit = int(sys.argv[idx + 1])
    
    print(f'=== RYM Batch Fill v2 (limit={limit}) ===\n')
    
    albums = get_albums_to_fill(limit)
    print(f'Found {len(albums)} albums to fill\n')
    
    if not albums:
        print('No albums to fill.')
        return
    
    # 启动浏览器（只启动一次）
    print('[0] Launching CloakBrowser...')
    browser = launch(headless=False)
    page = browser.new_page()
    page.goto(BASE_URL)
    print('  Waiting for CF challenge (25s)...')
    time.sleep(25)
    print('  Ready.\n')
    
    success = 0
    failed = 0
    
    for i, (album_id, album_name, artist) in enumerate(albums, 1):
        print(f'[{i}/{len(albums)}] {album_name} - {artist} (id={album_id})')
        
        try:
            # 搜索
            query = f"{album_name} {artist}"
            if not search_album(page, query):
                print('  -> SKIP (search failed)')
                failed += 1
                continue
            
            # 点击第一个结果
            click_first_album(page)
            
            # 提取信息
            info = extract_album_info(page)
            
            if info.get('rating'):
                print(f"  -> Rating: {info['rating']} / 5 ({info['ratings_count']} ratings)")
                update_db(album_id, info)
                success += 1
            else:
                print('  -> SKIP (no rating found)')
                failed += 1
            
            # 返回首页准备下一次搜索
            page.evaluate('window.location.href = "https://rateyourmusic.com/"')
            time.sleep(5)
            
        except Exception as e:
            print(f'  -> ERROR: {e}')
            failed += 1
        
        # 间隔
        if i < len(albums):
            print('  Waiting 3s...\n')
            time.sleep(3)
    
    print(f'\n=== Done: {success} success, {failed} failed ===')


if __name__ == '__main__':
    main()
