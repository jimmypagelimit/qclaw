import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.google.com", timeout=15000)
        await page.screenshot(path="google_screenshot.png", full_page=False)
        print("Screenshot saved: google_screenshot.png")
        await browser.close()

asyncio.run(main())
