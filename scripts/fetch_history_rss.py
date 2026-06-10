import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
import os

china_tz = timezone(timedelta(hours=8))
now = datetime.now(china_tz)
cutoff = now - timedelta(hours=72)  # 3 days for weekly task

sources = [
    ('History Today', 'https://www.historytoday.com/rss.xml'),
    ('History Extra', 'https://www.historyextra.com/feed'),
    ('History Workshop', 'https://historyworkshop.org.uk/feed/'),
    ('Smithsonian', 'https://www.smithsonianmag.com/rss/latest_articles/'),
    ('OUP History', 'https://blog.oup.com/category/history/feed/'),
    ('World History Encyclopedia', 'https://www.worldhistory.org/rss/'),
    ('Medievalists.net', 'https://www.medievalists.net/feed/'),
    ('Foreign Affairs', 'https://www.foreignaffairs.com/rss.xml'),
    ('Journal of Democracy', 'https://www.journalofdemocracy.org/feed/'),
]

all_items = []
for name, url in sources:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        root = ET.fromstring(data)
        
        for item in root.findall('.//item'):
            title = item.findtext('title', '').strip()
            link = item.findtext('link', '').strip()
            pub = item.findtext('pubDate', '')
            try:
                dt = parsedate_to_datetime(pub) if pub else None
                if dt and dt.replace(tzinfo=timezone.utc) >= cutoff.replace(tzinfo=None).replace(tzinfo=timezone.utc):
                    all_items.append({'src': name, 'title': title, 'link': link, 'pub': pub, 'dt': dt})
            except:
                pass
        
        # Try atom format
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
            title = entry.findtext('{http://www.w3.org/2005/Atom}title', '').strip()
            link_el = entry.find('{http://www.w3.org/2005/Atom}link')
            link = link_el.get('href', '') if link_el is not None else ''
            updated = entry.findtext('{http://www.w3.org/2005/Atom}updated', '')
            try:
                dt = datetime.fromisoformat(updated.replace('Z', '+00:00')) if updated else None
                if dt and dt >= cutoff.replace(tzinfo=None):
                    all_items.append({'src': name, 'title': title, 'link': link, 'pub': updated, 'dt': dt})
            except:
                pass
    except Exception as e:
        print(f'ERROR {name}: {e}')

# Reddit history sources
reddit_sources = [
    ('r/AskHistorians', 'https://www.reddit.com/r/AskHistorians/.rss'),
    ('r/history', 'https://www.reddit.com/r/history/.rss'),
    ('r/ChineseHistory', 'https://www.reddit.com/r/ChineseHistory/.rss'),
    ('r/medihist', 'https://www.reddit.com/r/medihist/.rss'),
]

for name, url in reddit_sources:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        root = ET.fromstring(data)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
            title = entry.findtext('{http://www.w3.org/2005/Atom}title', '').strip()
            link_el = entry.find('{http://www.w3.org/2005/Atom}link')
            link = link_el.get('href', '') if link_el is not None else ''
            updated = entry.findtext('{http://www.w3.org/2005/Atom}updated', '')
            try:
                dt = datetime.fromisoformat(updated.replace('Z', '+00:00')) if updated else None
                if dt and dt >= cutoff.replace(tzinfo=None):
                    all_items.append({'src': name, 'title': title, 'link': link, 'pub': updated, 'dt': dt})
            except:
                pass
    except Exception as e:
        print(f'ERROR {name}: {e}')

all_items.sort(key=lambda x: x['dt'], reverse=True)

out_path = 'C:/Users/qujt/.qclaw/workspace/heartbeat_history_20260610.txt'
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(f'Total: {len(all_items)}\n\n')
    for it in all_items:
        pub_str = it['dt'].strftime('%Y-%m-%d %H:%M') if it['dt'] else '?'
        f.write(f"[{it['src']}] {pub_str} | {it['title']}\n")
        f.write(f"  {it['link']}\n\n")

print(f'Done. {len(all_items)} items saved to {out_path}')
