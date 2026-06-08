# CloakBrowser - 通过搜索找到专辑
from cloakbrowser import launch
import sys, time

sys.stdout.reconfigure(encoding='utf-8')

print("启动 CloakBrowser...")
browser = launch(headless=False)
page = browser.new_page()

# Step 1: 访问首页（过验证）
print("Step 1: 访问 RYM 首页...")
page.goto("https://rateyourmusic.com/", timeout=60000)
time.sleep(10)

title = page.title()
print(f"首页标题: {title}")

# Step 2: 通过搜索找专辑
print("\nStep 2: 搜索 Paul McCartney - The Boys of Dungeon Lane...")
search_input = page.locator("#searchbar")
if search_input.count() > 0:
    search_input.fill("The Boys of Dungeon Lane Paul McCartney")
    search_input.press("Enter")
    print("已提交搜索，等待结果...")
    time.sleep(8)
    
    search_title = page.title()
    print(f"搜索页标题: {search_title}")
    page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_search.png")
    
    # 尝试点击专辑链接
    album_link = page.locator("a[href*='paul-mccartney']").first
    if album_link.count() > 0:
        print("\nStep 3: 点击专辑链接...")
        album_link.click()
        time.sleep(8)
        
        album_title = page.title()
        print(f"专辑页面标题: {album_title}")
        page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_album.png", full_page=True)
        
        html = page.content()
        with open("C:/Users/qujt/.qclaw/workspace/rym_album.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        # 提取评分信息
        print("\n--- 提取专辑数据 ---")
        try:
            rating = page.locator(".avg_rating").first.text_content()
            print(f"平均评分: {rating.strip()}")
        except Exception as e:
            print(f"评分提取失败: {e}")
        
        try:
            ratings_count = page.locator(".num_ratings").first.text_content()
            print(f"评价人数: {ratings_count.strip()}")
        except:
            pass
        
        try:
            genres = page.locator(".release_genres a").all_text_contents()
            if genres:
                print(f"流派: {', '.join([g.strip() for g in genres])}")
        except:
            pass
            
        try:
            year = page.locator(".release_year a").first.text_content()
            print(f"年份: {year.strip()}")
        except:
            pass
    else:
        print("未找到专辑链接，保存搜索结果HTML")
        html = page.content()
        with open("C:/Users/qujt/.qclaw/workspace/rym_search.html", "w", encoding="utf-8") as f:
            f.write(html)
else:
    print("未找到搜索框")

browser.close()
print("\n[OK] 完成")
