import tarfile, os

t = tarfile.open(r'D:\skillhub.tar.gz')
t.extractall(r'D:\skillhub')
t.close()

for root, dirs, files in os.walk(r'D:\skillhub'):
    for f in files:
        path = os.path.join(root, f)
        rel = os.path.relpath(path, r'D:\skillhub')
        print(rel)
