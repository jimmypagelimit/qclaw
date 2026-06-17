# -*- coding: utf-8 -*-
import urllib.request, re, sys

blogs = [
    # Personal indie blogs
    ('Mix It All Up', 'http://mixitallup.com/feed/'),
    ('Beats Per Minute', 'https://beatsperminute.com/feed/'),
    ('Folk Radio UK', 'https://folkradio.co.uk/feed/'),
    ('Backseat Mafia', 'https://backseatmafia.com/feed/'),
    ('The Punk Site', 'https://www.thepunksite.com/feed/'),
    ('New Transcendence', 'https://new-transcendence.com/feed/'),
    ('Austin Town Hall', 'https://austintownhall.com/feed'),
    ('Musicscanner', 'https://musicscannersite.wordpress.com/feed/'),
    ('Classic Rock Review', 'https://classicrockreview.wordpress.com/feed/'),
    # More indie blogs
    ('Indie Music Review', 'https://www.indiemusicreview.com/feed/'),
    ('Sound Check', 'https://soundcheck.blog/feed/'),
    ('New Music Review UK', 'https://www.newmusicreview.co.uk/feed/'),
    # Metal blogs
    ('Metal Storm', 'https://www.metalstorm.net/rss/'),
    ('Heavy Blog Is Heavy', 'https://www.heavyblogisheavy.com/feed/'),
    ('MRU Heavy Music', 'https://www.musicremission.com/feed/'),
    ('Sentinel Daily', 'https://sentimentor.com/feed/'),
    ('Overkill', 'https://www.getreadyforoverkill.com/feed/'),
    # Folk/Americana
    ('No Ripcord', 'https://www.noripcord.com/feed/'),
    ('American Pancake', 'http://americanpancake.blogspot.com/feeds/posts/default?alt=rss'),
    ('I Guess I\'m Floating', 'https://iguessimfloating.blogspot.com/feeds/posts/default?alt=rss'),
    # Experimental
    ('Sonic Abuse', 'https://sonicabuse.com/feed/'),
    ('The Obelisk', 'https://www.getreadyforoverkill.com/feed/'),
    ('Crypt', 'https://www.cryptmagazine.com/feed/'),
    # More indie blogs
    ('Almost (Music Blog)', 'https://almostmusicblog.com/feed/'),
    ('Don\'t Eat The Paste', 'https://dont Eat thepaste.com/feed/'),
    ('The Yellow Cards', 'https://theyellowcardboard.wordpress.com/feed/'),
]

HEADERS = {'User-Agent': 'Mozilla/5.0'}
ok = []
for name, url in blogs:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='replace')
        items = re.findall(r'<item', resp, re.IGNORECASE)
        ok.append((name, url, len(items)))
        sys.stdout.buffer.write(("X %s: %d items\n" % (name, len(items))).encode('utf-8'))
    except Exception as e:
        sys.stdout.buffer.write(("  %s: %s\n" % (name, str(e)[:50])).encode('utf-8'))

sys.stdout.buffer.write(("\n--- Working: %d ---\n" % len(ok)).encode('utf-8'))
for name, url, n in ok:
    sys.stdout.buffer.write(("  %s: %s (%d)\n" % (name, url, n)).encode('utf-8'))