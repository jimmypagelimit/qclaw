#!/usr/bin/env python3
"""更新宋冬野《再想想》专辑信息"""
import sqlite3, os, urllib.request

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
ALBUM_ID = 600

# 从之前API返回的数据
COMPANY = "Beijing Modern Sky Culture Development Co.,Ltd."  # 摩登天空
RELEASE_YEAR = 2026  # 从时间戳转换：2026-06-29
COVER_FILENAME = f"{ALBUM_ID}-宋冬野-再想想.jpg"
COVER_URL = "http://p2.music.126.net/7RoHUwChyO-K0R5QwJV_GA==/109951173491710736.jpg"

# 1. 更新数据库
conn = sqlite3.connect(DB)
cur = conn.cursor()

update_sql = """
UPDATE albums SET
    release_company = ?,
    release_year = ?,
    cover_image_url = ?
WHERE album_id = ?
"""

cur.execute(update_sql, (
    COMPANY,
    RELEASE_YEAR,
    f'/covers/{COVER_FILENAME}',
    ALBUM_ID
))

conn.commit()
print(f"已更新专辑信息:")
print(f"  发行公司: {COMPANY}")
print(f"  发行年份: {RELEASE_YEAR}")
print(f"  封面URL: /covers/{COVER_FILENAME}")

conn.close()

# 2. 下载封面
cover_path = fr"C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers\{COVER_FILENAME}"
os.makedirs(os.path.dirname(cover_path), exist_ok=True)

print(f"\n下载封面...")
try:
    req = urllib.request.Request(COVER_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as r:
        with open(cover_path, 'wb') as f:
            f.write(r.read())
    print(f"封面已保存: {cover_path}")
except Exception as e:
    print(f"下载失败: {e}")

# 3. 导出SQL
print(f"\n导出 database.sql...")
try:
    # 尝试调用export_sql.py脚本
    export_script = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\scripts\export_sql.py"
    if os.path.exists(export_script):
        os.system(f'"{os.path.dirname(os.path.abspath(__file__))}\\tasks\\2026-05-12-long-term-project\\album-tracker\\scripts\\export_sql.py"')
        print("已导出 database.sql")
    else:
        print(f"导出脚本不存在: {export_script}")
except Exception as e:
    print(f"导出失败: {e}")

print(f"\n完成！请重启A项目查看更新。")
