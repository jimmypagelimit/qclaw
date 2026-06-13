import urllib.request, json, re, time, os

os.makedirs('rym_genre_test', exist_ok=True)

# Use JS location.href approach - first visit home to pass CF, then navigate to genre page
# We'll use urllib + headers that might work, or try a simpler approach
url = 'https://rateyourmusic.com/genre/rock/'

req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://rateyourmusic.com/',
})

try:
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    print(f'Response length: {len(html)}')
    print(f'Status: {resp.status}')
    
    # Save for inspection
    with open('rym_genre_test/rock_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # Extract page title
    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
    if title_match:
        print(f'Title: {title_match.group(1)}')
    
    # Check for CF challenge
    if 'cloudflare' in html.lower() or 'ray id' in html.lower() or len(html) < 50000:
        print('⚠️  Cloudflare challenge detected or short response')
        print(f'Page size: {len(html)} bytes')
    else:
        print('✅ Page loaded successfully')
        
    # Try to extract genre description area
    # Look for the main content area
    desc_patterns = [
        r'<meta name="description" content="(.*?)"',
        r'"description"\s*:\s*"([^"]+)"',
        r'<div class="article_body".*?>(.*?)</div>',
    ]
    for p in desc_patterns:
        m = re.search(p, html, re.IGNORECASE | re.DOTALL)
        if m:
            print(f'\nFound description ({p}): {m.group(1)[:200]}')
            break
    
except Exception as e:
    print(f'Error: {e}')