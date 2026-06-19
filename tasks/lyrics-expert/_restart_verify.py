import os, time, subprocess, urllib.request, json

os.system('taskkill /f /im node.exe 2>nul')
time.sleep(2)

basedir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker'
proc = subprocess.Popen(
    ['node', 'dist/server.js'],
    cwd=basedir,
    stdout=open(os.devnull, 'w'),
    stderr=subprocess.STDOUT,
    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
)

time.sleep(3)

# verify 424
r = json.loads(urllib.request.urlopen('http://localhost:3456/api/albums/424', timeout=5).read())
print(f'SERVICE OK | {r["artist"]} - {r["album_name"]} | Tracks: {len(r.get("tracks",[]))}')
for t in r['tracks']:
    print(f'  {t["track_number"]}. {t["track_name"]} ({t.get("duration","?")}s)')
