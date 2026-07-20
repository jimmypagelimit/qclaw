#!/usr/bin/env python3
"""
RYM Charts 抓取工具（Selenium + Firefox profile）
比 CloakBrowser 快 10 倍，秒级完成

用法:
    python _rym_charts_selenium.py [--url URL] [--output FILE]

依赖:
    - geckodriver 0.37.0+（/usr/local/bin/geckodriver）
    - selenium（pip install selenium）
    - Firefox ESR profile（3pdxe3s8.default-esr）

原理:
    复用 Firefox 已有 profile（含 cf_clearance cookie），
    跳过 Cloudflare 验证，直接访问 RYM 页面。

    cf_clearance 绑定到签发时的 TLS 指纹，
    不能跨工具复用（curl/requests 都会403）。
    唯一可行方案：复用同一个浏览器上下文。
"""

import sys
import json
import re
import argparse
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# Firefox profile 路径
FIREFOX_PROFILE = "/root/.mozilla/firefox/3pdxe3s8.default-esr"

# 默认 Charts URL
CHARTS_URL = "https://rateyourmusic.com/charts/top/album/all-time/"


def extract_charts(html):
    """从 RYM Charts 页面提取专辑数据"""
    # 专辑名+艺人 (从封面图的 alt 属性: "Artist - Album, Cover art")
    alts = re.findall(r'alt="([^"]* - [^"]*)"', html)

    # 评分 (每张专辑有2个评分，取第一个)
    ratings = re.findall(
        r'class="page_charts_section_charts_item_details_average_num"[^>]*>([^<]+)<',
        html
    )

    results = []
    for i, alt in enumerate(alts):
        artist, album = alt.split(" - ", 1)
        if ", Cover art" in album:
            album = album.replace(", Cover art", "")
        results.append({
            "rank": i + 1,
            "artist": artist,
            "album": album,
            "rating": ratings[i * 2] if i * 2 < len(ratings) else None,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="抓取 RYM Charts")
    parser.add_argument("--url", default=CHARTS_URL, help="RYM 页面 URL")
    parser.add_argument("--output", default=None, help="输出 JSON 文件路径")
    args = parser.parse_args()

    print(f"[1/3] 启动 Firefox（profile: {FIREFOX_PROFILE}）...")
    opts = Options()
    opts.add_argument("-profile")
    opts.add_argument(FIREFOX_PROFILE)
    driver = webdriver.Firefox(options=opts)

    print(f"[2/3] 访问 {args.url} ...")
    driver.get(args.url)
    import time
    time.sleep(5)

    title = driver.title
    html = driver.page_source
    print(f"      标题: {title} | HTML: {len(html)} 字节")

    if "Just a moment" in html[:500]:
        print("[!] 被 CF 拦截，cf_clearance 可能已过期")
        print("    请先用 computer_use 驱动 Firefox 访问 RYM 重新过 CF")
        driver.quit()
        sys.exit(1)

    print(f"[3/3] 提取数据...")
    data = extract_charts(html)
    print(f"      找到 {len(data)} 张专辑")

    # 输出
    output = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"      已保存到 {args.output}")
    else:
        print(f"\n🏆 RYM Charts Top {len(data)}:")
        for item in data[:20]:
            print(f"  {item['rank']:2d}. {item['artist']} - {item['album']}  [{item['rating']}/5]")

    driver.quit()
    print("\n✅ 完成")


if __name__ == "__main__":
    main()