#!/usr/bin/env python3
import urllib.request, json, os, sqlite3, shutil

# 用 iTunes API 查 underscores - U 封面
url = "https://itunes.apple.com/search?term=underscores+U&entity=album&limit=5"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())

print("iTunes results:")
for album in data.get('results', []):
    print(f"  - {album.get('collectionName', 'N/A')} by {album.get('artistName', 'N/A')}")
    print(f"    artwork: {album.get('artworkUrl100', 'N/A')}")
    print()
