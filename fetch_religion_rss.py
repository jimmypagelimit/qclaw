import urllib.request
import xml.etree.ElementTree as ET
import datetime
import json
import ssl

# 忽略SSL验证（部分站点可能需要）
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 计算7天前日期
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
    ('reddit_religion', 'general', 'https://www.reddit.com/r/religion/.rss'),
    ('reddit_buddhism', 'buddhism', 'https://www.reddit.com/r/Buddhism/.rss'),
    ('reddit_christianity', 'christianity', 'https://www.reddit.com/r/Christianity/.rss'),
    ('reddit_islam', 'islam', 'https://www.reddit.com/r/islam/.rss'),
    ('reddit_judaism', 'judaism', 'https://www.reddit.com/r/Judaism/.rss'),
]

results = {}
for name, category, url in rss_feeds:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        data = resp.read()
        root = ET.fromstring(data)
        
        items = []
        
        # 尝试 RSS 2.0 格式 (item)
        for item in root.findall('.//item'):
            title = item.findtext('title', '')
            link = item.findtext('link', '')
            pub_date = item.findtext('pubDate', '')
            desc = item.findtext('description', '')
            
            # 解析日期
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(pub_date)
                dt_naive = dt.replace(tzinfo=None)
                if dt_naive >= week_ago.replace(tzinfo=None):
                    items.append({'title': title.strip(), 'link': link.strip(), 'date': str(dt)})
            except Exception as e2:
                pass
        
        # 尝试 Atom 格式 (entry)
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
                        items.append({'title': title.strip(), 'link': link.strip(), 'date': str(dt)})
                except Exception as e3:
                    pass
        
        results[name] = {'category': category, 'count': len(items), 'items': items[:5]}
        print(f'{name}: {len(items)} recent articles')
    except Exception as e:
        print(f'{name}: ERROR - {e}')
        results[name] = {'category': category, 'count': 0, 'error': str(e)}

print()
print('=== SUMMARY ===')
for name, data in results.items():
    cat = data['category']
    count = data['count']
    print(f'{name} ({cat}): {count} articles')

# 按类别整理
categories = {'buddhism': [], 'christianity': [], 'islam': [], 'judaism': [], 'sikh': [], 'general': []}
for name, data in results.items():
    cat = data['category']
    for item in data.get('items', []):
        categories[cat].append({'source': name, **item})

print()
for cat, items in categories.items():
    print(f'\n--- {cat.upper()} ({len(items)} articles) ---')
    for item in items[:3]:
        print(f'  [{item["source"]}] {item["title"]}')
        print(f'    {item["link"]}')
