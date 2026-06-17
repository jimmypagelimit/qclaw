import os
base = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker"
for root, dirs, files in os.walk(os.path.join(base, "src")):
    level = root.replace(base, "").count(os.sep)
    indent = "  " * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = "  " * (level + 1)
    for f in sorted(files):
        print(f"{subindent}{f}")
