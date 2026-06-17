import os

base = r'C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\docs\zh'
for slot in ['indie', 'metal', 'folk']:
    path = os.path.join(base, slot)
    if os.path.exists(path):
        files = sorted(os.listdir(path))
        print(f'{slot}: {len(files)} files')
        for f in files[-3:]:
            print(f'  {f}')
    else:
        print(f'{slot}: NOT FOUND')
