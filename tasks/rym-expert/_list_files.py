import os, sys
sys.path.append(r"C:\Users\qujt\.qclaw\workspace\tasks\rym-expert")
root = r"C:\Users\qujt\.qclaw\workspace\tasks\rym-expert"
files = []
for r, d, f in os.walk(root):
    for file in f:
        if '.git' in r or '__pycache__' in r:
            continue
        files.append(os.path.relpath(os.path.join(r, file), root))
print(f"\n".join(sorted(files)))
