import json
d = json.load(open(r'C:\Users\qujt\.qclaw\workspace\rym_batch_results.json', encoding='utf-8'))
for x in d:
    if 'Twin Fantasy' in x.get('album_name', '') or 'Car Seat Headrest' in x.get('artist', ''):
        print(x.get('album_name'), '|', x.get('artist'), '|', x.get('rym_rating'), '|', 'error' in x)