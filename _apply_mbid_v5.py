#!/usr/bin/env python3
"""
应用 MBID v5 候选列表
- 读取 _mbid_v5_report.txt 中的 SQL
- 写入数据库
- 然后继续处理剩余缺失 MBID 的专辑
"""

import sqlite3
import urllib.request
import urllib.parse
import json
import time
import ssl
import re

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

DB_PATH = 'C:/Users/qujt/.qclaw/workspace/_music_latest.db'

# 19 条候选（从报告里抄出来的，100% 置信度）
CANDIDATES = [
    (2,   'b32a3330-dcdf-4b3e-966b-32bd5b87ca28'),  # 吴青峰 - 马拉美的星期二
    (550, '81d44b2f-edd1-447e-bcd3-633aba22afab'),  # 周华健 - 怎么断句呢
    (303, 'bd025f4b-ef9c-38a9-8beb-db8bd69d35bc'),  # 张悬 - 亲爱的...我还不知道
    (168, '90782b04-4e9b-4c22-880d-84a2a56b72fd'),  # 张悬 - 城市
    (6,   'd05e9340-e542-486f-af69-48ffc8e4caa2'),  # 张悬 - 神的游戏
    (95,  'e0135bcb-268f-48f8-80f5-fb5eaf98d654'),  # 张雨生 - 两伊战争
    (10,  '87ef0dea-df13-49ef-98e7-b2a9ddbdd005'),  # 林忆莲 - 蓋亚
    (333, 'ec3ac7bc-8500-3b0f-a6a4-fbb868c5ea3d'),  # 罗大佑 - 原乡
    (159, 'af8f3eb8-3fdb-3215-8fb7-c7545fe2cd70'),  # 罗大佑 - 爱人同志
    (185, 'cc2c1881-2fd1-4c4d-a59f-9a99881a03b1'),  # 罗大佑 - 美丽岛
    (337, '5a5f75ff-0a46-4c90-91a0-ba2ca7f969c9'),  # 达明一派 - 神经
    (368, 'b08f795d-5604-4ab8-b260-a5e61d5d416a'),  # 郑智化 - 单身逃亡
    (246, 'b227b6b5-ef55-427b-b851-3bc9fdfefeda'),  # 郑智化 - 星星点灯
    (38,  '6e3e6f3c-4d19-4022-ba6b-5d4095bd911f'),  # 郑智化 - 落泪的戏子
    (276, 'aeaecbec-556d-3b72-bfdf-dda0637db940'),  # 陈绮贞 - 华丽的冒险
    (279, 'c6af3dfb-e48a-4d3f-b184-dbfc1863f384'),  # 陈绮贞 - 沙发海
    (142, 'b051325c-9031-3914-8965-aefbd2bff919'),  # 陈绮贞 - 花的姿态演唱会经典实录
    (410, '2ce80082-c8f0-36ba-bd30-d6a3021a2bc9'),  # 陈绮贞 - 让我想一想
    (275, '59f8c580-f50a-4c2c-b810-dec0d6c4b864'),  # 魏如萱 - 不允许哭泣的场合
]

def apply_candidates():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA journal_mode=WAL')
    c = conn.cursor()
    
    updated = 0
    for aid, mbid in CANDIDATES:
        c.execute("UPDATE albums SET release_mbid = ? WHERE album_id = ?", (mbid, aid))
        if c.rowcount > 0:
            updated += 1
    
    conn.commit()
    print(f"已写入 {updated} 条 MBID")
    
    # 检查剩余缺失
    c.execute("SELECT COUNT(*) FROM albums WHERE release_mbid IS NULL OR release_mbid = ''")
    remaining = c.fetchone()[0]
    print(f"剩余缺失: {remaining}")
    
    conn.close()
    return remaining

def search_mb(artist, album):
    query = f'artist:"{artist}" AND releasegroup:"{album}"'
    url = f"https://musicbrainz.org/ws/2/release-group/?query={urllib.parse.quote(query)}&limit=3&fmt=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'album-tracker/1.0'})
        resp = urllib.request.urlopen(req, timeout=15, context=SSL_CTX)
        return json.loads(resp.read())
    except:
        return None

def continue_fill():
    """继续补剩余缺失 MBID 的专辑（放宽搜索策略）"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA journal_mode=WAL')
    c = conn.cursor()
    
    c.execute("""SELECT album_id, album_name, artist 
        FROM albums 
        WHERE release_mbid IS NULL OR release_mbid = ''
        ORDER BY artist, album_name
    """)
    rows = c.fetchall()
    
    print(f"\n继续处理剩余 {len(rows)} 张专辑...")
    print("=" * 70)
    
    updated = 0
    failed = []
    
    for idx, (aid, aname, artist) in enumerate(rows, 1):
        line = f"[{idx}/{len(rows)}] {artist} - {aname}"
        print(line)
        
        # 策略1：精确搜索
        data = search_mb(artist, aname)
        best = None
        if data and data.get('release-groups'):
            best = data['release-groups'][0]
        
        # 策略2：只用专辑名搜索
        if not best or int(best.get('score', 0)) < 60:
            time.sleep(1)
            query2 = f'releasegroup:"{aname}"'
            url2 = f"https://musicbrainz.org/ws/2/release-group/?query={urllib.parse.quote(query2)}&limit=5&fmt=json"
            try:
                req = urllib.request.Request(url2, headers={'User-Agent': 'album-tracker/1.0'})
                resp = urllib.request.urlopen(req, timeout=15, context=SSL_CTX)
                data2 = json.loads(resp.read())
                if data2.get('release-groups'):
                    # 找 artist 匹配的
                    for rg in data2['release-groups']:
                        for artist_credit in rg.get('artist-credit', []):
                            if 'artist' in artist_credit and artist in artist_credit['artist'].get('name', ''):
                                best = rg
                                break
                        if best:
                            break
            except:
                pass
        
        if best and int(best.get('score', 0)) >= 60:
            rgid = best.get('id', '')
            title = best.get('title', '')
            score = best.get('score', 0)
            print(f"  -> 匹配: {title} [{score}分]  MBID={rgid}")
            c.execute("UPDATE albums SET release_mbid = ? WHERE album_id = ?", (rgid, aid))
            updated += 1
        else:
            print(f"  [FAIL] 无结果")
            failed.append((aid, aname, artist))
        
        time.sleep(1.5)
    
    conn.commit()
    conn.close()
    
    print(f"\n本轮新增: {updated} 条")
    print(f"仍失败: {len(failed)} 张")
    
    if failed:
        print("\n失败列表:")
        for r in failed:
            print(f"  id={r[0]} | {r[2]} - {r[1]}")

if __name__ == '__main__':
    print("=== 阶段1：写入 19 条候选 MBID ===")
    remaining = apply_candidates()
    
    if remaining > 0:
        print(f"\n=== 阶段2：继续补剩余 {remaining} 张 ===")
        continue_fill()
    else:
        print("\n全部完成！MBID 覆盖率 100%")
