import subprocess, signal, sys, os

# 找到运行 server.js 的 node.exe 进程
result = subprocess.run(['tasklist', '/fi', 'imagename eq node.exe', '/fo', 'csv', '/nh'],
                       capture_output=True, text=True)
print('当前 node 进程:')
print(result.stdout)

# 找 server.js 对应的 PID（通过命令行参数）
import psutil
target_pids = []
for p in psutil.process_iter(['pid', 'name', 'cmdline']):
    if p.info['name'] == 'node.exe':
        cmdline = ' '.join(p.info['cmdline'] or [])
        if 'server.js' in cmdline:
            target_pids.append(p.info['pid'])
            print(f'  找到 server.js 进程: PID={p.info["pid"]}')

if not target_pids:
    print('未找到 server.js 进程，可能已停止')
else:
    for pid in target_pids:
        print(f'  终止 PID={pid}...')
        os.kill(pid, signal.SIGTERM)
    print('完成')
