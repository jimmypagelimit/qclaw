# CloakBrowser 直接下载二进制文件
import asyncio
import sys

async def download_and_test():
    from cloakbrowser import download, launch_async
    
    print("步骤1: 下载 CloakBrowser 定制版 Chromium...")
    try:
        await download(verbose=True)
        print("✓ 下载完成")
    except Exception as e:
        print(f"下载失败: {e}")
        return
    
    print("\n步骤2: 启动浏览器测试 RYM...")
    try:
        browser = await launch_async(headless=False)
        page = await browser.new_page()
        
        print("访问 RYM...")
        await page.goto("https://rateyourmusic.com/release/album/paul-mccartney/the-boys-of-dungeon-lane/")
        await page.wait_for_load_state("networkidle")
        
        title = await page.title()
        print(f"页面标题: {title}")
        
        await page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_test.png")
        print("✓ 截图已保存")
        
        await browser.close()
        print("✓ 测试完成")
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(download_and_test())
