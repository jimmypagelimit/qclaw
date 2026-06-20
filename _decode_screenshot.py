import base64, sys

data = open('C:\\Users\\qujt\\.qclaw\\workspace\\exec.txt', 'rb').read()
# 找base64开始位置
text = data.decode('utf-8', errors='ignore')
start = text.find('Ej33')
if start > 0:
    b64 = text[start:text.find(' Update', start)]
    raw = base64.b64decode(b64)
    with open('C:\\Users\\qujt\\.qclaw\\workspace\\screenshot.png', 'wb') as f:
        f.write(raw)
    print(f'Saved {len(raw)} bytes')
else:
    print('No base64 found')
    print(text[:500])
