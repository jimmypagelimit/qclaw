#!/usr/bin/env python3
"""
Phase2 完整版：处理全部剩余缺失 MBID 的专辑
- 每 5 张写一次进度到文件
- 超时保护：单张搜索限 10 秒
- 输出 UTF-8 报告
"""

import sqlite3
import urllib.request
import urllib.parse
import json
import time
import ssl
import signal

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

DB_PATH = 'C:/Users/qujt/.qclaw/workspace/_music_latest.db'
REPORT = 'C:/Users/qujt/.qclaw/workspace/_phase2_full_report.txt'

def search_mb(artist, album):
    query = f'artist:"{artist}" AND releasegroup:"{album}"'
    url = f"https://musicbrainz.org/ws/2/release-group/?query={urllib.parse.quote(query)}&limit=3&fmt=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'album-tracker/1.0'})
        resp = urllib.request.urlopen(req, timeout=10, context=SSL_CTX)
        return json.loads(resp.read())
    except Exception as e:
        return None

def write_progress(lines):
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

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

    lines = [f"Phase2 完整版：处理 {len(rows)} 张\n" + "=" * 70 + "\n"]
    updated = 0
    failed = []

    for idx, (aid, aname, artist) in enumerate(rows, 1):
        line = f"[{idx}/{len(rows)}] {artist} - {aname}"
        lines.append(line)
        print(line)

        data = search_mb(artist, aname)
        if data and data.get('release-groups'):
            best = data['release-groups'][0]
            score = int(best.get('score', 0))
            if score >= 70:
                rgid = best.get('id', '')
                title = best.get('title', '')
                ok = f"  -> 匹配: {title} [{score}分]  MBID={rgid}"
                lines.append(ok)
                print(ok)
                c.execute("UPDATE albums SET release_mbid = ? WHERE album_id = ?", (rgid, aid))
                updated += 1
            else:
                skip = f"  -> 分数过低 [{score}分]"
                lines.append(skip)
                print(skip)
                failed.append((aid, aname, artist, f"低分-{score}"))
        else:
            fail = f"  [FAIL] 无结果"
            lines.append(fail)
            print(fail)
            failed.append((aid, aname, artist, '无结果'))

        # 每 5 张写一次进度
        if idx % 5 == 0:
            write_progress(lines + [f"\n进度: {idx}/{len(rows)}, 已匹配: {updated}"])
            print(f"  [进度] 已处理 {idx}/{len(rows)}")

        time.sleep(1.2)

    conn.commit()

    # 最终统计
    c.execute("SELECT COUNT(*) FROM albums WHERE release_mbid IS NOT NULL AND release_mbid != ''")
    has_mbid = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM albums")
    total = c.fetchone()[0]

    lines.append("")
    lines.append("=" * 70)
    lines.append(f"Phase2 新增: {updated} 条")
    lines.append(f"仍失败: {len(failed)} 张")
    lines.append(f"最终覆盖率: {has_mbid}/{total} = {has_mbid/total*100:.1f}%")
    lines.append("")
    if failed:
        lines.append("失败列表（需手动处理）:")
        for r in failed:
            lines.append(f"  id={r[0]} | {r[2]} - {r[1]}  ({r[3]})")

    write_progress(lines)

    print(f"\n报告已保存: {REPORT}")
    print(f"Phase2 新增: {updated} 条")
    print(f"最终覆盖率: {has_mbid}/{total} = {has_mbid/total*100:.1f}%")

    conn.close()

if __name__ == '__main__':
    main()
