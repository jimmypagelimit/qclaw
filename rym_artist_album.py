#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RYM 艺人页面专辑抓取 - 先进 Artist 页面再找专辑
用法: python rym_artist_album.py "艺人名" "专辑名"
"""

import sys
import time
import json
import re
from cloakbrowser import launch


def main():
    if len(sys.argv) < 3:
        print("用法: python rym_artist_album.py '艺人名' '专辑名'")
        sys.exit(1)
    
    artist_name = sys.argv[1]
    album_name = sys.argv[2]
    
    print(f"=== RYM 艺人页专辑抓取 ===")
    print(f"目标: {artist_name} - {album_name}\n")
    
    # 启动浏览器
    print("[0/5] 启动 CloakBrowser...")
    browser = launch(headless=False)
    page = browser.new_page()
    
    # 访问首页过 CF
    print("\n[0.5/5] 过 CF challenge (20秒)...")
    page.goto("https://rateyourmusic.com/", timeout=90000)
    time.sleep(20)
    print("  -> CF 完成")
    
    # 搜索艺人
    print(f"\n[1/5] 搜索艺人: {artist_name}")
    search_box = page.locator("#ui_search_input_main_search").first
    search_box.click()
    time.sleep(0.3)
    search_box.fill("")
    search_box.type(artist_name, delay=60)
    search_box.press("Enter")
    print("  -> 等待搜索结果 (12秒)...")
    time.sleep(12)
    
    # 点击 Artist 链接（不是 Release）
    print(f"\n[2/5] 点击艺人: {artist_name}")
    js = """() => {
        // 优先找 Artists 区域的链接
        const artistLinks = document.querySelectorAll('a[href*="/artist/"]');
        for (const link of artistLinks) {
            if (link.textContent.trim().includes('__ARTIST__')) {
                return 'artist:' + link.href;
            }
        }
        // fallback: 找第一个 artist 链接
        if (artistLinks.length > 0) return 'artist:' + artistLinks[0].href;
        return null;
    }""".replace("__ARTIST__", artist_name)
    
    result = page.evaluate(js)
    if not result or not result.startswith("artist:"):
        page.screenshot(path="rym_artist_search.png", full_page=True)
        print(f"  -> 未找到艺人链接，截图保存为 rym_artist_search.png")
        browser.close()
        sys.exit(1)
    
    artist_url = result.split(":", 1)[1]
    print(f"  -> 艺人URL: {artist_url}")
    
    # 用 JS click 进入艺人页面
    js_click = f"""() => {{
        const links = document.querySelectorAll('a[href*="/artist/"]');
        for (const link of links) {{
            if (link.href === '{artist_url}') {{ link.click(); return true; }}
        }}
        return false;
    }}"""
    page.evaluate(js_click)
    print("  -> 等待艺人页加载 (15秒)...")
    time.sleep(15)
    page.screenshot(path="rym_artist_page.png", full_page=True)
    print("  -> 截图: rym_artist_page.png")
    
    # 在艺人页面找专辑
    print(f"\n[3/5] 查找专辑: {album_name}")
    html = page.content()
    
    # 找所有 release 链接及其文本
    releases = re.findall(r'<a[^>]+href="(/release/[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    target_link = None
    for href, text in releases:
        clean_text = re.sub(r'<[^>]+>', '', text).strip()
        if clean_text.lower() == album_name.lower():
            target_link = href
            print(f"  -> 找到专辑: {clean_text} ({href})")
            break
    
    if not target_link:
        # 尝试模糊匹配
        for href, text in releases:
            clean_text = re.sub(r'<[^>]+>', '', text).strip()
            if album_name.lower() in clean_text.lower() or clean_text.lower() in album_name.lower():
                target_link = href
                print(f"  -> 模糊匹配: {clean_text} ({href})")
                break
    
    if not target_link:
        print(f"  -> ❌ 在艺人页面未找到专辑 '{album_name}'")
        print(f"  -> 可用专辑:")
        seen = set()
        for href, text in releases:
            clean_text = re.sub(r'<[^>]+>', '', text).strip()
            if clean_text and clean_text not in seen:
                seen.add(clean_text)
                print(f"     - {clean_text}")
        page.screenshot(path="rym_artist_releases.png", full_page=True)
        browser.close()
        sys.exit(1)
    
    # 点击进入专辑页
    print(f"\n[4/5] 进入专辑页...")
    full_url = "https://rateyourmusic.com" + target_link
    js_nav = f"""() => {{
        const link = document.querySelector('a[href="{target_link}"]');
        if (link) {{ link.click(); return true; }}
        return false;
    }}"""
    page.evaluate(js_nav)
    print("  -> 等待专辑页加载 (15秒)...")
    time.sleep(15)
    page.screenshot(path="rym_album.png", full_page=True)
    
    # 提取信息
    print(f"\n[5/5] 提取专辑信息...")
    html = page.content()
    info = {}
    
    m = re.search(r'<title>(.*?)\s+by\s+', html, re.DOTALL)
    info['title'] = m.group(1).strip() if m else "N/A"
    
    m = re.search(r'class="artist"[^>]*>(.*?)</(?:a|span)', html, re.DOTALL)
    if m:
        info['artist'] = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    else:
        info['artist'] = "N/A"
    
    m = re.search(r'class="avg_rating"[^>]*>(.*?)</', html, re.DOTALL)
    info['rating'] = re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else "N/A"
    
    m = re.search(r'class="num_ratings"[^>]*>(.*?)</', html, re.DOTALL)
    if m:
        m2 = re.search(r'([\d,]+)', re.sub(r'<[^>]+>', '', m.group(1)))
        info['num_ratings'] = m2.group(1) if m2 else "N/A"
    else:
        info['num_ratings'] = "N/A"
    
    genres = list(dict.fromkeys(g.replace("-", " ").rstrip("/") for g in re.findall(r'href="/genre/([^"]+)"', html)))[:8]
    styles = list(dict.fromkeys(s.replace("-", " ").rstrip("/") for s in re.findall(r'href="/style/([^"]+)"', html)))[:8]
    info['genres'] = genres
    info['styles'] = styles
    
    print(f"  -> 专辑: {info.get('title')}")
    print(f"  -> 艺人: {info.get('artist')}")
    print(f"  -> 评分: {info.get('rating')} / 5")
    print(f"  -> 评价数: {info.get('num_ratings')}")
    if genres: print(f"  -> 流派: {', '.join(genres[:5])}")
    if styles: print(f"  -> 风格: {', '.join(styles[:5])}")
    
    # 保存
    output_file = f"rym_{artist_name.replace(' ', '_')}_{album_name.replace(' ', '_')}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 完成 ===")
    print(f"结果: {output_file}")
    print(f"截图: rym_artist_search.png, rym_artist_page.png, rym_album.png")
    
    browser.close()


if __name__ == "__main__":
    main()
