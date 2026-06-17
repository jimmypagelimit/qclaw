# -*- coding: utf-8 -*-
import urllib.request, re, sys

blogs = [
    ('Mix It All Up', 'http://mixitallup.com/feed/'),
    ('Country and Folk', 'https://www.countryandfolk.com/feed/'),
    ('Folksy Blog', 'https://blog.folksy.com/feed/'),
    ('Rock Dafuq Out', 'https://rockdafuqout.com/feed/'),
    ('Indie Shuffle', 'https://indieshuffle.com/feed/'),
    ('Earmilk', 'https://www.earmilk.com/feed/'),
    ('Hype Machine', 'https://hypem.com/wordpress/feed/'),
    ('Line of Best Fit', 'https://www.thelineofbestfit.com/feed/'),
    ('When You Motor Away', 'https://whenyoumotoraway.com/feed/'),
    ('Deli Magazine', 'https://www.delimagazine.com/feed'),
    ('Raven Sings', 'https://ravensingstheblues.com/feed/'),
    ('Gigslutz', 'https://gigslutz.co.uk/feed/'),
    ('Sounds of the Suburbs', 'https://soundsofthesuburbs.wordpress.com/feed/'),
    ('KEXP Blog', 'https://blog.kexp.org/feed/'),
    ('BBC Music', 'https://www.bbc.co.uk/music/rss.xml'),
    ('Treble', 'https://treblezine.com/feed/'),
    ('Uproxx Music', 'https://uproxx.com/music/feed/'),
    ('Thrillist Music', 'https://thrillist.com/feed/music'),
    ('BrooklynVegan', 'https://www.brooklynvegan.com/feed/'),
    ('Flood Magazine', 'https://www.floodmagazine.com/feed/'),
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
ok = []
for name, url in blogs:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='replace')
        items = re.findall(r'<item', resp, re.IGNORECASE)
        if items:
            ok.append((name, url, len(items)))
            sys.stdout.buffer.write(f"[OK] {name}: {len(items)} items\n".encode('utf-8'))
        else:
            sys.stdout.buffer.write(f"[EMPTY] {name}\n".encode('utf-8'))
    except Exception as e:
        msg = str(e)[:60]
        sys.stdout.buffer.write(f"[FAIL] {name}: {msg}\n".encode('utf-8'))

sys.stdout.buffer.write(f"\n--- Working: {len(ok)}/{len(blogs)} ---\n".encode('utf-8'))
for name, url, n in ok:
    sys.stdout.buffer.write(f"  {{\"name\": \"{name}\", \"rss\": \"{url}\"}},\n".encode('utf-8'))
