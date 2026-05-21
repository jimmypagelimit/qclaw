import json, os
path = os.path.join(os.path.dirname(__file__), 'memory', 'heartbeat-state.json')
with open(path, 'r', encoding='utf-8') as f:
    d = json.load(f)
d['lastChecks']['rss_music'] = '2026-05-02'
with open(path, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False)
print('ok')
