import urllib.request, json, re, ssl, sys
sys.stdout.reconfigure(encoding="utf-8")
ctx = ssl._create_unverified_context()

url = "https://pitchfork.com/search/?q=teens+of+denial"
req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
})
html = urllib.request.urlopen(req, timeout=20, context=ctx).read().decode("utf-8", errors="replace")
m = re.search(r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\})\s*;', html, re.DOTALL)
if not m:
    print("No PRELOADED_STATE")
    sys.exit(1)
data = json.loads(m.group(1))
search = data.get("transformed", {}).get("search", {})
print("search keys:", list(search.keys()))
items = search.get("items", [])
print(f"items length: {len(items)}")
for i, section in enumerate(items):
    if isinstance(section, list):
        for item in section:
            if isinstance(item, dict):
                print(f"  {item.get('title','')} -> {item.get('url','')}")
    elif isinstance(section, dict):
        print(f"  section dict: {list(section.keys())[:5]}")
