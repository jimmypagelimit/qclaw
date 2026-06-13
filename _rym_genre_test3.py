import subprocess, json, re, time, os

os.makedirs('rym_genre_test', exist_ok=True)

script = '''
import sys
sys.path.insert(0, r'C:\\Users\\qujt\\.qclaw\\workspace')
from cloakbrowser import launch

url = 'https://rateyourmusic.com/genre/rock/'

with launch(headless=False, timeout=60) as browser:
    # Step 1: visit home to pass CF
    print("Visiting home...")
    page = browser.new_page()
    page.goto('https://rateyourmusic.com/')
    time.sleep(25)
    
    # Step 2: navigate to genre page via JS
    print("Navigating to rock genre page via JS...")
    page.evaluate('window.location.href = "/genre/rock/"')
    time.sleep(20)
    
    # Step 3: extract page content
    html = page.content()
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
    
    # Try to find genre description - RYM has this info in the page
    # Look for meta description first
    meta_desc = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', html, re.IGNORECASE)
    if meta_desc:
        print(f"\\nMeta description: {meta_desc.group(1)}")
    
    # Look for article body text
    article = re.search(r'<div class="article_body"[^>]*>(.*?)</div>', html, re.IGNORECASE | re.DOTALL)
    if article:
        text = re.sub(r'<[^>]+>', '', article.group(1))
        text = re.sub(r'\\s+', ' ', text).strip()
        if len(text) > 50:
            print(f"\\nArticle body: {text[:500]}")
        else:
            print("Article body too short or empty")
    else:
        print("No article_body found")
    
    # Check page size category
    if len(html) < 73000:
        print("⚠️ CF challenge page (too short)")
    else:
        print("✅ Full page loaded")
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