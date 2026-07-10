#!/usr/bin/env python3
"""获取和更新宋冬野《再想想》专辑信息"""
import json, time, datetime, urllib.request, os, sqlite3, sys

# 网易云专辑ID
ALBUM_ID_NETEASE = 384720819
ALBUM_ID_DB = 600  # 数据库中的ID

# 1. 获取专辑详情
def get_album_info(album_id):
    url = f'https://music.163.com/api/album/get?id={album_id}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            if data.get('code') == 200:
                return data.get('album')
    except Exception as e:
        print(f'获取专辑信息失败: {e}')
        return None

# 2. 下载封面
def download_cover(pic_id, save_path):
    # 网易云封面URL格式
    url = f'https://p2.music.126.net/7RoHUwChyO-K0R5QwJV_GA==/{pic_id}.jpg'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            with open(save_path, 'wb') as f:
                f.write(r.read())
        return True
    except Exception as e:
        print(f'下载封面失败: {e}')
        return False

# 3. 主流程
print('=== 获取宋冬野《再想想》专辑信息 ===\n')

# 获取专辑信息
album_info = get_album_info(ALBUM_ID_NETEASE)
if not album_info:
    print('无法获取专辑信息')
    sys.exit(1)

# 解析信息
album_name = album_info.get('name', '')
artist_name = album_info.get('artist', {}).get('name', '')
company = album_info.get('company', '')
publish_time = album_info.get('publishTime', 0)
pic_id = album_info.get('picId', 0)
songs = album_info.get('songs', [])

# 转换发行时间
if publish_time > 0:
    publish_date = datetime.datetime.fromtimestamp(publish_time / 1000).strftime('%Y-%m-%d')
else:
    publish_date = None

print(f'专辑名称: {album_name}')
print(f'艺人: {artist_name}')
print(f'发行公司: {company}')
print(f'发行日期: {publish_date}')
print(f'曲目数量: {len(songs)}')

# 下载封面
cover_filename = f'{ALBUM_ID_DB}-宋冬野-再想想.jpg'
cover_path = fr'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers\{cover_filename}'
os.makedirs(os.path.dirname(cover_path), exist_ok=True)

print(f'\n下载封面...')
if download_cover(pic_id, cover_path):
    print(f'封面已保存: {cover_path}')
    cover_db_url = f'/covers/{cover_filename}'
else:
    print('封面下载失败')
    cover_db_url = None

# 显示曲目列表
if songs:
    print(f'\n曲目列表 ({len(songs)} 首):')
    for i, song in enumerate(songs, 1):
        name = song.get('name', '')
        duration_ms = song.get('duration', 0)
        duration_s = duration_ms // 1000
        min = duration_s // 60
        sec = duration_s % 60
        print(f'  {i:2d}. {name} ({min}:{sec:02d})')

# 更新数据库
DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

update_sql = """
UPDATE albums SET
    release_company = ?,
    cover_image_url = ?,
    release_date = ?
WHERE album_id = ?
"""

cur.execute(update_sql, (
    company,
    cover_db_url,
    publish_date,
    ALBUM_ID_DB
))

conn.commit()
print(f'\n数据库已更新:')
print(f'  发行公司: {company}')
print(f'  封面URL: {cover_db_url}')
print(f'  发行日期: {publish_date}')

conn.close()

# 导出SQL
print(f'\n导出 database.sql...')
export_script = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\scripts\export_sql.py'
if os.path.exists(export_script):
    os.system(f'"{sys.executable}" "{export_script}"')
    print('已导出 database.sql')
else:
    print(f'导出脚本不存在: {export_script}')

print('\n=== 完成 ===')
print('请重启A项目以查看更新后的数据。')
