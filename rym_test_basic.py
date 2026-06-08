#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RYM 抓取测试 - 最简版本
测试: Car Seat Headrest - Twin Fantasy (2018)
"""

import time
import json
import re
from cloakbrowser import launch

def main():
    print("=== RYM 抓取测试 ===\n")
    
    # 1. 启动浏览器
    print("[1/6] 启动 CloakBrowser (headless=False)...")
    browser = launch(headless=False)
    page = browser.new_page()
    
    # 2. 访问首页过 CF
    print("\n[2/6] 访问首页 (等待 CF challenge 20秒)...")
    page.goto("https://rateyourmusic.com/", timeout=90000)
    time.sleep(20)
    print("  -> CF challenge 完成")
    
    # 3. 搜索专辑
    print("\n[3/6] 搜索: Twin Fantasy Car Seat Headrest")
    search_box = page.locator("#ui_search_input_main_search")
    search_box.click()
    time.sleep(1)
    search_box.fill("")
    time.sleep(0.5)
    search_box.type("Twin Fantasy Car Seat Headrest", delay=60)
    time.sleep(1)
    search_box.press("Enter")
    
    print("  -> 等待搜索结果 (12秒)...")
    time.sleep(12)
    page.screenshot(path="rym_test_search.png", full_page=True)
    print("  -> 截图: rym_test_search.png")
    
    # 4. 点击第一个专辑链接
    print("\n[4/6] 点击第一个专辑链接...")
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
    
    # 5. 提取专辑信息
    print("\n[5/6] 提取专辑信息...")
    html = page.content()
    
    # 保存 HTML 用于调试
    with open("rym_album.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("  -> HTML 已保存: rym_album.html")
    
    info = {}
    
    # 专辑名
    m = re.search(r'<h1[^>]*>.*?<span[^>]*>([^<]+)</span>', html, re.DOTALL)
    if m:
        info["title"] = m.group(1).strip()
    else:
        info["title"] = "N/A"
    
    # 艺人名
    m = re.search(r'class="artist"[^>]*>.*?<a[^>]*>([^<]+)</a>', html, re.DOTALL)
    if m:
        info["artist"] = m.group(1).strip()
    else:
        info["artist"] = "N/A"
    
    # 评分
    m = re.search(r'class="avg_rating"[^>]*>([\d.]+)', html)
    if m:
        info["rating"] = m.group(1)
    else:
        info["rating"] = "N/A"
    
    # 评价数
    m = re.search(r'([\d,]+)\s*Ratings?', html)
    if m:
        info["num_ratings"] = m.group(1)
    else:
        info["num_ratings"] = "N/A"
    
    # 评论数
    m = re.search(r'([\d,]+)\s*Reviews?', html)
    if m:
        info["num_reviews"] = m.group(1)
    else:
        info["num_reviews"] = "N/A"
    
    # 流派
    genres = re.findall(r'<a href="/genre/[^"]+">([^<]+)</a>', html)
    if genres:
        seen = set()
        unique = []
        for g in genres:
            if g not in seen:
                seen.add(g)
                unique.append(g)
        info["genres"] = unique[:8]
    else:
        info["genres"] = []
    
    # 风格
    styles = re.findall(r'<a href="/style/[^"]+">([^<]+)</a>', html)
    if styles:
        seen = set()
        unique = []
        for s in styles:
            if s not in seen:
                seen.add(s)
                unique.append(s)
        info["styles"] = unique[:8]
    else:
        info["styles"] = []
    
    print(f"  专辑: {info.get('title', 'N/A')}")
    print(f"  艺人: {info.get('artist', 'N/A')}")
    print(f"  评分: {info.get('rating', 'N/A')} / 5")
    print(f"  评价数: {info.get('num_ratings', 'N/A')}")
    if info.get("genres"):
        print(f"  流派: {', '.join(info['genres'][:5])}")
    if info.get("styles"):
        print(f"  风格: {', '.join(info['styles'][:5])}")
    
    # 6. 保存结果
    print("\n[6/6] 保存结果...")
    output = {
        "test_album": "Twin Fantasy - Car Seat Headrest",
        "info": info,
        "screenshots": [
            "rym_test_search.png",
            "rym_test_album.png"
        ]
    }
    
    with open("rym_test_result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("  -> 结果已保存: rym_test_result.json")
    
    print("\n=== 测试完成 ===")
    print("关闭浏览器...")
    browser.close()
    print("完成！")

if __name__ == "__main__":
    main()
