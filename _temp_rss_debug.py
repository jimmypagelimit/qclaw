import urllib.request, json, hashlib
from xml.etree import ElementTree as ET
from datetime import datetime, timezone, timedelta
import html, re

MAX_AGE_HOURS = 48

def fetch_rss(rss_url):
    req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
    data = urllib.request.urlopen(req, timeout=15).read()
    return ET.fromstring(data)

root = fetch_rss("https://pitchfork.com/feed/rss")
items = root.findall('.//item')
now = datetime.now(timezone.utc)
cutoff = now - timedelta(hours=MAX_AGE_HOURS)

results = []
for item in items[:15]:
    title = item.find('title').text or ''
    link = item.find('link').text or ''
    pub_date_str = item.find('pubDate').text or ''
    
    try:
        pub_date = datetime.strptime(pub_date_str.strip(), '%a, %d %b %Y %H:%M:%S %z')
    except:
        pub_date = None
    
    is_recent = pub_date and pub_date >= cutoff
    link_hash = hashlib.md5(link.encode()).hexdigest()
    
    results.append({
        'title': title,
        'link': link,
        'link_hash': link_hash,
        'date': pub_date,
        'is_recent': is_recent
    })

with open(r'C:\Users\qujt\.qclaw\workspace\_temp_debug_rss.json', 'w', encoding='utf-8') as f:
    json.dump([{
        'title': r['title'],
        'link': r['link'],
        'link_hash': r['link_hash'],
        'date': str(r['date']),
        'is_recent': r['is_recent']
    } for r in results], f, ensure_ascii=False, indent=2)

print(f"Total: {len(results)}, Recent: {sum(1 for r in results if r['is_recent'])}")
print(f"Now: {now}, Cutoff: {cutoff}")
