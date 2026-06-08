# CloakBrowser - 增强版：更长的等待时间 + 重试
from cloakbrowser import launch
import sys, time

sys.stdout.reconfigure(encoding='utf-8')

print("启动 CloakBrowser...")
browser = launch(headless=False)
page = browser.new_page()

# Step 1: 访问首页（过验证）- 给足时间
print("Step 1: 访问 RYM 首页...")
page.goto("https://rateyourmusic.com/", timeout=90000, wait_until="domcontentloaded")

print("等待页面完全加载（20秒）...")
time.sleep(20)

title = page.title()
url = page.url
print(f"标题: {title}")
print(f"URL: {url}")

page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_home_v2.png")

if "Rate Your Music" not in title and "Welcome" not in title:
    print("[WARN] 首页可能未加载完成，再等15秒...")
    time.sleep(15)
    title = page.title()
    url = page.url
    print(f"等待后 - 标题: {title}, URL: {url}")
    page.screenshot(path="C:/Users/qujt\.qclaw\workspace/rym_home_v3.png")

# Step 2: 尝试搜索
print("\nStep 2: 尝试多种方式定位搜索框...")

# 方法1: ID选择器
selectors = [
    "#searchbar",
    "input[name='searchterm']",
    "input[type='text']",
    ".search_input",
    "#search",
]

search_found = False
for sel in selectors:
    try:
        elem = page.locator(sel).first
        if elem.count() > 0 and elem.is_visible():
            print(f"找到搜索框: {sel}")
            search_found = True
            elem.fill("The Boys of Dungeon Lane")
            elem.press("Enter")
            break
    except:
        continue

if not search_found:
    # 方法2: 用 JavaScript 搜索
    print("尝试通过URL直接搜索...")
    page.goto("https://rateyourmusic.com/search?searchtype=all&searchterm=The+Boys+of+Dungeon+Lane", timeout=60000, wait_until="domcontentloaded")
    time.sleep(10)

search_title = page.title()
search_url = page.url
print(f"搜索结果 - 标题: {search_title}, URL: {search_url}")
page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_search.png")

# 保存HTML用于分析
html = page.content()
with open("C:/Users/qujt/.qclaw/workspace/rym_latest.html", "w", encoding="utf-8") as f:
    f.write(html)
print("HTML已保存到 rym_latest.html")

browser.close()
print("\n[OK] 完成")
