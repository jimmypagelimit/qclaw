import json, os
hist_path = r'C:\Users\qujt\.qclaw\workspace\_translate_history.json'
if os.path.exists(hist_path):
    with open(hist_path, 'r', encoding='utf-8') as f:
        hist = json.load(f)
    print(f"History entries: {len(hist.get('translated', []))}")
    for h in hist.get('translated', [])[:10]:
        print(f"  {h}")
else:
    print("No history file")
