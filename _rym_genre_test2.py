import subprocess, json, re, time, os

os.makedirs('rym_genre_test', exist_ok=True)

script = '''
import sys
sys.path.insert(0, r'C:\\Users\\qujt\\.qclaw\\workspace')
from cloakbrowser import CloakBrowser

url = 'https://rateyourmusic.com/genre/rock/'

with CloakBrowser(headless=False, timeout=60) as browser:
    # Step 1: visit home to pass CF
    print("Visiting home...")
    browser.visit('https://rateyourmusic.com/')
    time.sleep(25)
    
    # Step 2: navigate to genre page via JS
    print("Navigating to rock genre page via JS...")
    browser.page.evaluate('window.location.href = "/genre/rock/"')
    time.sleep(20)
    
    # Step 3: extract page content
    html = browser.page.content()
    print(f"Page length: {len(html)} bytes")
    
    # Save for inspection
    with open('rym_genre_test/rock_genre_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # Check for CF
    if 'cloudflare' in html.lower() or len(html) < 73000:
        print("⚠️ CF challenge detected")
    else:
        print("✅ Page loaded")
    
    # Extract title
    title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
    if title:
        print(f"Title: {title.group(1)}")
    
    # Extract genre description - look for article body or main text
    # RYM genre pages typically have a description in the page
    desc_patterns = [
        r'<div class="article_body"[^>]*>(.*?)</div>',
        r'<div class="genre_description"[^>]*>(.*?)</div>',
        r'"description"\\s*:\\s*"([^"]+)"',
        r'<meta name="description" content="([^"]+)"',
    ]
    
    for p in desc_patterns:
        m = re.search(p, html, re.IGNORECASE | re.DOTALL)
        if m:
            text = re.sub(r'<[^>]+>', '', m.group(1))
            text = re.sub(r'\\s+', ' ', text).strip()
            if len(text) > 50:
                print(f"\\nDescription ({p}): {text[:500]}")
                break
'''

with open('rym_genre_test/_test_genre.py', 'w', encoding='utf-8') as f:
    f.write(script)

result = subprocess.run(
    ['C:\\Python311\\python.exe', 'rym_genre_test/_test_genre.py'],
    capture_output=True, text=True, timeout=120
)
print(result.stdout)
if result.stderr:
    print('STDERR:', result.stderr[:500])