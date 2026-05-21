#!/usr/bin/env python3
"""用 Playwright 从 Genius 抓歌词"""
import asyncio, re, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def fetch_genius():
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://genius.com/Car-seat-headrest-plane-vs-tank-vs-submarine-lyrics"
        print(f"打开: {url}")
        
        try:
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(3)
            
            # 截图
            await page.screenshot(path="C:/Users/15206/.qclaw/workspace/genius_page.png")
            print("截图已保存")
            
            # 提取歌词 - Genius 的歌词在 data-lyrics-container 属性的 div 里
            lyrics_elem = await page.query_selector('[data-lyrics-container="true"]')
            if lyrics_elem:
                lyrics = await lyrics_elem.inner_text()
                print(f"✅ 歌词获取成功 ({len(lyrics)} 字符)")
                print(f"\n预览:\n{lyrics[:500]}...")
                
                # 保存
                with open("C:/Users/15206/.qclaw/workspace/lyrics/Plane vs Tank vs Submarine_raw.txt", "w", encoding="utf-8") as f:
                    f.write(lyrics)
                print("\n✅ 已保存原始歌词")
                return lyrics
            else:
                # 尝试其他选择器
                print("尝试其他选择器...")
                content = await page.content()
                # 保存完整 HTML 调试用
                with open("C:/Users/15206/.qclaw/workspace/genius_page.html", "w", encoding="utf-8") as f:
                    f.write(content)
                print("HTML 已保存")
                
        except Exception as e:
            print(f"❌ 失败: {e}")
        finally:
            await browser.close()

asyncio.run(fetch_genius())
