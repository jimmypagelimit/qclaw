import os, time, subprocess

basedir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker'

# kill all node
os.system('taskkill /f /im node.exe 2>nul')
time.sleep(2)

# check no node running
r = os.popen('tasklist /fi "imagename eq node.exe" /nh 2>nul').read().strip()
print('After kill:', 'node running' if 'node' in r.lower() else 'none')

# start with background subprocess
proc = subprocess.Popen(
    ['node', 'dist/server.js'],
    cwd=basedir,
    stdout=open(os.devnull, 'w'),
    stderr=subprocess.STDOUT,
    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
)
pid = proc.pid
print('Started PID=' + str(pid))

# wait up to 15 seconds
for i in range(15):
    time.sleep(1)
    r = os.popen('tasklist /fi "imagename eq node.exe" /nh 2>nul').read().strip()
    has_node = 'node' in r.lower()
    if has_node:
        try:
            import urllib.request, json
            resp = urllib.request.urlopen('http://localhost:3456/api/albums/461', timeout=3)
            data = json.loads(resp.read())
            print('Service OK! PID=' + str(pid) + ' Has tracks=' + str('tracks' in data) + ' count=' + str(len(data.get('tracks',[]))))
            break
        except:
            print('  Waiting... (' + str(i+1) + 's, node running)')
    else:
        print('  Process died! Trying to restart...')
        proc = subprocess.Popen(
            ['node', 'dist/server.js'],
            cwd=basedir,
            stdout=open(os.devnull, 'w'),
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
        )
        pid = proc.pid
        print('  Restarted PID=' + str(pid))
