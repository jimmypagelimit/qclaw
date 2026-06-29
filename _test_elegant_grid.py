"""测试 elegant_grid.py"""
import sys, os
sys.path.insert(0, r'C:\Users\qujt\.qclaw\workspace\tasks\v-project')

import elegant_grid
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
output = r'C:\Users\qujt\.qclaw\workspace\elegant_test2.png'
elegant_grid.run(db_path=db, output=output, limit=20, seed=42)
