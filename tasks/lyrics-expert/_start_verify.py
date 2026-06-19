import os, signal, time, subprocess, urllib.request, json

# kill node
os.system('taskkill /f /im node.exe 2>nul')
time.sleep(2)

# start
basedir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker'
proc = subprocess.Popen(
    ['node', 'dist/server.js'],
    cwd=basedir,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=subprocess.CREATE_NO_WINDOW
)
print('Started PID=' + str(proc.pid))
time.sleep(3)

# verify
r = json.loads(urllib.request.urlopen('http://localhost:3456/api/albums/461', timeout=10).read())
has_tracks = 'tracks' in r
t_count = len(r.get('tracks', []))
print('API OK. Has tracks=' + str(has_tracks) + ', count=' + str(t_count))
if has_tracks:
    for t in r['tracks'][:3]:
        print('  #' + str(t['track_number']) + ' ' + repr(t['track_name']) + ' (' + str(t.get('duration','?')) + 's)')
