"""
用 opencli 浏览器（已登录网易云）批量抓取专辑歌词
"""
import subprocess, json, time, re, sys

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'

def run_opencli(js):
    """通过 opencli browser eval 执行 JS，返回 JSON 结果"""
    js_escaped = js.replace('"', '\\"').replace('\n', ' ')
    cmd = f'opencli browser work eval "fetch(\\047https://music.163.com/api/album/{js_escaped}\\047,{{credentials:\\047include\\047}}).then(r=>r.json()).then(d=>{{window.__result=JSON.stringify(d);return d;}}).catch(e=>{{window.__result=JSON.stringify({{error:e.message}});return {{error:e.message}};}})"'
    # 简化：用固定的 fetch 调用
    result = subprocess.run(
        f'opencli browser work eval "fetch(\\047https://music.163.com{js}\\047,{{credentials:\\047include\\047}}).then(r=>r.json()).then(d=>{{window.__result=JSON.stringify(d);return d;}})"',
        capture_output=True, text=True, timeout=30, shell=True
    )
    return result.stdout + result.stderr

def get_album_data_js(album_id):
    """生成获取专辑数据的 JS"""
    return (
        f"fetch('/api/album/{album_id}',{{credentials:'include'}}"
        f".then(r=>r.json())"
        f".then(d=>{{window.__album=JSON.stringify(d);return d;}})"
    )

def get_song_lyric_js(song_id):
    """生成获取歌词的 JS"""
    return (
        f"fetch('/api/song/lyric?id={song_id}&lv=1&kv=1&tv=-1',{{credentials:'include'}}"
        f".then(r=>r.json())"
        f".then(d=>{{window.__lyric=JSON.stringify(d);return d;}})"
    )

def extract_result(stdout, key):
    """从 opencli 输出中提取 __result 值"""
    # 找 "window.__result=..." 或直接找 JSON
    m = re.search(r'window\.__\w+=({.+?})\s*(?:window\.|Process|$)', stdout, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except:
            pass
    # 尝试直接找 JSON
    m = re.search(r'\{".+?\]\}', stdout, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except:
            pass
    return None

# 测试：用嘎调专辑验证
album_id = 35136
js = get_album_data_js(album_id).replace("'", "\\'")
cmd = [
    'opencli', 'browser', 'work', 'eval',
    f"fetch('/api/album/{album_id}',{{credentials:'include'}}).then(r=>r.json()).then(d=>{{window.__album=JSON.stringify(d);return Object.keys(d);}})"
]

print('Running opencli command...')
print(' '.join(cmd))

result = subprocess.run(
    ['opencli', 'browser', 'work', 'eval',
     f"fetch('/api/album/{album_id}',{{credentials:'include'}}).then(r=>r.json()).then(d=>{{window.__album=JSON.stringify(d);return Object.keys(d);}})"],
    capture_output=True, text=True, timeout=30
)
print('STDOUT:', result.stdout[:500])
print('STDERR:', result.stderr[:200])
