import subprocess, os, signal

r = subprocess.run(['tasklist', '/fi', 'IMAGENAME eq node.exe', '/fo', 'csv'],
                   capture_output=True, text=True)
lines = r.stdout.strip().split('\n')
for line in lines[1:]:
    parts = line.split(',')
    if len(parts) >= 1:
        name = parts[0].strip('"')
        pid = int(parts[1].strip('"'))
        if 'server' in name.lower() or 'node' == name.lower():
            os.kill(pid, 9)
            print(f"Killed pid={pid} ({name})")
print("done")
