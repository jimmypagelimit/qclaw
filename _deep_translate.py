# -*- coding: utf-8 -*-
"""
深度翻译管道 v4：三时段全覆盖
Indie/Rock/Folk + Metal + Experimental
45个源（17专业媒体 + 28个人博客），覆盖独立/摇滚/民谣/金属
不碰CF站
"""
import urllib.request, json, re, os, sys, time, hashlib, html
from datetime import datetime, timezone, timedelta

SLOT_SOURCES = {
    "indie": {
        "name": "独立/摇滚/民谣",
        "emoji": "🎸",
        "max_articles": 5,
        "sources": [
            {"name": "Pitchfork", "rss": "https://pitchfork.com/feed/rss"},
            {"name": "Stereogum", "rss": "https://www.stereogum.com/feed/"},
            {"name": "Consequence", "rss": "https://consequence.net/feed/"},
            {"name": "Paste", "rss": "https://www.pastemagazine.com/feed/"},
            {"name": "PopMatters", "rss": "https://www.popmatters.com/feed"},
            {"name": "The Quietus", "rss": "https://www.thequietus.com/rss"},
            {"name": "TLOBF", "rss": "https://www.thelineofbestfit.com/feed/"},
            {"name": "God Is in the TV", "rss": "https://www.godisinthetvzine.co.uk/feed"},
            {"name": "Louder Than War", "rss": "https://louderthanwar.com/feed/"},
            {"name": "AV Club", "rss": "https://www.avclub.com/feed/"},
            {"name": "Spin", "rss": "https://www.spinmagazine.com/feed/"},
            {"name": "Hearing Things", "rss": "https://www.hearingthings.co/archive/rss/"},
            {"name": "Post-Punk.com", "rss": "https://post-punk.com/feed/"},
            {"name": "Bandcamp Daily", "rss": "https://daily.bandcamp.com/feed"},
            {"name": "MusicOMH", "rss": "https://www.musicomh.com/feed/"},
            {"name": "Clash Music", "rss": "https://www.clashmusic.com/feed/"},
            {"name": "Aquarium Drunkard", "rss": "https://aquariumdrunkard.com/feed/"},
            {"name": "Beats Per Minute", "rss": "https://beatsperminute.com/feed/"},
            {"name": "Folk Radio UK", "rss": "https://folkradio.co.uk/feed/"},
            {"name": "Backseat Mafia", "rss": "https://backseatmafia.com/feed/"},
            {"name": "Austin Town Hall", "rss": "https://austintownhall.com/feed/"},
            {"name": "Earmilk", "rss": "https://www.earmilk.com/feed/"},
            {"name": "Treble", "rss": "https://treblezine.com/feed/"},
            {"name": "Uproxx Music", "rss": "https://uproxx.com/music/feed/"},
            {"name": "Mix It All Up", "rss": "http://mixitallup.com/feed/"},
            {"name": "Gigslutz", "rss": "https://gigslutz.co.uk/feed/"},
        ]
    },
    "metal": {
        "name": "金属/硬核",
        "emoji": "🔥",
        "max_articles": 5,
        "sources": [
            {"name": "Decibel", "rss": "https://www.decibelmagazine.com/feed/"},
            {"name": "Angry Metal Guy", "rss": "https://www.angrymetalguy.com/feed/"},
            {"name": "No Clean Singing", "rss": "https://www.nocleansinging.com/feed/"},
            {"name": "Metal Injection", "rss": "https://metalinjection.net/feed/"},
            {"name": "Invisible Oranges", "rss": "https://www.invisibleoranges.com/feed/"},
            {"name": "Toilet Ov Hell", "rss": "https://toiletovhell.com/feed/"},
            {"name": "MetalSucks", "rss": "https://www.metalsucks.net/feed/"},
            {"name": "Metal-Hammer.de", "rss": "https://www.metal-hammer.de/feed/"},
            {"name": "No Echo", "rss": "https://feeds.feedburner.com/noecho"},
            {"name": "Lambgoat", "rss": "https://www.lambgoat.com/rss/news"},
            {"name": "The Punk Site", "rss": "https://www.thepunksite.com/feed/"},
        ]
    },
    "folk": {
        "name": "实验/地下",
        "emoji": "🌊",
        "max_articles": 3,
        "sources": [
            {"name": "Aquarium Drunkard", "rss": "https://aquariumdrunkard.com/feed/"},
            {"name": "The Quietus", "rss": "https://www.thequietus.com/rss"},
            {"name": "TLOBF", "rss": "https://www.thelineofbestfit.com/feed/"},
            {"name": "Bandcamp Daily", "rss": "https://daily.bandcamp.com/feed/"},
            {"name": "PopMatters", "rss": "https://www.popmatters.com/feed"},
            {"name": "Louder Than War", "rss": "https://louderthanwar.com/feed/"},
            {"name": "GoldenPlec", "rss": "https://www.goldenplec.com/feed/"},
            {"name": "Post-Punk.com", "rss": "https://post-punk.com/feed/"},
            {"name": "Indie Music Review", "rss": "https://www.indiemusicreview.com/feed/"},
            {"name": "Sound Check Blog", "rss": "https://soundcheck.blog/feed/"},
            {"name": "New Music Review UK", "rss": "https://www.newmusicreview.co.uk/feed/"},
            {"name": "Classic Rock Review", "rss": "https://classicrockreview.wordpress.com/feed/"},
            {"name": "Musicscanner", "rss": "https://musicscannersite.wordpress.com/feed/"},
            {"name": "New Transcendence", "rss": "https://new-transcendence.com/feed/"},
            {"name": "Sounds of the Suburbs", "rss": "https://soundsofthesuburbs.wordpress.com/feed/"},
        ]
    }
}

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_translate_history.json")
MAX_AGE_HOURS = 48
HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; FeedFetcher)'}

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"translated": []}

def save_history(hist):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)

def is_translated(hist, url):
    if not url:
        return False
    return hashlib.md5(url.encode()).hexdigest() in hist["translated"]

def mark_translated(hist, url):
    if not url:
        return
    h = hashlib.md5(url.encode()).hexdigest()
    if h not in hist["translated"]:
        hist["translated"].append(h)
    if len(hist["translated"]) > 1000:
        hist["translated"] = hist["translated"][-1000:]

def fetch_rss(rss_url):
    try:
        req = urllib.request.Request(rss_url, headers=HEADERS)
        raw = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='replace')
    except Exception:
        return []
    
    items = re.findall(r'<item[^>]*>(.*?)</item>', raw, re.DOTALL | re.IGNORECASE)
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=MAX_AGE_HOURS)
    articles = []
    
    for block in items:
        # Title (handle CDATA)
        tm = re.search(r'<title[^>]*>(.*?)</title>', block, re.DOTALL | re.IGNORECASE)
        if not tm:
            continue
        title = html.unescape(tm.group(1).strip())
        cm = re.match(r'<!\[CDATA\[(.*?)\]\]>', title, re.DOTALL)
        if cm:
            title = cm.group(1).strip()
        if not title:
            continue
        
        # Link
        lm = re.search(r'<link[^>]*>(.*?)</link>', block, re.DOTALL | re.IGNORECASE)
        link = lm.group(1).strip() if lm else ''
        
        # Date
        dm = re.search(r'<pubDate[^>]*>(.*?)</pubDate>', block, re.DOTALL | re.IGNORECASE)
        pub_date = None
        if dm:
            ds = dm.group(1).strip()
            for fmt in ('%a, %d %b %Y %H:%M:%S %z', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%SZ'):
                try:
                    pub_date = datetime.strptime(ds, fmt)
                    if pub_date.tzinfo is None:
                        pub_date = pub_date.replace(tzinfo=timezone.utc)
                    break
                except:
                    continue
        
        if pub_date and pub_date < cutoff:
            continue
        
        # Categories
        cats = re.findall(r'<category[^>]*>(.*?)</category>', block, re.IGNORECASE)
        cats_lower = [c.lower() for c in cats]
        
        # Score
        score = 0
        tl = title.lower()
        cj = ' '.join(cats_lower)
        
        if any(w in tl for w in ['review', 'interview', 'profile']):
            score += 3
        if any(w in cj for w in ['review', 'interview']):
            score += 3
        if any(w in tl for w in ['best new music', 'bnm', 'best new']):
            score += 5
        for s in re.findall(r'(\d+\.\d+)', title):
            if float(s) >= 8.0:
                score += 4
            elif float(s) >= 7.0:
                score += 2
        if 'reviews / albums' in cj:
            score += 2
        
        articles.append({
            'title': title, 'link': link, 'date': pub_date.isoformat() if pub_date else '',
            'score': score, 'categories': cats
        })
    
    return articles

def fetch_full_text(url):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html'
        })
        resp = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='replace')
        for pat in (r'<script[^>]*>.*?</script>', r'<style[^>]*>.*?</style>',
                    r'<nav[^>]*>.*?</nav>', r'<header[^>]*>.*?</header>', r'<footer[^>]*>.*?</footer>'):
            resp = re.sub(pat, '', resp, flags=re.DOTALL | re.IGNORECASE)
        
        am = re.search(r'<article[^>]*>(.*?)</article>', resp, re.DOTALL | re.IGNORECASE)
        content = am.group(1) if am else resp
        content = re.sub(r'<br\s*/?>', '\n', content)
        content = re.sub(r'</p>', '\n\n', content, flags=re.IGNORECASE)
        content = re.sub(r'<[^>]+>', '', content)
        content = html.unescape(content)
        content = re.sub(r'\n{3,}', '\n\n', content).strip()
        return content[:8000] + ('...' if len(content) > 8000 else '')
    except Exception as e:
        return f"[Fetch failed: {e}]"

def main():
    slot = None
    for i, arg in enumerate(sys.argv):
        if arg == '--slot' and i + 1 < len(sys.argv):
            slot = sys.argv[i + 1]
        elif arg.startswith('--slot='):
            slot = arg.split('=', 1)[1]
    
    if slot not in SLOT_SOURCES:
        sys.stderr.write("Usage: python _deep_translate.py --slot indie|metal|folk\n")
        sys.exit(1)
    
    cfg = SLOT_SOURCES[slot]
    hist = load_history()
    
    all_articles = []
    for src in cfg["sources"]:
        try:
            arts = fetch_rss(src["rss"])
            for a in arts:
                a['source_name'] = src["name"]
                if a['link'] and not is_translated(hist, a['link']):
                    all_articles.append(a)
        except:
            continue
    
    all_articles.sort(key=lambda x: (x['score'], x['date']), reverse=True)
    
    # Pick: max N articles, max 1 per source
    picked = []
    seen_src = set()
    for a in all_articles:
        if a['source_name'] in seen_src:
            continue
        if a['score'] < 3 and len(picked) >= 2:
            continue  # only take low-score articles if we have room
        picked.append(a)
        seen_src.add(a['source_name'])
        if len(picked) >= cfg["max_articles"]:
            break
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    if not picked:
        output = {"slot": slot, "name": cfg["name"], "emoji": cfg["emoji"], "articles": []}
        with open(os.path.join(script_dir, f"_translate_{slot}.json"), 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        sys.stdout.buffer.write(f"{cfg['emoji']} {cfg['name']}：今日无重要更新\n".encode('utf-8'))
        return
    
    results = []
    for a in picked:
        ft = fetch_full_text(a['link'])
        results.append({
            'title': a['title'], 'link': a['link'], 'source': a['source_name'],
            'date': a['date'], 'score': a['score'], 'full_text': ft
        })
        mark_translated(hist, a['link'])
        time.sleep(1)
    
    save_history(hist)
    
    output = {"slot": slot, "name": cfg["name"], "emoji": cfg["emoji"], "articles": results}
    with open(os.path.join(script_dir, f"_translate_{slot}.json"), 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    sys.stdout.buffer.write(f"{cfg['emoji']} {cfg['name']}：抓取 {len(results)} 篇\n".encode('utf-8'))
    for r in results:
        sys.stdout.buffer.write(f"  - [{r['source']}] {r['title']} ({r['score']})\n".encode('utf-8'))

if __name__ == '__main__':
    main()
