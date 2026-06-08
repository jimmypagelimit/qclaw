#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RYM 抓取实战 v5 - 用正确的正则模式
测试: Car Seat Headrest - Twin Fantasy (2018)
"""

import time
import json
import re
from cloakbrowser import launch


def search_and_enter(page, query):
    """搜索并回车"""
    print(f"  搜索: {query}")
    search_box = page.locator("#ui_search_input_main_search")
    search_box.click()
    time.sleep(1)
    search_box.fill("")
    time.sleep(0.5)
    search_box.type(query, delay=60)
    time.sleep(1)
    search_box.press("Enter")
    time.sleep(12)
    page.screenshot(path="rym_search.png", full_page=True)
    print("  -> 截图: rym_search.png")


def click_first_album(page):
    """点击第一个专辑链接"""
    print("  点击第一个专辑链接...")
    js = (
        "() => {" +
        "  const links = document.querySelectorAll('a[href*=\"/release/\"]');" +
        "  if (links.length > 0) {" +
        "    links[0].click();" +
        "    return true;" +
        "  }" +
        "  return false;" +
        "}"
    )
    page.evaluate(js)
    time.sleep(15)
    page.screenshot(path="rym_album.png", full_page=True)
    print("  -> 截图: rym_album.png")


def extract_album_info(page):
    """用正则表达式从 HTML 提取专辑信息"""
    print("  提取专辑信息...")
    html = page.content()
    
    info = {
        "title": "",
        "artist": "",
        "rating": "",
        "num_ratings": "",
        "num_reviews": "",
        "genres": [],
        "styles": []
    }
    
    # 专辑名 - 从 title 标签
    m = re.search(r"<title>(.*?)\s+by\s+", html, re.DOTALL)
    if m:
        info["title"] = m.group(1).strip()
    
    # 艺人名 - 从 class="artist"
    m = re.search(r"class=\"artist\"[^>]*>(.*?)</", html, re.DOTALL)
    if m:
        artist_html = m.group(1)
        m2 = re.search(r">([^<]+)<", artist_html)
        if m2:
            info["artist"] = m2.group(1).strip()
    
    # 评分 - 从 class="avg_rating"
    m = re.search(r"class=\"avg_rating\"[^>]*>(.*?)</", html, re.DOTALL)
    if m:
        rating_text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        info["rating"] = rating_text
    
    # 评价数 - 从 class="num_ratings"
    m = re.search(r"class=\"num_ratings\"[^>]*>(.*?)</", html, re.DOTALL)
    if m:
        ratings_text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        m2 = re.search(r"([\d,]+)", ratings_text)
        if m2:
            info["num_ratings"] = m2.group(1)
    
    # 评论数
    m = re.search(r"([\d,]+)\s*Reviews?", html)
    if m:
        info["num_reviews"] = m.group(1)
    
    # 流派 - 从 href="/genre/..."
    genres = re.findall(r"href=\"/genre/([^\"]+)\"", html)
    if genres:
        seen = set()
        unique = []
        for g in genres:
            if g not in seen:
                seen.add(g)
                unique.append(g.replace("-", " "))
        info["genres"] = unique[:8]
    
    # 风格 - 从 href="/style/..."
    styles = re.findall(r"href=\"/style/([^\"]+)\"", html)
    if styles:
        seen = set()
        unique = []
        for s in styles:
            if s not in seen:
                seen.add(s)
                unique.append(s.replace("-", " "))
        info["styles"] = unique[:8]
    
    # 打印结果
    print(f"  -> 专辑: {info['title']}")
    print(f"  -> 艺人: {info['artist']}")
    print(f"  -> 评分: {info['rating']} / 5")
    print(f"  -> 评价数: {info['num_ratings']}")
    print(f"  -> 评论数: {info['num_reviews']}")
    if info["genres"]:
        print(f"  -> 流派: {', '.join(info['genres'])}")
    if info["styles"]:
        print(f"  -> 风格: {', '.join(info['styles'])}")
    
    return info


def main():
    test_albums = [
        ("Twin Fantasy", "Car Seat Headrest"),
        ("Disintegration", "The Cure"),
    ]
    
    print("=== RYM 抓取实战 v5 ===\n")
    print("[0/5] 启动浏览器 (headless=False)...")
    browser = launch(headless=False)
    page = browser.new_page()
    
    print("\n[1/5] 访问首页 (等待 CF challenge 20秒)...")
    page.goto("https://rateyourmusic.com/", timeout=90000)
    time.sleep(20)
    print("  -> CF challenge 完成")
    
    results = []
    
    for i, (album_name, artist_name) in enumerate(test_albums):
        print(f"\n{'='*60}")
        print(f"[{i+2}/5] 处理: {artist_name} - {album_name}")
        print("="*60)
        
        # 搜索
        query = f"{album_name} {artist_name}"
        search_and_enter(page, query)
        
        # 点击专辑
        click_first_album(page)
        
        # 提取信息
        info = extract_album_info(page)
        info["album_name"] = album_name
        info["artist_name"] = artist_name
        results.append(info)
        
        # 回到首页
        page.goto("https://rateyourmusic.com/", timeout=90000)
        time.sleep(20)
    
    # 保存结果
    output_file = "rym_result_v5.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 完成 ===")
    print(f"结果已保存: {output_file}")
    print(f"截图文件:")
    print(f"  - rym_search.png")
    print(f"  - rym_album.png")
    
    print("\n[5/5] 关闭浏览器...")
    browser.close()
    print("完成！")


if __name__ == "__main__":
    main()
