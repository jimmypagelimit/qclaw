"""测试 RYM CLI 基础搜索功能"""
import sys, json
sys.path.insert(0, r"C:\Users\qujt\.qclaw\workspace\tasks\rym-expert")
from rym_cli import RYMClient

client = RYMClient(headless=False)
result = client.search_album("Twin Fantasy", "Car Seat Headrest")
if result:
    print("=== 搜索结果 ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))
else:
    print("搜索失败")
