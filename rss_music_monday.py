#!/usr/bin/env python3
"""Batch RSS fetcher for heartbeat - no feedparser, pure stdlib"""
import urllib.request, urllib.error, json, time, re
from datetime import datetime, timezone

def fetch(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        for enc in encodings:
            try:
                return raw.decode(enc)
            except:
                pass
        return raw.decode('utf-8', errors='replace')
    except Exception as e:
        return None

def parse_feed(xml_text, max_items=5, max_age_days=2):
    cutoff = time.time() - max_age_days * 86400
    items = []
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_text)
        ns = {}
        # detect namespace
        tag = root.tag
        if tag.startswith('{'):
            ns['def'] = tag[1:tag.index('}')]
        entries = root.findall('.//item') or root.findall('.//entry')
        for entry in entries[:max_items]:
            def f(tag):
                return entry.findtext(f'.//{tag}', '', ns)
            title = entry.findtext('title', '', ns)
            link = entry.findtext('link', '', ns)
            pub_raw = entry.findtext('pubDate', entry.findtext('published', '', ns), ns)
            if not link and entry.findtext('{http://www.w3.org/2005/Atom}href'):
                link = entry.findtext('{http://www.w3.org/2005/Atom}href')
            ts = None
            if pub_raw:
                try:
                    import email.utils
                    parsed = email.utils.parsedate_to_datetime(pub_raw)
                    ts = parsed.timestamp()
                except:
                    pass
            if ts and ts < cutoff:
                continue
            if title:
                items.append({'title': title[:120], 'link': link, 'pub_ts': ts})
    except Exception as e:
        pass
    return items

FEEDS = [
    ("Pitchfork", "https://pitchfork.com/feed/rss"),
    ("Stereogum", "https://www.stereogum.com/feed/"),
    ("Consequence", "https://consequence.net/feed/"),
    ("NME", "https://www.nme.com/feed/"),
    ("BrooklynVegan", "https://www.brooklynvegan.com/feed/"),
    ("Paste Magazine", "https://www.pastemagazine.com/feed/"),
    ("The Quietus", "https://www.thequietus.com/rss"),
    ("PopMatters", "https://www.popmatters.com/feed"),
    ("Line of Best Fit", "https://www.thelineofbestfit.com/feed/"),
    ("DIY Magazine", "https://diymag.com/feeds/all"),
    ("God Is in the TV", "https://www.godisinthetvzine.co.uk/feed"),
    ("Louder Than War", "https://louderthanwar.com/feed"),
    ("GoldenPlec", "https://www.goldenplec.com/feed"),
    ("Fact Magazine", "https://www.factmag.com/feed"),
    ("AV Club", "https://www.avclub.com/feed"),
    ("Spin", "https://www.spinmagazine.com/feed/"),
    ("Billboard", "https://www.billboard.com/feed/"),
    ("Hearing Things", "https://www.hearingthings.co/archive/rss/"),
    ("Post-Punk.com", "https://post-punk.com/feed/"),
    ("Aquarium Drunkard", "https://aquariumdrunkard.com/feed/"),
    ("Bandcamp Daily", "https://daily.bandcamp.com/feed"),
    ("MusicOMH", "https://www.musicomh.com/feed"),
    ("Decibel", "https://www.decibelmagazine.com/feed/"),
    ("No Clean Singing", "https://www.nocleansinging.com/feed/"),
    ("Invisible Oranges", "https://www.invisibleoranges.com/feed/"),
    ("Angry Metal Guy", "https://www.angrymetalguy.com/feed/"),
    ("Toilet Ov Hell", "https://toiletovhell.com/feed/"),
    ("Metal-Hammer", "https://www.metal-hammer.de/feed/"),
    ("Lambgoat", "https://www.lambgoat.com/rss/news"),
    ("MetalSucks", "https://www.metalsucks.net/feed/"),
    ("Metal Injection", "https://metalinjection.net/feed/"),
    ("No Echo", "https://feeds.feedburner.com/noecho"),
    ("r/indieheads", "https://www.reddit.com/r/indieheads/.rss"),
    ("r/shoegaze", "https://www.reddit.com/r/shoegaze/.rss"),
    ("r/postrock", "https://www.reddit.com/r/postrock/.rss"),
    ("r/noiserock", "https://www.reddit.com/r/noiserock/.rss"),
    ("r/postpunk", "https://www.reddit.com/r/postpunk/.rss"),
    ("r/Metal", "https://www.reddit.com/r/Metal/.rss"),
    ("r/blackmetal", "https://www.reddit.com/r/blackmetal/.rss"),
    ("r/LetsTalkMusic", "https://www.reddit.com/r/LetsTalkMusic/.rss"),
    ("r/experimentalmusic", "https://www.reddit.com/r/experimentalmusic/.rss"),
    ("r/indie_rock", "https://www.reddit.com/r/indie_rock/.rss"),
    ("UPEE", "https://upee.substack.com/feed"),
    ("Les Inrockuptibles", "https://www.lesinrocks.com/culture/musique/feed/"),
    ("Jenesaispop", "https://jenesaispop.com/feed/"),
    ("L'Indiependente", "https://www.lindiependente.it/feed/"),
    ("Mondosonoro", "https://www.mondosonoro.com/feed/"),
    ("Clash Music", "https://www.clashmusic.com/feed/"),
    ("fRoots", "https://frootsmag.com/feed"),
]

results = []
for site, url in FEEDS:
    text = fetch(url)
    if text:
        items = parse_feed(text, max_items=5, max_age_days=2)
        for item in items:
            item['site'] = site
            results.append(item)

# Deduplicate by title
seen = set()
unique = []
for r in results:
    key = r['title'][:80]
    if key not in seen:
        seen.add(key)
        unique.append(r)

# Sort newest first
unique.sort(key=lambda x: x.get('pub_ts') or 0, reverse=True)

with open(r'C:\Users\qujt\.qclaw\workspace\rss_music_result.json', 'w', encoding='utf-8') as f:
    json.dump(unique[:80], f, ensure_ascii=False, indent=2)

print(f"Fetched {len(unique)} items from {len(FEEDS)} feeds")