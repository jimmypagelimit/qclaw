"""测试6x6网格"""
import importlib.util, os
from PIL import Image

covers_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

import sqlite3
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute('SELECT album_id FROM albums WHERE cover_image_url IS NOT NULL ORDER BY album_id LIMIT 20')
album_ids = [r[0] for r in cur.fetchall()]
conn.close()

covers = []
for aid in album_ids:
    prefix = str(aid) + '-'
    matched = [f for f in os.listdir(covers_dir)
               if f.startswith(prefix) and f.endswith('.jpg')]
    if matched:
        covers.append(Image.open(os.path.join(covers_dir, matched[0])).convert('RGB'))

print(f'{len(covers)} 张封面，6x6=36格，循环填满')

spec = importlib.util.spec_from_file_location(
    'elegant_grid',
    r'C:\Users\qujt\.qclaw\workspace\tasks\v-project\elegant_grid.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

mod.run(covers=covers,
        output=r'C:\Users\qujt\.qclaw\workspace\elegant_test_6x6.png',
        cols=6, rows=6, seed=42)
