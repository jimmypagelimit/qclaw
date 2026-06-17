import urllib.request
from xml.etree import ElementTree as ET

url = "https://pitchfork.com/feed/rss"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
data = urllib.request.urlopen(req, timeout=15).read()
root = ET.fromstring(data)
items = root.findall('.//item')
with open(r'C:\Users\qujt\.qclaw\workspace\_temp_rss_test.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total items: {len(items)}\n\n")
    for item in items[:10]:
        title = item.find('title').text if item.find('title') is not None else 'N/A'
        link = item.find('link').text if item.find('link') is not None else 'N/A'
        pub = item.find('pubDate').text if item.find('pubDate') is not None else 'N/A'
        cats = [c.text for c in item.findall('category')]
        f.write(f"Title: {title}\nLink: {link}\nDate: {pub}\nCats: {cats}\n\n")
