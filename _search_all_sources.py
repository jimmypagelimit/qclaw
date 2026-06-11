# -*- coding: utf-8 -*-
"""多来源搜索 Porcelain Stars - Rosemary"""
import urllib.request, re, json, time

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# 1. Discogs 公开搜索（无需 token）
print("=== Discogs ===")
try:
    url = "https://api.discogs.com/database/search?q=Porcelain+Stars+Rosemary&type=release&per_page=5"
    req = urllib.request.Request(url, headers=headers)
    data = json.loads(urllib.request.urlopen(req, timeout=10).read())
    results = data.get("results", [])
    print("找到", len(results), "条")
    for r in results[:3]:
        print(" -", r.get("title"), "| id:", r.get("id"), "| year:", r.get("year"))
        if r.get("thumb"):
            print("   thumb:", r["thumb"])
except Exception as e:
    print("Discogs 失败:", e)

# 2. MusicBrainz 搜索（正确 API）
print("\n=== MusicBrainz ===")
try:
    url = "https://musicbrainz.org/ws/2/release/?query=artist:Porcelain+Stars+title:Rosemary&limit=5&fmt=json"
    req = urllib.request.Request(url, headers={**headers, "User-Agent": "QClawWorkspace/1.0 (jim@example.com)"})
    data = json.loads(urllib.request.urlopen(req, timeout=10).read())
    releases = data.get("releases", [])
    print("找到", len(releases), "条")
    for r in releases[:3]:
        print(" -", r.get("title"), "| id:", r.get("id"), "| date:", r.get("date"))
except Exception as e:
    print("MusicBrainz 失败:", e)

# 3. RYM 用 CloakBrowser
print("\n=== RYM (CloakBrowser) ===")
try:
    from cloakbrowser import launch
    browser = launch(headless=False)
    page = browser.new_page()
    page.goto("https://rateyourmusic.com/search?search_type=ra&search_term=Porcelain+Stars+Rosemary")
    time.sleep(20)
    content = page.content()
    with open("rym_search_rosemary2.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("HTML size:", len(content))
    # 找搜索结果
    matches = re.findall(r'href="/release/([^"]+)"[^>]*>([^<]+)<', content)
    print("搜索结果:", matches[:5])
    browser.close()
except Exception as e:
    print("RYM 失败:", e)

print("\n完成")