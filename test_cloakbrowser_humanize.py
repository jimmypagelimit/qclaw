# CloakBrowser - humanize模式 + 从首页导航到专辑
from cloakbrowser import launch
from cloakbrowser.human import patch_page, human_type, human_click
import sys, time

sys.stdout.reconfigure(encoding='utf-8')

print("启动 CloakBrowser...")
browser = launch(headless=False)
page = browser.new_page()

# 应用 humanize 补丁到 page 对象
patch_page(page)

# Step 1: 访问首页
print("Step 1: 访问 RYM 首页...")
page.goto("https://rateyourmusic.com/", timeout=90000)
time.sleep(15)

title = page.title()
print(f"标题: {title}")

if "Welcome" not in title and "Rate Your Music" not in title:
    print("等待更长时间...")
    time.sleep(15)
    title = page.title()
    print(f"等待后标题: {title}")

# Step 2: 用首页搜索框（模拟真人打字）
print("\nStep 2: 在搜索框中输入...")

search_box = page.locator("#searchbar")
if search_box.count() > 0:
    search_box.click()
    time.sleep(0.5)
    
    # 使用 human_type 模拟真人打字
    human_type(page, "#searchbar", "Boys of Dungeon Lane")
    time.sleep(0.3)
    
    # 用回车提交
    from cloakbrowser.human.keyboard import press_key
    press_key(page, "Enter")
    
    print("已提交搜索，等待结果...")
    time.sleep(10)
    
    stitle = page.title()
    surl = page.url
    print(f"搜索结果 - 标题: {stitle}, URL: {surl}")
    page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_humanize_search.png")
    
    if "Error" not in stitle:
        # 尝试找到并点击专辑链接
        print("\n尝试查找专辑链接...")
        
        links = page.locator("a[href*='release']")
        count = links.count()
        print(f"找到 {count} 个 release 链接")
        
        for i in range(min(count, 15)):
            try:
                link_text = links.nth(i).text_content()
                href = links.nth(i).get_attribute("href")
                if link_text and ("McCartney" in link_text or "Dungeon" in link_text or "boys" in link_text.lower()):
                    print(f"找到匹配: {link_text.strip()[:60]} -> {href}")
                    human_click(page, f"a[href*='release']:nth-of-type({i+1})")
                    time.sleep(10)
                    
                    atitle = page.title()
                    aurl = page.url
                    print(f"专辑页 - 标题: {atitle}, URL: {aurl}")
                    page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_album_final.png", full_page=True)
                    
                    html = page.content()
                    with open("C:/Users/qujt/.qclaw/workspace/rym_album_final.html", "w", encoding="utf-8") as f:
                        f.write(html)
                    
                    # 提取数据
                    print("\n--- 专辑数据 ---")
                    import re
                    # RYM评分格式
                    ratings = re.findall(r'(\d+\.\d{2})\s*of\s*5', html)
                    if ratings:
                        print(f"评分: {ratings[0]} / 5")
                    # 评价数量
                    rc = re.findall(r'([\d,]+)\s*Ratings?', html)
                    if rc:
                        print(f"评价数: {rc[0]}")
                    break
            except Exception as e:
                continue
        
        if i >= min(count, 15) - 1:
            print("未找到匹配的专辑链接，保存全部HTML")
            html = page.content()
            with open("C:/Users/qujt/.qclaw/workspace/rym_search_result.html", "w", encoding="utf-8") as f:
                f.write(html)
    else:
        print("搜索返回错误，可能是RYM临时故障")
else:
    print("未找到搜索框，截图诊断")
    page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_no_searchbox.png")

browser.close()
print("\n[OK] 完成")
