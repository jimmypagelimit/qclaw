"""RYM test after cloakbrowser upgrade check"""
import sys, time
sys.stdout.reconfigure(encoding='utf-8')
from cloakbrowser import launch

browser = launch(headless=False)
page = browser.new_page()
try:
    print("[1/3] opening rym...")
    page.goto("https://rateyourmusic.com", timeout=90000,
              wait_until="domcontentloaded")
    
    print("[2/3] waiting 25s for CF...")
    time.sleep(25)
    
    page.screenshot(path="rym_debug2.png", full_page=True)
    
    title = page.evaluate("document.title")
    url = page.evaluate("window.location.href")
    html = page.content()
    
    has_search = 'id="ui_search_input_main_search"' in html
    turnstile = html.lower().count('turnstile')
    
    print(f"Title: {title}")
    print(f"URL: {url}")
    print(f"search box: {has_search}")
    print(f"page: {len(html)} chars | turnstile refs: {turnstile}")
    
finally:
    browser.close()
