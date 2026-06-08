#!/usr/bin/env python3
"""
RYM (Rate Your Music) 专辑/艺人信息抓取工具
使用 CloakBrowser 绕过 Cloudflare 防护

成功路径记录：
1. 必须用 launch(headless=False) - 无头模式会被检测
2. 首页必须等待 20 秒让 CF challenge 完成
3. 进入专辑页必须用 JS click() - 不能用 page.goto() 直接跳转
4. 搜索框选择器: #ui_search_input_main_search
"""

import time
import json
import re
from cloakbrowser import launch

def search_album(page, album_name, artist_name):
    """在 RYM 搜索专辑并返回第一个匹配结果的链接"""
    print(f"[1/5] 搜索专辑: {artist_name} - {album_name}")
    
    # 在搜索框输入
    search_box = page.locator("#ui_search_input_main_search")
    search_box.click()
    time.sleep(1)
    search_box.fill("")  # 清空
    time.sleep(0.5)
    
    # 输入搜索词 (专辑名 + 艺人名)
    query = f"{album_name} {artist_name}"
    search_box.type(query, delay=60)
    time.sleep(1)
    search_box.press("Enter")
    
    # 等待搜索结果
    print("  -> 等待搜索结果 (12秒)...")
    time.sleep(12)
    
    # 截图保存搜索结果页
    page.screenshot(path="rym_search_results.png", full_page=True)
    print("  -> 搜索结果截图: rym_search_results.png")
    
    return page.content()

def click_album_link(page, album_name):
    """通过 JS click() 进入专辑页（关键步骤）"""
    print(f"[2/5] 点击进入专辑页: {album_name}")
    
    # 转义 JS 字符串中的单引号
    safe_name = album_name.replace("'", "\\'")
    
    js_code = f"""
    () => {{
        const links = document.querySelectorAll('a[href*="/release/"]');
        let found = false;
        for (const link of links) {{
            if (link.textContent.toLowerCase().includes('{safe_name.lower()}')) {{
                link.click();
                found = true;
                return link.href;
            }}
        }}
        // 如果没找到精确匹配，点第一个
        if (links.length > 0) {{
            links[0].click();
            return links[0].href;
        }}
        return null;
    }}
    """
    
    result = page.evaluate(js_code)
    
    # 等待专辑页加载
    print("  -> 等待专辑页加载 (15秒)...")
    time.sleep(15)
    
    # 截图
    page.screenshot(path="rym_album_page.png", full_page=True)
    print("  -> 专辑页截图: rym_album_page.png")
    
    return page.content()

def extract_album_info(html):
    """从专辑页 HTML 提取信息"""
    print("[3/5] 提取专辑信息...")
    
    info = {
        "title": "",
        "artist": "",
        "rating": "",
        "num_ratings": "",
        "num_reviews": "",
        "genres": [],
        "styles": [],
        "year": "",
        "country": "",
        "format": "",
        "label": "",
        "duration": "",
        "tracklist": []
    }
    
    # 专辑名
    m = re.search(r'<h1[^>]*class="[^"]*album_title[^"]*"[^>]*>\s*<span[^>]*>([^<]+)</span>', html, re.DOTALL)
    if not m:
        m = re.search(r'<h1[^>]*>\s*<span[^>]*>([^<]+)</span>', html, re.DOTALL)
    if m:
        info["title"] = m.group(1).strip()
    
    # 艺人名
    m = re.search(r'class="[^"]*artist[^"]*"[^>]*>\s*<a[^>]*>([^<]+)</a>', html, re.DOTALL)
    if not m:
        m = re.search(r'<h2[^>]*>\s*<a[^>]*>([^<]+)</a>', html, re.DOTALL)
    if m:
        info["artist"] = m.group(1).strip()
    
    # 评分
    m = re.search(r'class="avg_rating"[^>]*>([\d.]+)', html)
    if not m:
        m = re.search(r'"avgRating":\s*([\d.]+)', html)
    if m:
        info["rating"] = m.group(1)
    
    # 评价数
    m = re.search(r'([\d,]+)\s*Ratings?', html)
    if m:
        info["num_ratings"] = m.group(1)
    
    # 评论数
    m = re.search(r'([\d,]+)\s*Reviews?', html)
    if m:
        info["num_reviews"] = m.group(1)
    
    # 年份
    m = re.search(r'(\d{4})\s*</a>\s*\)', html)
    if not m:
        m = re.search(r'year[^<]*?</td>\s*<td[^>]*>(\d{4})', html, re.DOTALL | re.IGNORECASE)
    if m:
        info["year"] = m.group(1)
    
    # 流派 (genres)
    genres = re.findall(r'<a href="/genre/[^"]+"[^>]*>([^<]+)</a>', html)
    if genres:
        # 去重
        seen = set()
        unique_genres = []
        for g in genres:
            if g not in seen:
                seen.add(g)
                unique_genres.append(g)
        info["genres"] = unique_genres[:10]
    
    # 风格 (styles)
    styles = re.findall(r'<a href="/style/[^"]+"[^>]*>([^<]+)</a>', html)
    if styles:
        seen = set()
        unique_styles = []
        for s in styles:
            if s not in seen:
                seen.add(s)
                unique_styles.append(s)
        info["styles"] = unique_styles[:10]
    
    # 厂牌
    labels = re.findall(r'label.*?<a[^>]*href="[^"]+"[^>]*>([^<]+)</a>', html, re.DOTALL | re.IGNORECASE)
    if labels:
        info["label"] = labels[0].strip()
    
    # 发行格式
    for fmt in ['CD', 'Vinyl', 'Digital', 'Cassette', 'LP', 'Album']:
        if fmt in html:
            info["format"] = fmt
            break
    
    print(f"  -> 专辑: {info['title']}")
    print(f"  -> 艺人: {info['artist']}")
    print(f"  -> 评分: {info['rating']} / 5")
    print(f"  -> 评价数: {info['num_ratings']}")
    if info['genres']:
        print(f"  -> 流派: {', '.join(info['genres'][:5])}")
    if info['styles']:
        print(f"  -> 风格: {', '.join(info['styles'][:5])}")
    
    return info

def extract_artist_info(page, artist_name):
    """访问艺人页面提取信息"""
    print(f"\n[4/5] 访问艺人页面: {artist_name}")
    
    # 在搜索框搜索艺人
    search_box = page.locator("#ui_search_input_main_search")
    search_box.click()
    time.sleep(1)
    search_box.fill("")
    time.sleep(0.5)
    search_box.type(artist_name, delay=60)
    search_box.press("Enter")
    
    print("  -> 等待搜索结果 (12秒)...")
    time.sleep(12)
    
    # 点击第一个艺人链接
    js_code = """
    () => {
        const links = document.querySelectorAll('a[href*="/artist/"]');
        if (links.length > 0) {
            links[0].click();
            return true;
        }
        return false;
    }
    """
    page.evaluate(js_code)
    
    print("  -> 等待艺人页加载 (15秒)...")
    time.sleep(15)
    
    # 截图
    page.screenshot(path="rym_artist_page.png", full_page=True)
    print("  -> 艺人页截图: rym_artist_page.png")
    
    # 提取艺人信息
    html = page.content()
    artist_info = {
        "name": artist_name,
        "top_albums": [],
        "genres": [],
        "rating": ""
    }
    
    # 提取艺人热门专辑
    albums = re.findall(r'<a href="/release/[^"]+"[^>]*>([^<]+)</a>', html)
    if albums:
        seen = set()
        unique_albums = []
        for a in albums[:20]:  # 只看前20个链接
            if a not in seen and len(a) > 3:
                seen.add(a)
                unique_albums.append(a)
        artist_info["top_albums"] = unique_albums[:10]
    
    print(f"  -> 艺人: {artist_info['name']}")
    if artist_info['top_albums']:
        print(f"  -> 热门专辑: {', '.join(artist_info['top_albums'][:5])}")
    
    return artist_info

def main():
    # 测试用专辑
    test_albums = [
        ("Twin Fantasy", "Car Seat Headrest"),
        ("Disintegration", "The Cure"),
    ]
    
    print("=== RYM 抓取工具 (CloakBrowser) ===\n")
    print("启动浏览器 (headless=False)...")
    browser = launch(headless=False)
    page = browser.new_page()
    
    # 访问首页过 CF
    print("\n[0/5] 访问首页 (等待 CF challenge 20秒)...")
    page.goto("https://rateyourmusic.com/", timeout=90000)
    time.sleep(20)
    print("  -> CF challenge 完成")
    
    results = []
    
    for album_name, artist_name in test_albums:
        print(f"\n{'='*60}")
        print(f"处理: {artist_name} - {album_name}")
        print('='*60)
        
        # 1. 搜索专辑
        html = search_album(page, album_name, artist_name)
        
        # 2. 点击进入专辑页
        html = click_album_link(page, album_name)
        
        # 3. 提取专辑信息
        album_info = extract_album_info(html)
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
    output_file = "rym_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 完成 ===")
    print(f"结果已保存: {output_file}")
    print(f"截图文件:")
    print(f"  - rym_search_results.png")
    print(f"  - rym_album_page.png")
    print(f"  - rym_artist_page.png")
    
    # 保持浏览器打开
    print("\n浏览器保持打开，按 Ctrl+C 退出...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        browser.close()

if __name__ == "__main__":
    main()
