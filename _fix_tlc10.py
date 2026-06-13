"""Remove the extra closing brace"""
js_path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\dist\server.js'
with open(js_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find line with double }} - extra closing brace
result = []
for line in lines:
    stripped = line.strip()
    if stripped == '}':
        # Check if the next line also starts the /api/albums/:id/listen endpoint
        idx = lines.index(line) if line in lines else -1
        result.append(line)
    else:
        result.append(line)

# Actually, simpler: find the exact line 354 (0-indexed 353) which has "}" 
# and remove it if the next line also has "}"
# But let me just find all lines that are just "}" preceded by another "}"
n = len(lines)
i = 0
new_lines = []
while i < n:
    curr = lines[i]
    nextline = lines[i+1] if i+1 < n else ''
    # If current line is just "}        " and next line is also "}        " - remove the second one
    if curr.strip() == '}' and nextline.strip() == '}' and nextline.strip() == curr.strip():
        # Keep first, skip second  
        new_lines.append(curr)
        i += 2
        print(f"Removed double }} at lines ~{i}")
    else:
        new_lines.append(curr)
        i += 1

lines = new_lines

with open(js_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

import subprocess, time
p = subprocess.Popen(['node', '-e', 'require("./dist/server.js")'],
    cwd=r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker',
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(3)
err = p.stderr.read(2000).decode('utf-8', errors='replace')
if err:
    print('SYNTAX ERROR:', err[:400])
else:
    print('Syntax OK')
p.kill()
