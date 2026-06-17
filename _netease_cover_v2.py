#!/usr/bin/env python3
"""
网易云专辑封面抓取 - 通过 opencli CD (Chrome)
用法: python _netease_cover_v2.py "专辑名" "艺人名" [album_id]
"""
import sys, json, os, re, urllib.request, urllib.parse, time
from playwright.sync_api import sync_playwright

def search_netease(album_name, artist):
    with sync_playwright() as p:
        # 连接已有 Chrome (opencli 已启动)
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0] if browser.contexts[0].pages else browser.contexts[0].new_page()
        
        query = f"{artist} {album_name}"
        url = f"https://music.163.com/search/m/?s={urllib.parse.quote(query)}&type=1"
        page.goto(url, timeout=15000)
        time.sleep(3)
        
        # 等待 iframe 加载
        page.wait_for_selector("#g_iframe", timeout=10000)
        frame = page.frame_locator("#g_iframe")
        
        # 点"专辑"标签
        try:
            frame.get_by_role("link", name="专辑").click()
            time.sleep(2)
        except:
            pass
        
        # 获取第一条专辑结果
        try:
            first_item = frame.locator(".m-cvrlst .f-cb").first
            img_src = first_item.locator("img").get_attribute("src")
            title = first_item.locator(".tit a").get_attribute("title")
            print(f"找到: {title}")
            print(f"封面: {img_src}")
            
            if img_src:
                # 转高清图
                img_src = img_src.replace("http://", "https://")
                img_src = re.sub(r'=\d+y\d+', '=600y600', img_src)
                browser.close()
                return img_src
        except Exception as e:
            print(f"提取失败: {e}")
        
        browser.close()
    return None

def download_cover(img_url, save_path):
    req = urllib.request.Request(img_url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://music.163.com'
    })
    with open(save_path, 'wb') as f:
        f.write(urllib.request.urlopen(req, timeout=15).read())
    return os.path.getsize(save_path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python _netease_cover_v2.py '专辑名' '艺人名' [album_id]")
        sys.exit(1)
    
    album_name = sys.argv[1]
    artist = sys.argv[2]
    album_id = sys.argv[3] if len(sys.argv) > 3 else "unknown"
    
    img_url = search_netease(album_name, artist)
    if not img_url:
        print("未找到封面")
        sys.exit(1)
    
    # 安全文件名
    safe_name = re.sub(r'[\\/*?:"<>|]', '', f"{album_id}-{artist}-{album_name}")
    save_path = f"C:/Users/qujt/.qclaw/workspace/tasks/2026-05-12-long-term-project/album-tracker/public/covers/{safe_name}.jpg"
    
    size = download_cover(img_url, save_path)
    print(f"下载完成: {save_path} ({size} bytes)")
