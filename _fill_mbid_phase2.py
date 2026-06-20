#!/usr/bin/env python3
"""
Phase2: 补充剩余缺失 MBID（37张）
策略：
  1. 精确搜索 artist + album
  2. 模糊搜索（去掉标点）
  3. 只更新置信度高的（score >= 70）
输出到 UTF-8 文件
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
REPORT = 'C:/Users/qujt/.qclaw/workspace/_mbid_phase2_report.txt'

def search_mb(query):
    url = f"https://musicbrainz.org/ws/2/release-group/?query={urllib.parse.quote(query)}&limit=5&fmt=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'album-tracker/1.0'})
        resp = urllib.request.urlopen(req, timeout=15, context=SSL_CTX)
        return json.loads(resp.read())
    except Exception as e:
        return None

def clean_name(s):
    """去掉标点，简化搜索"""
    s = re.sub(r'[^\w\s]', ' ', s)  # 去掉标点
    s = re.sub(r'\s+', ' ', s).strip()  # 合并空格
    return s

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA journal_mode=WAL')
    c = conn.cursor()

    c.execute("""SELECT album_id, album_name, artist 
        FROM albums 
        WHERE release_mbid IS NULL OR release_mbid = ''
        ORDER BY artist, album_name
    """)
    rows = c.fetchall()

    report_lines = []
    report_lines.append(f"Phase2 MBID 补充报告（{len(rows)} 张待处理）")
    report_lines.append("=" * 70)
    report_lines.append("")

    updated = 0
    failed = []

    for idx, (aid, aname, artist) in enumerate(rows, 1):
        line = f"[{idx}/{len(rows)}] {artist} - {aname}"
        report_lines.append(line)
        print(line)

        # 策略1：精确搜索
        q1 = f'artist:"{artist}" AND releasegroup:"{aname}"'
        data = search_mb(q1)
        best = None
        if data and data.get('release-groups'):
            best = data['release-groups'][0]

        # 策略2：模糊搜索（去掉标点）
        if not best or int(best.get('score', 0)) < 70:
            time.sleep(1)
            q2 = f'releasegroup:"{clean_name(aname)}"'
            data2 = search_mb(q2)
            if data2 and data2.get('release-groups'):
                # 找 artist 匹配的
                for rg in data2['release-groups']:
                    for ac in rg.get('artist-credit', []):
                        if 'artist' in ac and artist in ac['artist'].get('name', ''):
                            best = rg
                            break
                    if best:
                        break

        if best and int(best.get('score', 0)) >= 70:
            rgid = best.get('id', '')
            title = best.get('title', '')
            score = best.get('score', 0)
            ok_line = f"  -> 匹配: {title} [{score}分]  MBID={rgid}"
            report_lines.append(ok_line)
            print(ok_line)

            c.execute("UPDATE albums SET release_mbid = ? WHERE album_id = ?", (rgid, aid))
            updated += 1
        else:
            fail_line = f"  [FAIL] 无结果 (artist={artist}, album={aname})"
            report_lines.append(fail_line)
            print(fail_line)
            failed.append((aid, aname, artist))

        time.sleep(1.2)  # MusicBrainz 限速

    conn.commit()

    # 最终统计
    c.execute("SELECT COUNT(*) FROM albums WHERE release_mbid IS NOT NULL AND release_mbid != ''")
    has_mbid = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM albums")
    total = c.fetchone()[0]

    report_lines.append("")
    report_lines.append("=" * 70)
    report_lines.append(f"Phase2 新增: {updated} 条")
    report_lines.append(f"仍失败: {len(failed)} 张")
    report_lines.append(f"最终覆盖率: {has_mbid}/{total} = {has_mbid/total*100:.1f}%")
    report_lines.append("")
    if failed:
        report_lines.append("失败列表（需手动处理）:")
        for r in failed:
            report_lines.append(f"  id={r[0]} | {r[2]} - {r[1]}")

    # 写报告
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print(f"\n报告已保存: {REPORT}")
    print(f"Phase2 新增: {updated} 条")
    print(f"最终覆盖率: {has_mbid}/{total} = {has_mbid/total*100:.1f}%")

    conn.close()

if __name__ == '__main__':
    main()
