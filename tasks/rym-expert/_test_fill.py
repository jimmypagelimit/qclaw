"""测试回填前5张"""
import sys
sys.path.insert(0, r"C:\Users\qujt\.qclaw\workspace\tasks\rym-expert")
from rym_db_bridge import fill_database

fill_database(limit=5)
