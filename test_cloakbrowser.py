# CloakBrowser 测试脚本 - 访问 RYM 的 Paul McCartney 专辑页面
import asyncio
from cloakbrowser import launch_async

async def main():
    # 启动 CloakBrowser（自动下载定制版 Chromium）
    browser = await launch_async(headless=False)
    
    page = await browser.new_page()
    
    print("正在访问 RYM...")
    await page.goto("https://rateyourmusic.com/release/album/paul-mccartney/the-boys-of-dungeon-lane/")
    
    # 等待页面加载
    await page.wait_for_load_state("networkidle")
    
    # 截图
    await page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_test.png")
    print("截图已保存到 rym_test.png")
    
    # 获取页面标题
    title = await page.title()
    print(f"页面标题: {title}")
    
    # 获取页面内容
    content = await page.content()
    with open("C:/Users/qujt/.qclaw/workspace/rym_test.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("HTML 已保存到 rym_test.html")
    
    await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
