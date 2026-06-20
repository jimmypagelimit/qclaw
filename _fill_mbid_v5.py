#!/usr/bin/env python3
"""
MBID 补充脚本 v5（保守版 + GBK 修复）
- 只处理华语主流专辑
- 输出候选到 UTF-8 文件，控制台只用 ASCII
- 不自动写入数据库
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

MAINSTREAM = [
    '罗大佑', '张雨生', '张悬', '吴青峰', '林忆莲',
    '王杰', '陈绮贞', '魏如萱', '周华健', '郑智化',
    '高枫', '许景淳', '达明一派', '郁冬', '谢苒'
]

def search_mb(artist, album):
    query = f'artist:"{artist}" AND releasegroup:"{album}"'
    url = f"https://musicbrainz.org/ws/2/release-group/?query={urllib.parse.quote(query)}&limit=5&fmt=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'album-tracker/1.0 (test)'})
        resp = urllib.request.urlopen(req, timeout=15, context=SSL_CTX)
        return json.loads(resp.read())
    except Exception as e:
        return None

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA journal_mode=WAL')
    c = conn.cursor()

    placeholders = ','.join(['?'] * len(MAINSTREAM))
    c.execute(f"""
        SELECT album_id, album_name, artist
        FROM albums
        WHERE (release_mbid IS NULL OR release_mbid = '')
          AND artist IN ({placeholders})
        ORDER BY artist, album_name
    """, MAINSTREAM)

    rows = c.fetchall()
    print(f"找到 {len(rows)} 张主流艺人专辑待查 MBID")
    print("=" * 70)

    results = []
    out_lines = []

    for idx, (aid, aname, artist) in enumerate(rows, 1):
        line = f"[{idx}/{len(rows)}] {artist} - {aname}"
        print(line)
        out_lines.append(line)

        data = search_mb(artist, aname)
        if not data or 'release-groups' not in data or not data['release-groups']:
            msg = f"  [FAIL] 无搜索结果"
            print(msg)
            out_lines.append(msg)
            results.append((aid, aname, artist, None, '无结果'))
            time.sleep(1.5)
            continue

        best = data['release-groups'][0]
        score = int(best.get('score', 0))
        rgid = best.get('id', '')
        title = best.get('title', '')

        # 显示前3候选
        for i, rg in enumerate(data['release-groups'][:3]):
            cand_line = f"  {i+1}. [{rg.get('score', 0)}分] {rg.get('title', '')}  (MBID: {rg.get('id', '')})"
            print(cand_line)
            out_lines.append(cand_line)

        if score >= 75:
            ok_line = f"  -> 选中: {title} [{score}分]  MBID={rgid}"
            print(ok_line)
            out_lines.append(ok_line)
            results.append((aid, aname, artist, rgid, f"{score}分"))
        else:
            skip_line = f"  -> 分数过低，跳过 [{score}分]"
            print(skip_line)
            out_lines.append(skip_line)
            results.append((aid, aname, artist, None, f"低分-{score}"))

        time.sleep(1.5)

    # 写 UTF-8 报告
    report_path = 'C:/Users/qujt/.qclaw/workspace/_mbid_v5_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("MBID 候选报告（保守版 v5）\n")
        f.write("=" * 70 + "\n\n")
        for line in out_lines:
            f.write(line + "\n")

        f.write("\n" + "=" * 70 + "\n")
        auto_ok = [r for r in results if r[3]]
        f.write(f"自动匹配成功: {len(auto_ok)} 张\n")
        f.write(f"失败/低分: {len(results) - len(auto_ok)} 张\n\n")

        if auto_ok:
            f.write("--- 候选 SQL（请检查后执行）---\n")
            for r in auto_ok:
                sql = f"UPDATE albums SET release_mbid = '{r[3]}' WHERE album_id = {r[0]}; -- {r[2]} - {r[1]}"
                f.write(sql + "\n")

    print(f"\n报告已保存: {report_path}")
    print(f"自动匹配: {len([r for r in results if r[3]])} 张")
    print(f"请检查报告后决定是否写入数据库")

    conn.close()

if __name__ == '__main__':
    main()
