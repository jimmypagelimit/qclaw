# CloakBrowser - 搜索成功后点击链接（而非直接URL跳转）
from cloakbrowser import launch
import sys, time, re

sys.stdout.reconfigure(encoding='utf-8')

print("启动 CloakBrowser...")
browser = launch(headless=False)
page = browser.new_page()

# Step 1: 首页
print("Step 1: 访问 RYM 首页...")
page.goto("https://rateyourmusic.com/", timeout=90000)
time.sleep(20)

title = page.title()
print(f"标题: {title}")

# Step 2: 搜索
print("\nStep 2: 搜索...")
search_box = page.locator("#ui_search_input_main_search")
search_box.click()
time.sleep(0.3)
search_box.type("Boys of Dungeon Lane", delay=60)
time.sleep(0.3)
search_box.press("Enter")

print("等待搜索结果...")
time.sleep(12)

stitle = page.title()
surl = page.url
print(f"搜索 - 标题: {stitle}, URL: {surl}")
page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_search_ok.png")

# Step 3: 点击第一个专辑链接（关键：用 click 而非 goto）
print("\nStep 3: 点击专辑链接...")

# 方法: 用 JavaScript 获取链接并点击
click_result = page.evaluate("""() => {
    // 查找所有包含 "Boys of Dungeon Lane" 的 release 链接
    const links = document.querySelectorAll('a[href*="/release/"]');
    for (const link of links) {
        const text = link.textContent.trim();
        if (text.includes('Boys of Dungeon Lane') || text.includes('Dungeon Lane')) {
            // 模拟真实点击
            link.click();
            return {
                clicked: true,
                text: text.substring(0, 80),
                href: link.getAttribute('href')
            };
        }
    }
    return { clicked: false };
}""")

print(f"点击结果: {click_result}")

if click_result.get('clicked'):
    print("等待专辑页加载...")
    time.sleep(15)  # 给足时间过 Cloudflare
    
    atitle = page.title()
    aurl = page.url
    print(f"专辑页 - 标题: {atitle}")
    print(f"URL: {aurl}")
    
    # 截图
    page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_album_click.png", full_page=True)
    
    html = page.content()
    with open("C:/Users/qujt/.qclaw/workspace/rym_album_click.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("\n=== Paul McCartney - The Boys of Dungeon Lane ===")
    
    # 提取 RYM 数据
    # 平均评分
    avg_match = re.search(r'([\d.]+)\s*/\s*5', html)
    if avg_match:
        print(f"⭐ RYM 评分: {avg_match.group(1)} / 5")
    
    # 评价数
    ratings_matches = re.findall(r'([\d,]+)\s*(?:Ratings?|ratings?)', html)
    if ratings_matches:
        print(f"📊 评价数: {ratings_matches[0]}")
    
    # 流派
    genre_matches = re.findall(r'<a[^>]*href="/genre/[^"]*"[^>]*>([^<]+)</a>', html)
    if genre_matches:
        genres = [g.strip() for g in genre_matches[:6]]
        print(f"🎸 流派: {', '.join(genres)}")
    
    # 风格
    style_matches = re.findall(r'<a[^>]*href="/style/[^"]*"[^>]*>([^<]+)</a>', html)
    if style_matches:
        styles = [s.strip() for s in style_matches[:6]]
        print(f"🎵 风格: {', '.join(styles)}")
    
    # 年份
    year_match = re.search(r'(\d{4})\s*</a>\s*</span>\s*</div>', html)
    if not year_match:
        year_match = re.search(r'release_year[^>]*><a[^>]*>(\d{4})</a>', html)
    if year_match:
        print(f"📅 年份: {year_match.group(1)}")
    
    # 发行公司
    label_matches = re.findall(r'label[^>]*><a[^>]*>([^<]+)</a>', html, re.IGNORECASE)
    if label_matches:
        print(f"🏷️ 厂牌: {label_matches[0].strip()}")
else:
    print("未找到可点击的专辑链接")
    # 保存搜索结果HTML用于调试
    html = page.content()
    with open("C:/Users/qujt/.qclaw/workspace/rym_search_debug.html", "w", encoding="utf-8") as f:
        f.write(html)

browser.close()
print("\n[OK] 完成")
