#!/usr/bin/env python3
"""
歌词获取与翻译工具（中英对照）
从 AZLyrics 获取歌词，用 GLM API 翻译

用法:
    python lyrics_tool.py --artist "Car Seat Headrest" --title "Sober To Death"
    python lyrics_tool.py -a "Nirvana" -t "Smells Like Teen Spirit" -n
"""

import argparse
import json
import os
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


# ============ 工具函数 ============

def slugify_artist(artist: str) -> str:
    """AZLyrics 艺人 slug：全小写，去掉非字母数字，开头 'the ' 去掉"""
    s = artist.lower().strip()
    if s.startswith("the "):
        s = s[4:]
    return re.sub(r'[^a-z0-9]', '', s)


def slugify_title(title: str) -> str:
    """AZLyrics 歌曲 slug：全小写，去掉非字母数字"""
    s = title.lower().strip()
    return re.sub(r'[^a-z0-9]', '', s)


# ============ 歌词获取 ============

def fetch_azlyrics(artist: str, title: str) -> str:
    """从 AZLyrics 获取歌词"""
    url = f"https://www.azlyrics.com/lyrics/{slugify_artist(artist)}/{slugify_title(title)}.html"
    print(f"  URL: {url}")

    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
    })

    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"  请求失败: {e}")
        return None

    # AZLyrics 歌词在版权注释之后的 div 里
    # 注释文本有两种变体
    for marker in [
        "Usage of azlyrics.com content by any third-party",
        "Usage of azlyrics.com data by your application",
    ]:
        pos = html.find(marker)
        if pos != -1:
            break
    else:
        print("  未找到歌词标记")
        return None

    # 找注释结束后的第一个 </div>（这是包裹歌词的 div 的结束）
    comment_end = html.find("-->", pos)
    if comment_end == -1:
        return None

    # 歌词在注释之后直到下一个 </div>
    lyrics_start = comment_end + 3
    lyrics_end = html.find("</div>", lyrics_start)
    if lyrics_end == -1:
        return None

    raw = html[lyrics_start:lyrics_end]

    # 清理 HTML 标签
    raw = re.sub(r'<br\s*/?>', '\n', raw, flags=re.IGNORECASE)
    raw = re.sub(r'<[^>]+>', '', raw)
    raw = re.sub(r'\r\n', '\n', raw)
    raw = re.sub(r'\n{3,}', '\n\n', raw)
    lyrics = raw.strip()

    return lyrics if len(lyrics) > 20 else None


# ============ GLM 翻译 ============

def translate_glm(lyrics: str, api_key: str) -> str:
    """用 GLM-4-Flash 翻译歌词，逐段对照"""
    paragraphs = [p.strip() for p in lyrics.split('\n\n') if p.strip()]

    prompt = f"""请将以下英文歌词翻译成中文。

要求：
- 意译为主，保留诗意和情感
- 每段之间用 [SEP] 分隔（与原文段落一一对应）
- 不要加任何解释，只输出翻译

歌词（段落之间用 [SEP] 分隔）：
{chr(10).join(f"[SEP]{chr(10)}{p}" if i > 0 else p for i, p in enumerate(paragraphs))}

翻译："""

    data = json.dumps({
        "model": "glm-4-flash",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }).encode()

    req = urllib.request.Request(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )

    try:
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read())
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"  翻译失败: {e}")
        return None


def build_bilingual(lyrics: str, translation: str) -> str:
    """生成中英对照"""
    en_paras = [p.strip() for p in lyrics.split('\n\n') if p.strip()]
    zh_paras = [p.strip() for p in translation.split('[SEP]') if p.strip()]

    lines = []
    for i in range(max(len(en_paras), len(zh_paras))):
        en = en_paras[i] if i < len(en_paras) else ""
        zh = zh_paras[i] if i < len(zh_paras) else "（无翻译）"
        lines.append(en)
        lines.append(zh)
        lines.append("")
        lines.append("─" * 40)
        lines.append("")

    return '\n'.join(lines).strip()


# ============ 主函数 ============

def main():
    parser = argparse.ArgumentParser(description="歌词获取与翻译（中英对照）")
    parser.add_argument("--artist", "-a", required=True, help="艺人名称")
    parser.add_argument("--title", "-t", required=True, help="歌曲名称")
    parser.add_argument("--no-translate", "-n", action="store_true", help="只获取原文")
    parser.add_argument("--api-key", "-k", help="智谱 API Key")
    parser.add_argument("--save-dir", "-s", default="lyrics", help="保存目录（默认 lyrics/）")

    args = parser.parse_args()
    api_key = args.api_key or os.environ.get('ZHIPU_API_KEY')

    print(f"🎵 {args.title} — {args.artist}")
    print()

    # 1. 获取歌词
    print("📡 获取歌词...")
    lyrics = fetch_azlyrics(args.artist, args.title)

    if not lyrics:
        print("❌ 获取失败")
        return

    print(f"✅ 成功（{len(lyrics)} 字符）")
    print()

    # 2. 翻译
    translation = None
    if not args.no_translate:
        if api_key:
            print("🔄 翻译中...")
            translation = translate_glm(lyrics, api_key)
            if translation:
                print("✅ 翻译完成")
            print()
        else:
            print("⚠️  未设置 ZHIPU_API_KEY，跳过翻译")
            print()

    # 3. 生成输出
    if translation:
        output = build_bilingual(lyrics, translation)
    else:
        output = lyrics

    print("=" * 50)
    print(output)
    print("=" * 50)

    # 4. 保存
    save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.save_dir)
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{args.artist} - {args.title}.txt"
    filepath = os.path.join(save_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(output)
    print(f"\n📁 已保存: {filepath}")


if __name__ == "__main__":
    main()
