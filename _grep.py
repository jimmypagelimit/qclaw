import subprocess
r = subprocess.run(["grep", "-n", "total_listen_count", "C:/Users/qujt/.qclaw/workspace/tasks/2026-05-12-long-term-project/album-tracker/dist/server.js"], capture_output=True, text=True)
if r.stdout:
    print(r.stdout)
if r.stderr:
    print("stderr:", r.stderr[:200])
