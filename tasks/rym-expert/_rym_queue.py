"""
RYM 每日补充队列管理脚本
- 导出缺 RYM 评分的专辑到队列文件
- 每次取 4 张标记为 pending
- 完成后标记 done
"""
import sqlite3, json, sys, os, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
QUEUE_FILE = r'C:\Users\qujt\.qclaw\workspace\tasks\rym-expert\_rym_daily_queue.json'

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Get all albums missing RYM rating, ordered by listen count desc
cur.execute("""
SELECT a.album_id, a.artist, a.album_name, 
       COUNT(l.rowid) as listen_count
FROM albums a
LEFT JOIN listen_history l ON a.album_id = l.album_id
WHERE (a.rym_rating IS NULL OR a.rym_rating = 0)
GROUP BY a.album_id
ORDER BY listen_count DESC, a.artist, a.album_name
""")
rows = cur.fetchall()
conn.close()

# Load existing queue state
if os.path.exists(QUEUE_FILE):
    with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
        queue = json.load(f)
else:
    queue = {"done": [], "pending": [], "total": len(rows)}

# Mark already done items
done_ids = set(queue["done"])
# Build new pending list (skip already done)
pending = []
for aid, artist, album, lc in rows:
    if aid not in done_ids:
        pending.append({"id": aid, "artist": artist, "album": album, "listens": lc})

queue["total"] = len(rows)
queue["pending"] = pending[:4]  # next 4
queue["remaining"] = len(pending)

with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
    json.dump(queue, f, ensure_ascii=False, indent=2)

print(f'RYM Queue: {queue["total"]} total, {len(queue["done"])} done, {queue["remaining"]} remaining')
print(f'\nToday batch (4 albums):')
for item in queue["pending"]:
    print(f'  ID {item["id"]}: {item["artist"]} - {item["album"]} [{item["listens"]}x]')
