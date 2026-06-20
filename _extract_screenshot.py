import base64, re, sys

# 从 exec 输出读取 base64 数据
data = sys.stdin.read() if len(sys.argv) < 2 else open(sys.argv[1], 'r', encoding='utf-8', errors='ignore').read()

# 找 base64 开始（PNG signature: iVBOR）
start = data.find('iVBOR')
if start < 0:
    # 尝试找 Ej33h (另一个可能的开始)
    start = data.find('Ej33')

if start >= 0:
    # 找到结束位置（查找 "Update available" 或文件结束）
    end_markers = ['Update available', ' Run:', 'Process exited']
    end = len(data)
    for marker in end_markers:
        pos = data.find(marker, start)
        if pos > 0 and pos < end:
            end = pos
    
    b64 = data[start:end].strip()
    print(f'Found base64 at {start}, length {len(b64)}')
    try:
        raw = base64.b64decode(b64)
        out = 'screenshot.png'
        open(out, 'wb').write(raw)
        print(f'Decoded {len(raw)} bytes -> {out}')
    except Exception as e:
        print(f'Decode error: {e}')
        # 可能换行了，尝试清理
        b64_clean = re.sub(r'\s', '', b64)
        raw = base64.b64decode(b64_clean)
        open('screenshot.png', 'wb').write(raw)
        print(f'Decoded (cleaned) {len(raw)} bytes -> screenshot.png')
else:
    print('No base64 PNG found')
    print('First 500 chars:', data[:500])
