import urllib.request
import xml.etree.ElementTree as ET
import datetime
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

now = datetime.datetime.now()
week_ago = now - datetime.timedelta(days=7)

rss_feeds = [
    ('lionsroar', 'buddhism', 'https://www.lionsroar.com/feed/'),
    ('tricycle', 'buddhism', 'https://tricycle.org/feed/'),
    ('christianitytoday', 'christianity', 'https://www.christianitytoday.com/feed/'),
    ('religionnews', 'general', 'https://religionnews.com/feed/'),
    ('islam21c', 'islam', 'https://www.islam21c.com/feed/'),
    ('jpost', 'judaism', 'https://www.jpost.com/rss'),
    ('jns', 'judaism', 'https://www.jns.org/index.rss'),
    ('timesofisrael', 'judaism', 'https://www.timesofisrael.com/feed/'),
    ('forward', 'judaism', 'https://forward.com/feed/'),
    ('worldsikhnews', 'sikh', 'https://www.theworldsikhnews.com/feed/'),
    ('sikhsiyasat', 'sikh', 'https://sikhsiyasatnews.net/feed/'),
]

all_articles = {'buddhism': [], 'christianity': [], 'islam': [], 'judaism': [], 'sikh': [], 'general': []}

for name, category, url in rss_feeds:
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        })
        resp = urllib.request.urlopen(req, timeout=20, context=ctx)
        data = resp.read()
        root = ET.fromstring(data)
        
        items = []
        
        # RSS 2.0
        for item in root.findall('.//item'):
            title = item.findtext('title', '')
            link = item.findtext('link', '')
            pub_date = item.findtext('pubDate', '')
            desc = item.findtext('description', '')
            
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(pub_date)
                dt_naive = dt.replace(tzinfo=None)
                if dt_naive >= week_ago.replace(tzinfo=None):
                    # Clean description
                    import re
                    desc_clean = re.sub('<[^>]+>', '', desc or '')[:200]
                    items.append({
                        'title': title.strip(),
                        'link': link.strip(),
                        'date': dt.strftime('%Y-%m-%d'),
                        'source': name,
                        'desc': desc_clean.strip()
                    })
            except:
                pass
        
        # Atom
        if not items:
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            for entry in root.findall('.//atom:entry', ns):
                title = entry.findtext('atom:title', '', ns)
                link_elem = entry.find('atom:link', ns)
                link = link_elem.get('href', '') if link_elem is not None else ''
                updated = entry.findtext('atom:updated', '', ns)
                published = entry.findtext('atom:published', '', ns)
                date_str = published or updated
                
                try:
                    dt = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    dt_naive = dt.replace(tzinfo=None)
                    if dt_naive >= week_ago.replace(tzinfo=None):
                        items.append({
                            'title': title.strip(),
                            'link': link.strip(),
                            'date': dt.strftime('%Y-%m-%d'),
                            'source': name,
                            'desc': ''
                        })
                except:
                    pass
        
        for item in items:
            all_articles[category].append(item)
        
        print(f'OK: {name} ({category}) - {len(items)} articles')
    except Exception as e:
        print(f'FAIL: {name} ({category}) - {e}')

# 保存为JSON
with open('religion_articles.json', 'w', encoding='utf-8') as f:
    json.dump(all_articles, f, ensure_ascii=False, indent=2)

print('\n=== ALL RECENT ARTICLES ===')
for cat, articles in all_articles.items():
    print(f'\n--- {cat.upper()}: {len(articles)} articles ---')
    for a in articles:
        print(f'  [{a["date"]}] {a["title"][:80]}')
        print(f'    {a["link"]}')
