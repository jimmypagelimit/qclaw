#!/usr/bin/env python3
"""修复宋冬野《再想想》专辑封面"""
import urllib.request, json, os, sqlite3

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
ALBUM_ID = 600
COVER_PATH = fr'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers\{ALBUM_ID}-宋冬野-再想想.jpg'

print('=== 修复宋冬野《再想想》封面 ===\n')

# 1. 尝试从iTunes API获取封面
print('1. 从iTunes API搜索...')
search_url = 'https://itunes.apple.com/search?term=' + urllib.request.quote('宋冬野 再想想') + '&entity=album&limit=3'
try:
    r = urllib.request.urlopen(search_url, timeout=10)
    data = json.loads(r.read())
    if data.get('resultCount', 0) > 0:
        for res in data.get('results', []):
            name = res.get('collectionName', '')
            artist = res.get('artistName', '')
            artwork = res.get('artworkUrl100', '')
            if '再想想' in name or '宋冬野' in artist:
                print(f'  找到: {name} - {artist}')
                print(f'  Cover URL: {artwork}')
                # 下载封面（用600x600替换100x100）
                cover_url = artwork.replace('100x100', '600x600')
                break
        else:
            print('  未找到匹配结果，尝试第一个结果')
            if data['results']:
                artwork = data['results'][0].get('artworkUrl100', '').replace('100x100', '600x600')
    else:
        print('  iTunes未找到结果')
        cover_url = None
except Exception as e:
    print(f'  iTunes搜索失败: {e}')
    cover_url = None

# 2. 如果iTunes失败，尝试从网易云下载（使用正确的URL格式）
if not cover_url:
    print('\n2. 尝试从网易云下载...')
    # 网易云封面URL格式（需要正确处理）
    pic_id = 109951173491710736
    cover_url = f'https://p2.music.126.net/7RoHUwChyO-K0R5QwJV_GA==/{pic_id}.jpg'

# 3. 下载封面
print(f'\n3. 下载封面...')
os.makedirs(os.path.dirname(COVER_PATH), exist_ok=True)
try:
    req = urllib.request.Request(cover_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as r:
        data = r.read()
        if len(data) > 1000:  # 至少1KB
            with open(COVER_PATH, 'wb') as f:
                f.write(data)
            print(f'  封面已保存: {COVER_PATH}')
            print(f'  文件大小: {len(data)} bytes')
        else:
            print(f'  下载的文件太小: {len(data)} bytes')
except Exception as e:
    print(f'  下载失败: {e}')

# 4. 验证文件
print('\n4. 验证封面文件...')
if os.path.exists(COVER_PATH):
    size = os.path.getsize(COVER_PATH)
    print(f'  文件大小: {size} bytes')
    if size > 10000:  # 至少10KB
        print('  文件大小正常')
    else:
        print('  文件可能损坏')
else:
    print('  文件不存在')

# 5. 更新数据库（如果cover_image_url还没更新）
print('\n5. 更新数据库...')
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute('UPDATE albums SET cover_image_url=? WHERE album_id=?', 
            (f'/covers/{ALBUM_ID}-宋冬野-再想想.jpg', ALBUM_ID))
conn.commit()
print(f'  已更新 cover_image_url: /covers/{ALBUM_ID}-宋冬野-再想想.jpg')
conn.close()

# 6. 导出SQL
print('\n6. 导出 database.sql...')
conn = sqlite3.connect(DB)
with open(r'C:\Users\qujt\.qclaw\workspace\database.sql', 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write(line + '\n')
conn.close()
print('  已导出')

print('\n=== 完成 ===')
print('请重启A项目以查看更新。')
