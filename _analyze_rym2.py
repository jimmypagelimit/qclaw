import re

f = open('rym_genre_test/rock_genre_page.html', 'r', encoding='utf-8')
c = f.read()

# Extract the full article text - it's in a div with class containing "article"
# Find the main genre description article
article = re.search(r'<div class="article_body"[^>]*>(.*?)</div>', c, re.IGNORECASE | re.DOTALL)
if article:
    text = re.sub(r'<[^>]+>', '', article.group(1))
    text = re.sub(r'\s+', ' ', text).strip()
    print(f"Article ({len(text)} chars):\n")
    print(text)
else:
    # Try broader approach
    text = re.sub(r'<[^>]+>', '', c)
    text = re.sub(r'\s+', ' ', text).strip()
    # Search for the phrase we know exists
    idx = text.find('Typically uses a verse-chorus')
    if idx >= 0:
        print("Found at idx", idx)
        print(text[idx:idx+5000])