#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RYM 批量回填管道 v3 - 艺人页路径 + JS导航
用法: python rym_fill_v3.py [--limit N]

改进:
1. 先搜艺人页 → 在艺人作品列表找专辑（精确匹配）
2. 用 location.href 代替 page.goto（绕过 CF）
3. 结果验证（艺人名必须匹配）
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
    return bool(re.search(r'[\u4e00-\u9fa5]', text or ''))


def get_albums_to_fill(limit=10):
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
    non_chinese = [r for r in rows if not is_chinese(r[2])]
    return non_chinese[:limit]


def update_db(album_id, data):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        UPDATE albums
        SET rym_rating = ?,
            rym_ratings_count = ?,
            rym_url = ?
        WHERE album_id = ?
    ''', (data.get('rating'), data.get('ratings_count'), data.get('url'), album_id))
    conn.commit()
    conn.close()


def js_navigate(page, url):
    """用 JS 导航，绕过 CF"""
    page.evaluate(f'window.location.href = "{url}"')
    time.sleep(8)


def search_artist(page, artist_name):
    """搜索艺人页"""
    try:
        # 等待搜索框出现
        search_box = page.locator("#ui_search_input_main_search").first
        search_box.wait_for(timeout=10000)
        search_box.click(timeout=5000)
        time.sleep(0.3)
        search_box.fill("")
        time.sleep(0.2)
        search_box.type(artist_name, delay=40)
        time.sleep(0.3)
        search_box.press("Enter")
        time.sleep(10)
        
        # 截图保存搜索结果
        page.screenshot(path="rym_search.png")
        
        # 查找艺人链接（在搜索结果区域）
        html = page.content()
        
        # 搜索结果页的艺人链接格式：<a href="/artist/xxx" class="artist">艺人名</a>
        # 或者 <a href="/artist/xxx" ...>艺人名</a> 在 search_result 区域
        
        # 方法1：找 class="artist" 的链接
        artist_links = re.findall(r'<a[^>]*class="[^"]*artist[^"]*"[^>]*href="(/artist/[^"]+)"[^>]*>([^<]+)</a>', html)
        
        # 方法2：找搜索结果里的 /artist/ 链接
        if not artist_links:
            artist_links = re.findall(r'<a[^>]*href="(/artist/[^"]+)"[^>]*>([^<]+)</a>', html)
        
        # 去重（按链接）
        seen = set()
        unique_links = []
        for link, name in artist_links:
            if link not in seen:
                seen.add(link)
                unique_links.append((link, name))
        
        print(f'  Found {len(unique_links)} artist links')
        
        # 精确匹配
        for link, name in unique_links[:10]:  # 只看前10个
            name_clean = re.sub(r'\s*\([^)]+\)', '', name).strip().lower()
            if name_clean == artist_name.lower():
                print(f'  Exact match: {name} -> {link}')
                return link
        
        # 模糊匹配
        for link, name in unique_links[:10]:
            name_clean = re.sub(r'\s*\([^)]+\)', '', name).strip().lower()
            if artist_name.lower() in name_clean or name_clean in artist_name.lower():
                print(f'  Fuzzy match: {name} -> {link}')
                return link
        
        # 用第一个
        if unique_links:
            link, name = unique_links[0]
            print(f'  Using first: {name} -> {link}')
            return link
        
        return None
    except Exception as e:
        print(f'  Search error: {e}')
        return None


def find_album_on_artist_page(page, album_name):
    """在艺人页找专辑"""
    html = page.content()
    
    # 提取所有专辑链接（/release/album/...）
    album_links = re.findall(r'<a[^>]*href="(/release/album/[^"]+)"[^>]*>([^<]+)</a>', html)
    
    # 模糊匹配专辑名
    album_name_lower = album_name.lower().strip()
    for link, title in album_links:
        title_clean = re.sub(r'\s*\([^)]+\)', '', title).strip().lower()
        if album_name_lower in title_clean or title_clean in album_name_lower:
            print(f'  Found album: {title} -> {link}')
            return link
    
    # 没找到，返回第一个专辑链接
    if album_links:
        link, title = album_links[0]
        print(f'  Using first album: {title} -> {link}')
        return link
    
    return None


def extract_album_info(page, expected_artist):
    """从 HTML 提取专辑信息，验证艺人名"""
    html = page.content()
    info = {}
    
    # 专辑名
    m = re.search(r'<title>(.*?)\s+by\s+', html, re.DOTALL)
    info['title'] = m.group(1).strip() if m else "N/A"
    
    # 艺人名
    m = re.search(r'class="artist"[^>]*>(.*?)</(?:a|span)', html, re.DOTALL)
    if m:
        artist_clean = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        info['artist'] = artist_clean if artist_clean else "N/A"
    else:
        info['artist'] = "N/A"
    
    # 验证艺人名是否匹配
    if info['artist'] != "N/A":
        expected_lower = expected_artist.lower().strip()
        actual_lower = info['artist'].lower().strip()
        if expected_lower not in actual_lower and actual_lower not in expected_lower:
            print(f'  WARNING: Artist mismatch! Expected "{expected_artist}", got "{info["artist"]}"')
            info['mismatch'] = True
        else:
            info['mismatch'] = False
    
    # 评分 - 从 class="avg_rating"
    m = re.search(r'class="avg_rating"[^>]*>(.*?)</', html, re.DOTALL)
    if m:
        rating_text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        try:
            info['rating'] = float(rating_text)
        except:
            info['rating'] = None
    else:
        info['rating'] = None
    
    # 评价数 - 从 class="num_ratings"
    m = re.search(r'class="num_ratings"[^>]*>(.*?)</', html, re.DOTALL)
    if m:
        ratings_text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        m2 = re.search(r'([\d,]+)', ratings_text)
        info['ratings_count'] = int(m2.group(1).replace(',', '')) if m2 else 0
    else:
        info['ratings_count'] = 0
    
    # URL
    m = re.search(r'"url"\s*:\s*"(/release/[^"]+)"', html)
    info['url'] = BASE_URL + m.group(1) if m else None
    
    return info


def main():
    limit = 10
    if '--limit' in sys.argv:
        idx = sys.argv.index('--limit')
        limit = int(sys.argv[idx + 1])
    
    print(f'=== RYM Batch Fill v3 (limit={limit}) ===\n')
    
    albums = get_albums_to_fill(limit)
    print(f'Found {len(albums)} albums to fill\n')
    
    if not albums:
        print('No albums to fill.')
        return
    
    # 启动浏览器
    print('[0] Launching CloakBrowser...')
    browser = launch(headless=False)
    page = browser.new_page()
    
    # 首次访问首页（用 goto，之后用 location.href）
    print('  Visiting homepage (25s wait for CF)...')
    page.goto(BASE_URL, timeout=60000)
    time.sleep(25)
    print('  Ready.\n')
    
    success = 0
    failed = 0
    
    for i, (album_id, album_name, artist) in enumerate(albums, 1):
        print(f'[{i}/{len(albums)}] {album_name} - {artist} (id={album_id})')
        
        try:
            # Step 1: 搜索艺人
            print(f'  [1/3] Searching artist: {artist}')
            artist_link = search_artist(page, artist)
            
            if not artist_link:
                print('  -> SKIP (artist not found)')
                failed += 1
                continue
            
            # Step 2: 访问艺人页
            print(f'  [2/3] Visiting artist page...')
            js_navigate(page, BASE_URL + artist_link)
            
            # 在艺人页找专辑
            album_link = find_album_on_artist_page(page, album_name)
            
            if not album_link:
                print('  -> SKIP (album not found on artist page)')
                failed += 1
                continue
            
            # Step 3: 访问专辑页
            print(f'  [3/3] Visiting album page...')
            js_navigate(page, BASE_URL + album_link)
            time.sleep(3)  # 额外等待页面稳定
            
            # 提取信息
            info = extract_album_info(page, artist)
            
            if info.get('mismatch'):
                print(f'  -> SKIP (artist mismatch: {info["artist"]})')
                failed += 1
                continue
            
            if info.get('rating'):
                print(f'  -> Rating: {info["rating"]} / 5 ({info["ratings_count"]} ratings)')
                update_db(album_id, info)
                success += 1
            else:
                print('  -> SKIP (no rating found)')
                failed += 1
            
            # 返回首页（用 JS 导航）
            page.evaluate(f'window.location.href = "{BASE_URL}/"')
            time.sleep(8)  # 等待页面加载完成
            
        except Exception as e:
            print(f'  -> ERROR: {e}')
            failed += 1
        
        # 间隔
        if i < len(albums):
            print('  Waiting 3s...\n')
            time.sleep(3)
    
    print(f'\n=== Done: {success} success, {failed} failed ===')
    browser.close()


if __name__ == '__main__':
    main()
