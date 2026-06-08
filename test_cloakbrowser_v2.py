# CloakBrowser 测试 - 直接启动
import asyncio

async def test():
    from cloakbrowser import launch_async
    
    print("启动 CloakBrowser...")
    try:
        # launch_async 会自动下载二进制文件（如果未下载）
        browser = await launch_async(
            headless=False,  # 有头模式，方便观察
            verbose=True     # 显示详细信息
        )
        
        page = await browser.new_page()
        
        print("访问 RYM...")
        await page.goto("https://rateyourmusic.com/release/album/paul-mccartney/the-boys-of-dungeon-lane/", timeout=60000)
        await page.wait_for_load_state("networkidle", timeout=30000)
        
        title = await page.title()
        print(f"✓ 页面标题: {title}")
        
        await page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_test.png", full_page=True)
        print("✓ 截图已保存到 rym_test.png")
        
        # 保存HTML
        html = await page.content()
        with open("C:/Users/qujt/.qclaw/workspace/rym_test.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("✓ HTML已保存到 rym_test.html")
        
        await browser.close()
        print("✓ 测试完成")
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
