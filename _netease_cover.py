#!/usr/bin/env python3
"""
网易云专辑封面抓取脚本
用法: python _netease_cover.py "专辑名" "艺人名" [album_id]
依赖: playwright (pip install playwright && playwright install chromium)
"""
import sys, json, os, urllib.request
from playwright.sync_api import sync_playwright

def search_album(album_name, artist):
    """用网易云网页搜索专辑，返回封面URL"""
    query = f"{artist} {album_name}"
    url = f"https://music.163.com/#/search/m/?s={urllib.parse.quote(query)}&type=1"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=15000)
        page.wait_for_timeout(3000)
        
        # 切到搜索结果的 iframe
        frame = page.frame_locator("#g_iframe")
        # 点"专辑"tab
        frame.get_by_text("专辑").first.click()
        page.wait_for_timeout(2000)
        
        # 找匹配专辑
        items = frame.locator(".srchsongst .item").all()
        for item in items:
            title = item.locator(".tit").inner_text()
            artist_name = item.locator(".s-fc7").inner_text()
            if album_name.lower() in title.lower():
                # 获取封面
                img = item.locator("img").get_attribute("src")
                if img:
                    img = img.replace("http://", "https://").replace("=150y150", "=600y600")
                    browser.close()
                    return img
        browser.close()
    return None

def download_cover(img_url, save_path):
    req = urllib.request.Request(img_url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://music.163.com'
    })
    with open(save_path, 'wb') as f:
        f.write(urllib.request.urlopen(req, timeout=10).read())
    return os.path.getsize(save_path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python _netease_cover.py '专辑名' '艺人名' [album_id]")
        sys.exit(1)
    
    album_name = sys.argv[1]
    artist = sys.argv[2]
    album_id = sys.argv[3] if len(sys.argv) > 3 else "unknown"
    
    print(f"搜索: {artist} - {album_name}")
    img_url = search_album(album_name, artist)
    
    if not img_url:
        print("未找到封面")
        sys.exit(1)
    
    print(f"封面URL: {img_url}")
    
    save_path = f"C:/Users/qujt/.qclaw/workspace/tasks/2026-05-12-long-term-project/album-tracker/public/covers/{album_id}-{artist}-{album_name}.jpg"
    size = download_cover(img_url, save_path)
    print(f"下载完成: {save_path} ({size} bytes)")
