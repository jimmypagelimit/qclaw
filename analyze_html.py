import re
import sys

html_path = sys.argv[1] if len(sys.argv) > 1 else "lyrics/Wait-What-Did-You-Say/debug_The-City.html"
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 查找 PRELOADED_STATE
match = re.search(r"window\.__PRELOADED_STATE__\s*=\s*JSON\.parse\('([^']+)'\)", html)
if match:
    print("Found PRELOADED_STATE (JSON.parse)")
    json_str = match.group(1)
    # 解码
    json_str = json_str.replace("\\u0022", '"').replace("\\u003c", "<").replace("\\u003e", ">")
    print(f"Length: {len(json_str)}")
    # 查找 lyrics
    lyrics_match = re.search(r'"lyrics":\{[^}]*"body":\{[^}]*"html":"([^"]+)"', json_str)
    if lyrics_match:
        print("Found lyrics!")
        lyrics = lyrics_match.group(1)
        print(lyrics[:500])
    else:
        # 尝试另一种模式
        print("Trying alternative pattern...")
        lyrics_match2 = re.search(r'"html":"\[.+?\]', json_str)
        if lyrics_match2:
            print("Found bracket content:", lyrics_match2.group(0)[:200])
else:
    print("PRELOADED_STATE not found in expected format")
    # 搜索其他模式
    for pattern in ["Lyrics__Container", "data-lyrics-container", "lyrics-body"]:
        if pattern in html:
            idx = html.find(pattern)
            print(f"Found '{pattern}' at {idx}: {html[max(0,idx-20):idx+100]}")
