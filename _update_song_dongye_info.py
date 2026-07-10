#!/usr/bin/env python3
"""解析网易云音乐API返回的宋冬野《再想想》专辑信息"""
import json, time, datetime, urllib.request, os, sqlite3

# 网易云API返回的数据
api_data = {
    "name": "再想想",
    "id": 384720819,
    "type": "专辑",
    "size": 11,
    "picId": 109951173491710736,
    "company": "Beijing Modern Sky Culture Development Co.,Ltd.",
    "artist": {
        "name": "宋冬野",
        "id": 5073
    },
    "publishTime": 1782662400000  # 毫秒级时间戳
}

# 转换发行时间
publish_ts = api_data["publishTime"] / 1000  # 转为秒
publish_date = datetime.datetime.fromtimestamp(publish_ts).strftime('%Y-%m-%d')
print(f'发行时间: {publish_date}')

# 封面URL
pic_id = api_data["picId"]
cover_url = f"http://p2.music.126.net/7RoHUwChyO-K0R5QwJV_GA==/{pic_id}.jpg"
print(f'封面URL: {cover_url}')

# 下载封面
def download_cover(url, save_path):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            with open(save_path, 'wb') as f:
                f.write(r.read())
        return True
    except Exception as e:
        print(f'下载失败: {e}')
        return False

# 保存封面
album_id = 600  # 数据库中的ID
cover_path = f'C:\\Users\\qujt\\.qclaw\\workspace\\album-tracker\\public\\covers\\{album_id}-宋冬野-再想想.jpg'
os.makedirs(os.path.dirname(cover_path), exist_ok=True)

if download_cover(cover_url, cover_path):
    print(f'封面已下载: {cover_path}')
else:
    print('封面下载失败')

# 获取曲目列表
def get_tracks(album_id_netease):
    url = f'https://music.163.com/api/album/get?id={album_id_netease}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            if data.get('code') == 200:
                songs = data.get('album', {}).get('songs', [])
                return [(s['id'], s['name'], s['duration'] // 1000) for s in songs]
    except Exception as e:
        print(f'获取曲目失败: {e}')
        return []

print('\n获取曲目列表...')
tracks = get_tracks(api_data["id"])
if tracks:
    print(f'✅ 找到 {len(tracks)} 首曲目:')
    for i, (song_id, name, duration) in enumerate(tracks, 1):
        min = duration // 60
        sec = duration % 60
        print(f'  {i:2d}. {name} ({min}:{sec:02d})')
else:
    print('❌ 未找到曲目')

# 更新数据库
DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

# 更新专辑信息
update_sql = """
UPDATE albums SET
    release_company = ?,
    cover_image_url = ?,
    release_date = ?
WHERE album_id = ?
"""

cover_db_url = f'/covers/{album_id}-宋冬野-再想想.jpg'
cur.execute(update_sql, (
    api_data["company"],
    cover_db_url,
    publish_date,
    album_id
))

conn.commit()
print(f'\n✅ 数据库已更新:')
print(f'  发行公司: {api_data["company"]}')
print(f'  封面URL: {cover_db_url}')
print(f'  发行日期: {publish_date}')

conn.close()

# 导出SQL
os.system(f'"{os.path.dirname(os.path.abspath(__file__))}\\tasks\\2026-05-12-long-term-project\\album-tracker\\scripts\\export_sql.py"')
print('\n✅ 已导出 database.sql')
