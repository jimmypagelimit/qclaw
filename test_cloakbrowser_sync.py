# CloakBrowser 同步方式测试
from cloakbrowser import launch
import sys

# 修复控制台编码
sys.stdout.reconfigure(encoding='utf-8')

print("启动 CloakBrowser（同步模式）...")
try:
    browser = launch(headless=False)
    page = browser.new_page()
    
    print("访问 RYM...")
    page.goto("https://rateyourmusic.com/release/album/paul-mccartney/the-boys-of-dungeon-lane/", timeout=60000, wait_until="networkidle")
    
    title = page.title()
    print(f"[OK] 页面标题: {title}")
    
    page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_test.png", full_page=True)
    print("[OK] 截图已保存到 rym_test.png")
    
    html = page.content()
    with open("C:/Users/qujt/.qclaw/workspace/rym_test.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] HTML已保存到 rym_test.html")
    
    # 提取关键信息
    print("\n--- 提取专辑信息 ---")
    
    # 尝试提取评分
    try:
        rating = page.locator(".page-release-rating-value").first.text_content()
        print(f"RYM 评分: {rating.strip()}")
    except:
        print("RYM 评分: 未找到")
    
    # 尝试提取流派
    try:
        genres = page.locator(".release_genres a").all_text_contents()
        print(f"流派: {', '.join(genres)}")
    except:
        print("流派: 未找到")
    
    browser.close()
    print("\n[OK] 测试完成")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
