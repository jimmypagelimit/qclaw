#!/usr/bin/env python3
"""
Phase2 轻量版：只处理 10 张，输出到 UTF-8 文件
"""
import sqlite3
import urllib.request
import urllib.parse
import json
import time
import ssl

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

DB_PATH = 'C:/Users/qujt/.qclaw/workspace/_music_latest.db'
REPORT = 'C:/Users/qujt/.qclaw/workspace/_phase2_light_report.txt'

def search_mb(artist, album):
    query = f'artist:"{artist}" AND releasegroup:"{album}"'
    url = f"https://musicbrainz.org/ws/2/release-group/?query={urllib.parse.quote(query)}&limit=3&fmt=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'album-tracker/1.0'})
        resp = urllib.request.urlopen(req, timeout=15, context=SSL_CTX)
        return json.loads(resp.read())
    except:
        return None

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA journal_mode=WAL')
    c = conn.cursor()

    c.execute("""SELECT album_id, album_name, artist 
        FROM albums 
        WHERE release_mbid IS NULL OR release_mbid = ''
        ORDER BY artist, album_name
        LIMIT 10 OFFSET ?
    """, (idx*10,))
    rows = c.fetchall()

    lines = [f"Phase2 轻量版：处理 {len(rows)} 张\n" + "=" * 70 + "\n"]

    updated = 0
    for idx, (aid, aname, artist) in enumerate(rows, 1):
        line = f"[{idx}/10] {artist} - {aname}"
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
        else:
            fail = f"  [FAIL] 无结果"
            lines.append(fail)
            print(fail)

        time.sleep(1.5)

    conn.commit()

    # 统计
    c.execute("SELECT COUNT(*) FROM albums WHERE release_mbid IS NOT NULL AND release_mbid != ''")
    has_mbid = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM albums")
    total = c.fetchone()[0]

    lines.append("")
    lines.append("=" * 70)
    lines.append(f"本轮新增: {updated} 条")
    lines.append(f"覆盖率: {has_mbid}/{total} = {has_mbid/total*100:.1f}%")

    # 写报告
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"\n报告: {REPORT}")
    print(f"新增: {updated} 条")
    print(f"覆盖率: {has_mbid}/{total} = {has_mbid/total*100:.1f}%")

    conn.close()

if __name__ == '__main__':
    main()
