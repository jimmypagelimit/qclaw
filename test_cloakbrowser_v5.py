# CloakBrowser - 简化版：直接用搜索框 + type
from cloakbrowser import launch
import sys, time

sys.stdout.reconfigure(encoding='utf-8')

print("启动 CloakBrowser...")
browser = launch(headless=False)
page = browser.new_page()

# Step 1: 访问首页
print("Step 1: 访问 RYM 首页...")
page.goto("https://rateyourmusic.com/", timeout=90000)
time.sleep(18)

title = page.title()
url = page.url
print(f"标题: {title}")
print(f"URL: {url}")

if "Welcome" not in title and "Rate Your Music" not in title:
    print("等待更长时间...")
    time.sleep(15)
    title = page.title()
    print(f"等待后标题: {title}")

page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_home_final.png")

# Step 2: 搜索框输入
print("\nStep 2: 搜索...")

search_box = page.locator("#searchbar")
if search_box.count() > 0:
    print("找到搜索框，输入关键词...")
    search_box.click()
    time.sleep(0.3)
    
    # 逐字符模拟真人输入
    search_box.type("Boys of Dungeon Lane", delay=80)
    time.sleep(0.5)
    search_box.press("Enter")
    
    print("等待搜索结果...")
    time.sleep(12)
    
    stitle = page.title()
    surl = page.url
    print(f"搜索 - 标题: {stitle}, URL: {surl}")
    page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_search_result.png")
    
    html = page.content()
    with open("C:/Users/qujt/.qclaw/workspace/rym_search_result.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    # 分析HTML找专辑链接
    import re
    
    # 找所有 release 链接及其文本
    release_links = re.findall(r'<a[^>]*href="(/release/[^"]+)"[^>]*>([^<]+)</a>', html, re.IGNORECASE)
    print(f"\n找到 {len(release_links)} 个 release 链接:")
    for href, text in release_links[:20]:
        clean_text = re.sub(r'\s+', ' ', text).strip()
        if clean_text:
            print(f"  {clean_text[:50]} -> {href[:60]}")
    
    # 找 McCartney 相关的
    mccartney_links = [(h, t) for h, t in release_links if 'mccartney' in h.lower() or 'McCartney' in t or 'dungeon' in h.lower()]
    if mccartney_links:
        href, text = mccartney_links[0]
        print(f"\n点击匹配: {text.strip()[:50]}")
        full_url = f"https://rateyourmusic.com{href}"
        
        try:
            page.goto(full_url, timeout=60000)
            time.sleep(10)
            
            atitle = page.title()
            aurl = page.url
            print(f"专辑页 - 标题: {atitle}, URL: {aurl}")
            page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_album_final.png", full_page=True)
            
            ahtml = page.content()
            with open("C:/Users/qujt/.qclaw/workspace/rym_album_final.html", "w", encoding="utf-8") as f:
                f.write(ahtml)
            
            # 提取评分数据
            print("\n--- 专辑数据 ---")
            
            # RYM 平均评分
            avg_match = re.search(r'avg_rating[^>]*>\s*([\d.]+)', ahtml)
            if avg_match:
                print(f"平均评分: {avg_match.group(1)} / 5")
            
            # 评价数量
            ratings_match = re.search(r'([\d,]+)\s*(?:Ratings?|ratings?)', ahtml)
            if ratings_match:
                print(f"评价数: {ratings_match.group(1)}")
            
            # 流派
            genres = re.findall(r'class="genre"[^>]*><a[^>]*>([^<]+)</a>', ahtml)
            if genres:
                print(f"流派: {', '.join(genres)}")
            
        except Exception as e:
            print(f"访问专辑页失败: {e}")
    else:
        print("\n未找到 McCartney/Dungeon Lane 相关链接")
else:
    print("未找到搜索框")

browser.close()
print("\n[OK] 完成")
