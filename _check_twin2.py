import sqlite3, json
import urllib.request

# 查数据库 id=56
conn = sqlite3.connect(r'\\10.0.2.4\qemu\原创计划\music')
c = conn.cursor()
c.execute('SELECT album_id, album_name, artist, total_listen_count FROM albums WHERE album_id IN (56, 323)')
print('=== 数据库查询结果 ===')
for r in c.fetchall():
    print(f'  id={r[0]}, name={r[1]}, artist={r[2]}, tc={r[3]}')
conn.close()

# 查 API /api/albums/56 和 /api/albums/323
for aid in [56, 323]:
    try:
        r = urllib.request.urlopen(f'http://localhost:3456/api/albums/{aid}', timeout=3)
        d = json.loads(r.read())
        print(f'\n=== API /api/albums/{aid} ===')
        print(f'  name={d.get("album_name")}, artist={d.get("artist")}, tc={d.get("total_listen_count")}')
    except Exception as e:
        print(f'\n=== API /api/albums/{aid} === 错误: {e}')
