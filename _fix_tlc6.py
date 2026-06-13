"""Fix the syntax error from empty if block"""
js_path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\dist\server.js'
with open(js_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and fix: if (existing) { \n else { -> just remove the if (existing) block
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # If we see 'if (existing) {' followed immediately by 'else {'
    if 'if (existing)' in line:
        # Skip this line and the next 'else {' line
        i += 1
        while i < len(lines) and 'else {' not in lines[i]:
            i += 1
        if i < len(lines):
            # Found 'else {', skip it too
            i += 1
            continue
        # Don't continue to add the 'else {' we already skip it above
    new_lines.append(line)
    i += 1

lines = new_lines

with open(js_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Verify syntax
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
