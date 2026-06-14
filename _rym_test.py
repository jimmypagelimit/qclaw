# Quick check: RYM access test
import urllib.request, sys
url = 'https://rateyourmusic.com'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    print(f"Status: {resp.status}")
    body = resp.read()[:500]
    print(body.decode('utf-8', errors='replace'))
except Exception as e:
    print(f"Error: {e}")
