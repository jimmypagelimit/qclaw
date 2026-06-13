"""Debug: check what Pitchfork best-of pages actually contain"""
import subprocess, json, re

html = subprocess.run(
    ["curl", "-k", "-s", "-L", "https://pitchfork.com/best/albums/2024/"],
    capture_output=True, text=False, timeout=20
).stdout.decode("utf-8", errors="replace")

# Check size
print(f"HTML size: {len(html)} bytes")

# Check for __NEXT_DATA__
m = re.search(r'<script id="__NEXT_DATA__".*?>(.*?)</script>', html, re.DOTALL)
if m:
    print(f"__NEXT_DATA__ found: {len(m.group(1))} chars")
    try:
        data = json.loads(m.group(1))
        print(f"Keys top-level: {list(data.keys())}")
        pp = data.get("props", {}).get("pageProps", {})
        print(f"pageProps keys: {list(pp.keys())[:10]}...")
        # Search for items containing "score"
        for key in pp:
            val = pp[key]
            if isinstance(val, list):
                print(f"  pageProps.{key} list: len={len(val)}, first type={type(val[0]) if val else 'empty'}")
                if val and isinstance(val[0], dict):
                    print(f"    first keys: {list(val[0].keys())[:10]}")
                    for k in val[0]:
                        v = val[0][k]
                        if isinstance(v, (int, float, str, bool)):
                            print(f"    {k}: {repr(v)[:100]}")
            elif isinstance(val, dict):
                print(f"  pageProps.{key} dict: keys={list(val.keys())[:10]}")
    except json.JSONDecodeError as e:
        print(f"  JSON error: {e}")
else:
    print("__NEXT_DATA__ NOT found")
    # Check for other data
    m2 = re.search(r'__PRELOADED_STATE__', html)
    print(f"__PRELOADED_STATE__: {'found' if m2 else 'NOT found'}")
    
    # Look for list items
    items = re.findall(r'reviews/albums/[^"]+', html)
    print(f"Review links found: {len(set(items))}")
    
    # Look for any JSON data blocks
    scripts = re.findall(r'<script type="application/json".*?>(.*?)</script>', html, re.DOTALL)
    print(f"application/json scripts: {len(scripts)}")
    for i, s in enumerate(scripts):
        print(f"  Script {i}: {len(s)} chars")
        try:
            d = json.loads(s)
            if isinstance(d, list):
                print(f"    Is list, len={len(d)}")
                if d and isinstance(d[0], dict):
                    print(f"    first keys: {list(d[0].keys())[:10]}")
            elif isinstance(d, dict):
                print(f"    Is dict, keys={list(d.keys())[:10]}")
                # Check for nested content
                for k in list(d.keys())[:5]:
                    v = d[k]
                    if isinstance(v, list):
                        print(f"      {k}: list len={len(v)}")
                    elif isinstance(v, dict):
                        print(f"      {k}: dict keys={list(v.keys())[:5]}")
        except json.JSONDecodeError:
            print(f"    (not valid JSON)")

# Save for manual inspection
with open(r'C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\data\pf_best_2024_debug.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("HTML saved to pf_best_2024_debug.html")
