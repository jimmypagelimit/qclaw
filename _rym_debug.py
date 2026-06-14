"""Quick RYM accessibility test via CloakBrowser"""
import sys, time
sys.stdout.reconfigure(encoding='utf-8')
from cloakbrowser import launch

browser = launch(headless=False)
page = browser.new_page()
try:
    print("[1/3] opening rym homepage...")
    page.goto("https://rateyourmusic.com", timeout=90000,
              wait_until="domcontentloaded")
    
    print("[2/3] waiting 20s...")
    time.sleep(20)
    
    # Take screenshot
    page.screenshot(path="rym_debug.png")
    
    title = page.evaluate("document.title")
    html = page.content()
    
    has_search = 'id="ui_search_input_main_search"' in html
    turnstile = html.lower().count('turnstile')
    jam = html.lower().count('just a moment')
    
    print(f"Title: {title}")
    print(f"search box: {has_search}")
    print(f"page: {len(html)} chars")
    print(f"turnstile: {turnstile}, just_a_moment: {jam}")
    print(f"'rateyourmusic': {html.lower().count('rateyourmusic')}")
    
    # What page are we on?
    url = page.evaluate("window.location.href")
    print(f"URL: {url}")
    
finally:
    browser.close()
