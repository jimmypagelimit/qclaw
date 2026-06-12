import json, os
d = r'C:\Users\qujt\.qclaw\workspace\tasks\rym-expert\data\artists'
for f in ['rem_discog.json','pink-floyd_discog.json','sufjan-stevens_discog.json','big-thief_discog.json','supertramp_discog.json','david-bowie_discog.json']:
    p = os.path.join(d, f)
    with open(p, encoding='utf-8') as fp:
        data = json.load(fp)
    name = data.get('name','?')
    cnt = data.get('total_releases', 0)
    genres = data.get('genres', [])
    print(f'{name}: {cnt} releases, genres={genres}')
