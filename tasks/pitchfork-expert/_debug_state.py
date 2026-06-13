"""Extract __PRELOADED_STATE__ from best-of page and find list data"""
import subprocess, json, re

html = subprocess.run(
    ["curl", "-k", "-s", "-L", "https://pitchfork.com/best/albums/2024/"],
    capture_output=True, text=False, timeout=20
).stdout.decode("utf-8", errors="replace")

# Extract __PRELOADED_STATE__
m = re.search(r'window\.__PRELOADED_STATE__\s*=\s*(\{.+?\})\s*;\s*</script>', html, re.DOTALL)
if m:
    raw = m.group(1)
    print(f"__PRELOADED_STATE__ length: {len(raw)}")
    try:
        state = json.loads(raw)
        print(f"Top-level keys: {list(state.keys())}")
        
        t = state.get("transformed", {})
        print(f"transformed keys: {list(t.keys())[:10]}...")
        
        # Look for list-related data
        for key in list(t.keys())[:20]:
            val = t[key]
            if isinstance(val, dict):
                print(f"  transformed.{key}: dict, keys={list(val.keys())[:10]}")
                # Check for items/albums/reviews inside
                for k2 in list(val.keys())[:10]:
                    v2 = val[k2]
                    if isinstance(v2, list):
                        print(f"    {k2}: list, len={len(v2)}")
                        if v2 and isinstance(v2[0], dict):
                            print(f"      first keys: {list(v2[0].keys())[:10]}")
                    elif isinstance(v2, dict):
                        print(f"    {k2}: dict, keys={list(v2.keys())[:5]}")
            elif isinstance(val, list):
                print(f"  transformed.{key}: list, len={len(val)}")
                if val:
                    print(f"    first type: {type(val[0])}")
                    if isinstance(val[0], dict):
                        print(f"    first keys: {list(val[0].keys())[:10]}")
        
        # Save full state for analysis
        with open(r'C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\data\pf_best_2024_state.json', 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False)
        print("\nFull state saved to pf_best_2024_state.json")
    except json.JSONDecodeError as e:
        print(f"JSON error: {e}")
else:
    # Try truncated JSON parsing
    m2 = re.search(r'window\.__PRELOADED_STATE__\s*=\s*(\{.+)', html, re.DOTALL)
    if m2:
        raw = m2.group(1)
        # Find the last balancing }
        depth = 0
        last_good = 0
        for i, c in enumerate(raw):
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    last_good = i + 1
        trimmed = raw[:last_good]
        print(f"Truncated JSON: {len(raw)} -> {len(trimmed)}")
        try:
            state = json.loads(trimmed)
            print(f"Keys: {list(state.keys())}")
        except:
            print("Still couldn't parse")
