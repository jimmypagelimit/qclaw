import os
ws = 'C:\\Users\\qujt\\.qclaw\\workspace'
files = []
for dp, dn, fn in os.walk(ws):
    for f in fn:
        if 'lyrics' in f.lower():
            files.append(os.path.join(dp, f))
for x in files[:30]:
    print(x)
