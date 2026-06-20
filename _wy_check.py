import asyncio
from playwright.async_api import async_playwright

async def check_album(page, artist, album):
    search_term = f"{artist} {album}"
    await page.goto(f"https://music.163.com/#/search/m/?s={search_term}&type=1", wait_until="networkidle")
    await page.wait_for_timeout(3000)
    # 切到搜索 iframe
    try:
        frame = page.frame_locator("iframe#contentFrame")
        # 看有没有专辑结果
        albums = frame.locator(".srchsongst .item")
        count = await albums.count()
        print(f"[网页] {artist} - {album}: {count} 条结果")
        for i in range(min(count, 3)):
            text = await albums.nth(i).inner_text()
            print(f"  #{i+1}: {text[:80]}")
    except Exception as e:
        print(f"[网页] {artist} - {album}: 错误 {e}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # 先打开网易云首页，建立 session
        await page.goto("https://music.163.com", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        checks = [
            ("苍蝇", "The Fly II"),
            ("缺省", "共同的土地"),
            ("嘎调", "嘎调"),
            ("声无哀乐", "声无哀乐"),
            ("jody积融", "Is It Gonna Happen Again"),
            ("东京酒吐座", "Remains"),
        ]
        for artist, album in checks:
            await check_album(page, artist, album)
        await browser.close()

asyncio.run(main())
