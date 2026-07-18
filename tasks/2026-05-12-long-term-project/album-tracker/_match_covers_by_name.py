#!/usr/bin/env python3
"""按名称匹配封面，不按 ID"""
import sqlite3, os, re, shutil

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_music_latest.db')
BACKUP = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'covers')
PUBLIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public', 'covers')
os.makedirs(PUBLIC, exist_ok=True)

def normalize(s):
    """标准化用于比较：转小写、去空格、去标点"""
    s = str(s).lower().strip()
    s = re.sub(r'[\s\-_/\\:;,.!?\[\](){}""''「」【】、，。！？；：""''（）]', '', s)
    return s

def artist_from_filename(fname):
    """从文件名提取艺人名和专辑名：{id}-{artist}-{album}.jpg"""
    parts = fname.rsplit('.', 1)[0]  # 去掉扩展名
    # 去掉开头的数字ID
    m = re.match(r'^\d+-(.+)', parts)
    if m:
        return m.group(1)
    return parts

# 读取数据库
conn = sqlite3.connect(DB)
c = conn.cursor()

# 构建数据库索引：normalized_name -> (album_id, artist, album)
db_by_name = {}
c.execute("SELECT album_id, album_name, artist FROM albums")
for aid, aname, artist in c.fetchall():
    key = normalize(artist + aname)
    db_by_name[key] = (aid, artist, aname)

# 遍历备份目录
backup_files = [f for f in os.listdir(BACKUP) if f.endswith(('.jpg', '.png', '.jpeg'))]
matched = 0
not_found = []
wrong_name = []
public_existing = set(os.listdir(PUBLIC))

for fname in sorted(backup_files):
    # 提取文件名中的艺人+专辑名（去掉ID前缀）
    name_part = artist_from_filename(fname)
    key = normalize(name_part)
    
    if key in db_by_name:
        aid, db_artist, db_album = db_by_name[key]
        
        # 用 album_id 命名新文件
        ext = fname.rsplit('.', 1)[1]
        new_fname = f"{aid}-{db_artist}-{db_album}.{ext}"
        # 文件名安全化
        safe_new = re.sub(r'[\\/:*?"<>|,]', '_', new_fname)
        
        src = os.path.join(BACKUP, fname)
        dst = os.path.join(PUBLIC, safe_new)
        
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            print(f"  ✅ {aid} | {db_artist} - {db_album} → {safe_new}")
        else:
            print(f"  ⏭ {aid} | {db_artist} - {db_album} (已存在)")
        
        # 更新数据库
        new_url = f"/covers/{safe_new}"
        c.execute("UPDATE albums SET cover_image_url = ? WHERE album_id = ?", (new_url, aid))
        matched += 1
    else:
        # 尝试匹配部分：去掉可能的分隔符
        # 有时文件名用 - 分隔 artist 和 album，尝试拆分
        name_clean = name_part.replace('_', ' ')
        # 找第一个 - 前后
        parts = name_clean.split('-', 1)
        if len(parts) == 2:
            key2 = normalize(parts[0] + parts[1])
            if key2 in db_by_name:
                aid, db_artist, db_album = db_by_name[key2]
                ext = fname.rsplit('.', 1)[1]
                safe_new = re.sub(r'[\\/:*?"<>|,]', '_', f"{aid}-{db_artist}-{db_album}.{ext}")
                src = os.path.join(BACKUP, fname)
                dst = os.path.join(PUBLIC, safe_new)
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)
                new_url = f"/covers/{safe_new}"
                c.execute("UPDATE albums SET cover_image_url = ? WHERE album_id = ?", (new_url, aid))
                matched += 1
                print(f"  ✅(模糊) {aid} | {db_artist} - {db_album} → {fname}")
                continue
        not_found.append((fname, name_part))

conn.commit()
conn.close()

print(f"\n共匹配: {matched}/{len(backup_files)}")
if not_found:
    print(f"无法匹配: {len(not_found)}")
    for fname, name in not_found[:20]:
        print(f"  {fname} → 解析名: {name}")