# CloakBrowser 测试 - 先访问首页过验证
from cloakbrowser import launch
import sys, time

sys.stdout.reconfigure(encoding='utf-8')

print("启动 CloakBrowser...")
try:
    browser = launch(headless=False)
    page = browser.new_page()
    
    # Step 1: 访问 RYM 首页
    print("Step 1: 访问 RYM 首页...")
    page.goto("https://rateyourmusic.com/", timeout=60000)
    
    # 等待更长时间让 Cloudflare 验证完成
    print("等待 Cloudflare 验证（15秒）...")
    time.sleep(15)
    
    title = page.title()
    print(f"首页标题: {title}")
    
    page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_home.png")
    print("首页截图已保存")
    
    # 检查是否通过验证
    if "Just a moment" in title or "rateyourmusic.com" == title.strip():
        print("[WARN] 可能还在验证页面或被拦截")
        # 再等一会
        time.sleep(10)
        title = page.title()
        print(f"等待后标题: {title}")
        page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_home2.png")
    
    # Step 2: 如果首页成功，访问专辑页面
    if "Rate Your Music" in title or "RYM" in title:
        print("\nStep 2: 访问专辑页面...")
        page.goto("https://rateyourmusic.com/release/album/paul-mccartney/the-boys-of-dungeon-lane/", timeout=60000)
        time.sleep(10)
        
        album_title = page.title()
        print(f"专辑页面标题: {album_title}")
        page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_album.png", full_page=True)
        
        html = page.content()
        with open("C:/Users/qujt/.qclaw/workspace/rym_album.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("专辑页面HTML已保存")
    else:
        print(f"\n首页未通过验证，当前URL: {page.url}")
        html = page.content()
        with open("C:/Users/qujt/.qclaw/workspace/rym_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("调试HTML已保存")
    
    browser.close()
    print("\n[OK] 完成")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
