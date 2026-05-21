import urllib.request, ssl, re, sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

feeds = [
    ("Pitchfork", "https://pitchfork.com/feed/rss"),
    ("Stereogum", "https://www.stereogum.com/feed/"),
    ("Consequence", "https://consequence.net/feed/"),
    ("Metal Injection", "https://metalinjection.net/feed/"),
    ("Post-Punk.com", "https://www.post-punk.com/feed/"),
    ("Decibel", "https://www.decibelmagazine.com/feed/"),
    ("Angry Metal Guy", "https://www.angrymetalguy.com/feed/"),
    ("Invisible Oranges", "https://www.invisibleoranges.com/feed/"),
    ("No Echo", "https://www.noecho.net/feed"),
    ("Lambgoat", "https://www.lambgoat.com/rss.xml"),
    ("BrooklynVegan", "https://www.brooklynvegan.com/rss"),
    ("Aquarium Drunkard", "https://aquariumdrunkard.com/feed/"),
]

for name, url in feeds:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        data = resp.read().decode("utf-8", errors="replace")
        titles = re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>", data)
        if not titles:
            titles = re.findall(r"<title>(.*?)</title>", data)
        titles = [t.strip() for t in titles if t.strip() and t.strip() != name]
        if titles:
            print(f"=== {name} ({len(titles)} titles) ===")
            for t in titles[:20]:
                print(f"  {t}")
            print()
        else:
            print(f"=== {name} === (no titles)")
    except Exception as e:
        print(f"=== {name} === ERROR: {e}")
