#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RYM 抓取测试 v4 - 用 page.evaluate() 获取动态内容
测试: Car Seat Headrest - Twin Fantasy (2018)
"""

import time
import json
from cloakbrowser import launch


def search_album(page, album_name, artist_name):
    """在 RYM 搜索专辑"""
    print(f"[1/6] 搜索专辑: {artist_name} - {album_name}")
    
    query = f"{album_name} {artist_name}"
    search_box = page.locator("#ui_search_input_main_search")
    search_box.click()
    time.sleep(1)
    search_box.fill("")
    time.sleep(0.5)
    search_box.type(query, delay=60)
    time.sleep(1)
    search_box.press("Enter")
    
    print("  -> 等待搜索结果 (12秒)...")
    time.sleep(12)
    page.screenshot(path="rym_test_search.png", full_page=True)
    print("  -> 截图: rym_test_search.png")


def click_album_link(page, album_name):
    """通过 JS click() 进入专辑页"""
    print(f"[2/6] 点击进入专辑页: {album_name}")
    
    safe_name = album_name.replace("'", "\\'")
    js_click = (
        "() => {" +
        "  const links = document.querySelectorAll('a[href*=\"/release/\"]');" +
        "  if (links.length > 0) {" +
        "    links[0].click();" +
        "    return links[0].href;" +
        "  }" +
        "  return null;" +
        "}"
    )
    page.evaluate(js_click)
    
    print("  -> 等待专辑页加载 (15秒)...")
    time.sleep(15)
    page.screenshot(path="rym_test_album.png", full_page=True)
    print("  -> 截图: rym_test_album.png")


def extract_album_info(page):
    """用 JavaScript 提取专辑信息（处理动态内容）"""
    print("[3/6] 用 page.evaluate() 提取专辑信息...")
    
    js_code = (
        "() => {" +
        "  const info = {};" +
        # 专辑名
        "  const titleEl = document.querySelector('h1.album_title span');" +
        "  info.title = titleEl ? titleEl.textContent.trim() : '';" +
        # 艺人名
        "  const artistEl = document.querySelector('.artist a');" +
        "  info.artist = artistEl ? artistEl.textContent.trim() : '';" +
        # 评分
        "  const ratingEl = document.querySelector('.avg_rating');" +
        "  info.rating = ratingEl ? ratingEl.textContent.trim() : '';" +
        # 评价数
        "  const ratingsEl = document.querySelector('.num_ratings');" +
        "  if (ratingsEl) {" +
        "    const match = ratingsEl.textContent.match(/([\\d,]+)/);" +
        "    info.num_ratings = match ? match[1] : '';" +
        "  } else { info.num_ratings = ''; }" +
        # 评论数
        "  const reviewsEl = document.querySelector('.num_reviews');" +
        "  if (reviewsEl) {" +
        "    const match = reviewsEl.textContent.match(/([\\d,]+)/);" +
        "    info.num_reviews = match ? match[1] : '';" +
        "  } else { info.num_reviews = ''; }" +
        # 流派
        "  const genreLinks = document.querySelectorAll('a[href*=\"/genre/\"]');" +
        "  info.genres = Array.from(genreLinks).map(a => a.textContent.trim()).filter((v,i,a) => a.indexOf(v) === i);" +
        # 风格
        "  const styleLinks = document.querySelectorAll('a[href*=\"/style/\"]');" +
        "  info.styles = Array.from(styleLinks).map(a => a.textContent.trim()).filter((v,i,a) => a.indexOf(v) === i);" +
        # 年份
        "  const yearEl = document.querySelector('.album_info td:nth-child(2)');" +
        "  info.year = yearEl ? yearEl.textContent.trim() : '';" +
        # 厂牌
        "  const labelEl = document.querySelector('.album_info td:nth-child(4) a');" +
        "  info.label = labelEl ? labelEl.textContent.trim() : '';" +
        "  return info;" +
        "}"
    )
    
    info = page.evaluate(js_code)
    
    print(f"  -> 专辑: {info.get('title', 'N/A')}")
    print(f"  -> 艺人: {info.get('artist', 'N/A')}")
    print(f"  -> 评分: {info.get('rating', 'N/A')} / 5")
    print(f"  -> 评价数: {info.get('num_ratings', 'N/A')}")
    if info.get('genres'):
        print(f"  -> 流派: {', '.join(info['genres'][:5])}")
    if info.get('styles'):
        print(f"  -> 风格: {', '.join(info['styles'][:5])}")
    
    return info


def extract_artist_info(page, artist_name):
    """访问艺人页面提取信息"""
    print(f"\n[4/6] 访问艺人页面: {artist_name}")
    
    search_box = page.locator("#ui_search_input_main_search")
    search_box.click()
    time.sleep(1)
    search_box.fill("")
    time.sleep(0.5)
    search_box.type(artist_name, delay=60)
    search_box.press("Enter")
    
    print("  -> 等待搜索结果 (12秒)...")
    time.sleep(12)
    
    js_click = (
        "() => {" +
        "  const links = document.querySelectorAll('a[href*=\"/artist/\"]');" +
        "  if (links.length > 0) {" +
        "    links[0].click();" +
        "    return true;" +
        "  }" +
        "  return false;" +
        "}"
    )
    page.evaluate(js_click)
    
    print("  -> 等待艺人页加载 (15秒)...")
    time.sleep(15)
    page.screenshot(path="rym_artist_page.png", full_page=True)
    print("  -> 截图: rym_artist_page.png")
    
    # 提取艺人信息
    js_artist = (
        "() => {" +
        "  const info = { name: '' };" +
        "  const nameEl = document.querySelector('h1.artist_name');" +
        "  info.name = nameEl ? nameEl.textContent.trim() : '';" +
        # 热门专辑
        "  const albumLinks = document.querySelectorAll('.discography_table a[href*=\"/release/\"]');" +
        "  info.top_albums = Array.from(albumLinks).map(a => a.textContent.trim()).filter((v,i,a) => a.indexOf(v) === i).slice(0, 10);" +
        "  return info;" +
        "}"
    )
    
    artist_info = page.evaluate(js_artist)
    print(f"  -> 艺人: {artist_info.get('name', artist_name)}")
    if artist_info.get('top_albums'):
        print(f"  -> 热门专辑: {', '.join(artist_info['top_albums'][:5])}")
    
    return artist_info


def main():
    test_albums = [
        ("Twin Fantasy", "Car Seat Headrest"),
        ("Disintegration", "The Cure"),
    ]
    
    print("=== RYM 抓取测试 v4 (page.evaluate) ===\n")
    print("启动浏览器 (headless=False)...")
    browser = launch(headless=False)
    page = browser.new_page()
    
    print("\n[0/6] 访问首页 (等待 CF challenge 20秒)...")
    page.goto("https://rateyourmusic.com/", timeout=90000)
    time.sleep(20)
    print("  -> CF challenge 完成")
    
    results = []
    
    for album_name, artist_name in test_albums:
        print(f"\n{'='*60}")
        print(f"处理: {artist_name} - {album_name}")
        print('='*60)
        
        # 1. 搜索专辑
        search_album(page, album_name, artist_name)
        
        # 2. 点击进入专辑页
        click_album_link(page, album_name)
        
        # 3. 提取专辑信息（用 page.evaluate）
        album_info = extract_album_info(page)
        album_info["album_name"] = album_name
        album_info["artist_name"] = artist_name
        
        # 4. 访问艺人页面
        artist_info = extract_artist_info(page, artist_name)
        
        # 合并结果
        result = {
            "album": album_info,
            "artist": artist_info
        }
        results.append(result)
        
        # 回到首页准备下一个
        page.goto("https://rateyourmusic.com/", timeout=90000)
        time.sleep(20)
    
    # 保存结果
    output_file = "rym_test_result_v4.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 完成 ===")
    print(f"结果已保存: {output_file}")
    print(f"截图文件:")
    print(f"  - rym_test_search.png")
    print(f"  - rym_test_album.png")
    print(f"  - rym_artist_page.png")
    
    print("\n关闭浏览器...")
    browser.close()
    print("完成！")


if __name__ == "__main__":
    main()
