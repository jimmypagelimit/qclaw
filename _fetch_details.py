# -*- coding: utf-8 -*-
"""从 Discogs + MusicBrainz 获取 Porcelain Stars - Rosemary 详情"""
import urllib.request, json, time

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# 1. Discogs release 详情
print("=== Discogs Release 37021197 ===")
try:
    url = "https://api.discogs.com/releases/37021197"
    req = urllib.request.Request(url, headers=headers)
    data = json.loads(urllib.request.urlopen(req, timeout=10).read())
    print("Title:", data.get("title"))
    print("Year:", data.get("year"))
    print("Genres:", data.get("genres", []))
    print("Styles:", data.get("styles", []))
    print("Tracklist:")
    for t in data.get("tracklist", []):
        print("  ", t.get("position"), t.get("title"), t.get("duration"))
    # 封面
    images = data.get("images", [])
    if images:
        print("Cover:", images[0].get("uri"))
except Exception as e:
    print("Discogs 失败:", e)

time.sleep(1)

# 2. MusicBrainz release 详情
print("\n=== MusicBrainz Release ===")
try:
    rid = "6089faed-cf65-440c-bfbf-02061a7b1900"
    url = f"https://musicbrainz.org/ws/2/release/{rid}?inc=recordings+artist-credits+labels&fmt=json"
    req = urllib.request.Request(url, headers={**headers, "User-Agent": "QClawWorkspace/1.0 (jim@example.com)"})
    data = json.loads(urllib.request.urlopen(req, timeout=10).read())
    print("Title:", data.get("title"))
    print("Date:", data.get("date"))
    print("Artist:", data.get("artist-credit", [{}])[0].get("artist", {}).get("name") if data.get("artist-credit") else "N/A")
    print("Tracks:")
    for m in data.get("media", []):
        for t in m.get("tracks", []):
            print("  ", t.get("number"), t.get("title"), t.get("length"))
except Exception as e:
    print("MusicBrainz 失败:", e)

print("\n完成")