#!/usr/bin/env python3
import urllib.request, re, sys, html

urls = {
    "Lion's Roar": "https://www.lionsroar.com/feed/",
    "Tricycle": "https://tricycle.org/feed/",
    "Christianity Today": "https://www.christianitytoday.com/feed/",
    "Religion News": "https://religionnews.com/feed/",
    "Islam21c": "https://www.islam21c.com/feed/",
    "JPost": "https://www.jpost.com/rss",
    "JNS": "https://www.jns.org/index.rss",
    "World Sikh News": "https://www.theworldsikhnews.com/feed/",
    "Sikh Siyasat": "https://sikhsiyasatnews.net/feed/",
    "r/religion": "https://www.reddit.com/r/religion/.rss",
    "r/Buddhism": "https://www.reddit.com/r/Buddhism/.rss",
}

for name, url in urls.items():
    print(f"\n=== {name} ===")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read().decode("utf-8", errors="replace")
        titles = re.findall(r'<title>(.*?)</title>', data)
        seen = set()
        count = 0
        for t in titles:
            t = html.unescape(t).strip()
            if t and t not in seen and len(t) > 3:
                print(f"  {t}")
                seen.add(t)
                count += 1
                if count >= 8:
                    break
        if count == 0:
            print("  (no titles found)")
    except Exception as e:
        print(f"  ERROR: {e}")
