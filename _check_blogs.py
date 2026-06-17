# -*- coding: utf-8 -*-
import urllib.request, re, sys

blogs = [
    ('Testing Melodies', 'https://www.testingmelodies.com/feed/'),
    ('Indie Music Review', 'https://www.indiemusicreview.com/feed/'),
    ('RocknRowling', 'https://rocknrowling.com/feed/'),
    ('Sound Check', 'https://soundcheck.blog/feed/'),
    ('New Music Review UK', 'https://www.newmusicreview.co.uk/feed/'),
    ('Classic Rock Review', 'https://classicrockreview.wordpress.com/feed/'),
    ('Musicscanner', 'https://musicscannersite.wordpress.com/feed/'),
    ('MusicOMH', 'https://www.musicomh.com/feed'),
    ('Drowned In Sound', 'https://drownedinsound.com/rss'),
    ('Beats Per Minute', 'https://beatsperminute.com/feed/'),
    ('Mourning Coffee', 'https://mourningcoffee.com/feed/'),
    ('The Punk Site', 'https://www.thepunksite.com/feed/'),
    ('New Transcendence', 'https://new-transcendence.com/feed/'),
    ('Folk Radio', 'https://folkradio.co.uk/feed/'),
    ('Backseat Mafia', 'https://backseatmafia.com/feed/'),
    ('The Idle Hands', 'https://theidlehands.com/feed'),
    ('Austin Town Hall', 'https://austintownhall.com/feed'),
    ('My Mag', 'https://www.mymusicblog.co.uk/feed/'),
]

HEADERS = {'User-Agent': 'Mozilla/5.0'}
ok = []
for name, url in blogs:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='replace')
        items = re.findall(r'<item', resp, re.IGNORECASE)
        ok.append((name, url, len(items)))
        sys.stdout.buffer.write(f"[OK] {name}: {len(items)} items\n".encode('utf-8'))
    except Exception as e:
        sys.stdout.buffer.write(f"[FAIL] {name}: {str(e)[:60]}\n".encode('utf-8'))

sys.stdout.buffer.write(f"\n--- Working: {len(ok)}/{len(blogs)} ---\n".encode('utf-8'))
for name, url, n in ok:
    sys.stdout.buffer.write(f"  {name}: {url}\n".encode('utf-8'))