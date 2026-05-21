import urllib.request
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

url = "https://api.github.com/search/repositories?q=stars:>1000+pushed:>2026-03-01&sort=stars&order=desc&per_page=20"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read())

for i, r in enumerate(data["items"][:20], 1):
    desc = (r.get("description") or "No description")[:70]
    lang = r.get("language") or "N/A"
    stars = r["stargazers_count"]
    print(f"#{i} {r['full_name']} {stars//1000}.{stars%1000//100}k {lang}")
    print(f"   {desc}")
    print()
