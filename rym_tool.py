#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RYM 通用抓取工具 v8 (修复艺人名 + 清理 genre slug)
用法: python rym_tool.py "专辑名" "艺人名"
"""

import sys
import time
import json
import re
from cloakbrowser import launch


def search_album(page, query):
    """搜索专辑 - 直接用成功的选择器"""
    print(f"[1/4] 搜索: {query}")
    
    # 直接用成功的选择器
    search_box = page.locator("#ui_search_input_main_search").first
    
    search_box.click()
    time.sleep(0.5)
    search_box.fill("")
    time.sleep(0.3)
    search_box.type(query, delay=60)
    time.sleep(0.5)
    search_box.press("Enter")
    
    print("  -> 等待搜索结果 (12秒)...")
    time.sleep(12)
    page.screenshot(path="rym_search.png", full_page=True)
    print("  -> 截图: rym_search.png")
    return True


def click_first_album(page):
    """点击第一个专辑链接 - 用 JS click"""
    print("[2/4] 点击第一个专辑链接...")
    
    js = """() => {
        const links = document.querySelectorAll('a[href*="/release/"]');
        if (links.length > 0) {
            links[0].click();
            return true;
        }
        return false;
    }"""
    
    page.evaluate(js)
    
    print("  -> 等待专辑页加载 (15秒)...")
    time.sleep(15)
    page.screenshot(path="rym_album.png", full_page=True)
    print("  -> 截图: rym_album.png")
    return True


def extract_album_info(page):
    """从 HTML 提取专辑信息 - 修复版"""
    print("[3/4] 提取专辑信息...")
    
    html = page.content()
    info = {}
    
    # 专辑名 - 从 title 标签
    m = re.search(r'<title>(.*?)\s+by\s+', html, re.DOTALL)
    if m:
        info['title'] = m.group(1).strip()
    else:
        info['title'] = "N/A"
    
    # 艺人名 - 从 class="artist" (修复正则)
    m = re.search(r'class="artist"[^>]*>(.*?)</(?:a|span)', html, re.DOTALL)
    if m:
        artist_html = m.group(1)
        # 去掉 HTML 标签
        artist_clean = re.sub(r'<[^>]+>', '', artist_html).strip()
        if artist_clean:
            info['artist'] = artist_clean
        else:
            info['artist'] = "N/A"
    else:
        info['artist'] = "N/A"
    
    # 评分 - 从 class="avg_rating"
    m = re.search(r'class="avg_rating"[^>]*>(.*?)</', html, re.DOTALL)
    if m:
        rating_text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        info['rating'] = rating_text
    else:
        info['rating'] = "N/A"
    
    # 评价数 - 从 class="num_ratings"
    m = re.search(r'class="num_ratings"[^>]*>(.*?)</', html, re.DOTALL)
    if m:
        ratings_text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        m2 = re.search(r'([\d,]+)', ratings_text)
        if m2:
            info['num_ratings'] = m2.group(1)
        else:
            info['num_ratings'] = "N/A"
    else:
        info['num_ratings'] = "N/A"
    
    # 评论数
    m = re.search(r'([\d,]+)\s*Reviews?', html)
    if m:
        info['num_reviews'] = m.group(1)
    else:
        info['num_reviews'] = "N/A"
    
    # 流派 - 从 href="/genre/..." (清理 trailing /)
    genres = re.findall(r'href="/genre/([^"]+)"', html)
    if genres:
        seen = set()
        unique = []
        for g in genres:
            g = g.replace("-", " ").rstrip("/")  # 清理 trailing /
            if g not in seen:
                seen.add(g)
                unique.append(g)
        info['genres'] = unique[:8]
    else:
        info['genres'] = []
    
    # 风格 - 从 href="/style/..." (清理 trailing /)
    styles = re.findall(r'href="/style/([^"]+)"', html)
    if styles:
        seen = set()
        unique = []
        for s in styles:
            s = s.replace("-", " ").rstrip("/")  # 清理 trailing /
            if s not in seen:
                seen.add(s)
                unique.append(s)
        info['styles'] = unique[:8]
    else:
        info['styles'] = []
    
    # 打印结果
    print(f"  -> 专辑: {info.get('title', 'N/A')}")
    print(f"  -> 艺人: {info.get('artist', 'N/A')}")
    print(f"  -> 评分: {info.get('rating', 'N/A')} / 5")
    print(f"  -> 评价数: {info.get('num_ratings', 'N/A')}")
    if info.get('genres'):
        print(f"  -> 流派: {', '.join(info['genres'][:5])}")
    if info.get('styles'):
        print(f"  -> 风格: {', '.join(info['styles'][:5])}")
    
    return info


def main():
    if len(sys.argv) < 3:
        print("用法: python rym_tool.py '专辑名' '艺人名'")
        print("示例: python rym_tool.py 'Twin Fantasy' 'Car Seat Headrest'")
        sys.exit(1)
    
    album_name = sys.argv[1]
    artist_name = sys.argv[2]
    query = f"{album_name} {artist_name}"
    
    print("=== RYM 通用抓取工具 v8 ===\n")
    print(f"目标: {artist_name} - {album_name}\n")
    
    # 启动浏览器
    print("[0/4] 启动 CloakBrowser (headless=False)...")
    browser = launch(headless=False)
    page = browser.new_page()
    
    # 访问首页
    print("\n[0.5/4] 访问首页 (等待 CF challenge 20秒)...")
    page.goto("https://rateyourmusic.com/", timeout=90000)
    time.sleep(20)
    print("  -> CF challenge 完成")
    
    # 搜索
    if not search_album(page, query):
        print("[失败] 搜索失败")
        browser.close()
        sys.exit(1)
    
    # 点击专辑
    if not click_first_album(page):
        print("[失败] 点击专辑失败")
        browser.close()
        sys.exit(1)
    
    # 提取信息
    info = extract_album_info(page)
    info['album_name'] = album_name
    info['artist_name'] = artist_name
    
    # 保存结果
    output_file = f"rym_{artist_name.replace(' ', '_')}_{album_name.replace(' ', '_')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 完成 ===")
    print(f"结果已保存: {output_file}")
    print(f"截图: rym_search.png, rym_album.png")
    
    print("\n[4/4] 关闭浏览器...")
    browser.close()
    print("完成！")


if __name__ == "__main__":
    main()
