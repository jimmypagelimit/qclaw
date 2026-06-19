"""快速检查 LRCLIB"""
import json, urllib.request, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def check(q):
    url = f"https://lrclib.net/api/search?q={urllib.parse.quote(q)}"
    req = urllib.request.Request(url, headers={"User-Agent": "AlbumTracker/1.0"})
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=8).read())
        if r and (r[0].get('syncedLyrics') or r[0].get('plainLyrics')):
            print(f"  HIT: {r[0].get('trackName','')} [{len(r[0].get('syncedLyrics',''))} synced + {len(r[0].get('plainLyrics',''))} plain]")
            return True
        print(f"  MISS: no lyrics")
    except Exception as e:
        print(f"  ERR: {type(e).__name__}")
    return False

import urllib.parse
print("Checking LRCLIB...")
check("Sonic Youth Teen Age Riot")
time.sleep(0.5)
check("Nirvana Smells Like Teen Spirit")
time.sleep(0.5)
check("The Cure The Cure Lost")
time.sleep(0.5)
check("The Twilight Sad That Summer, at Home I Had Become the Invisible")
print("Done")
