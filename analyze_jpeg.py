import struct
import sys

def analyze_jpeg(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # 解析 JPEG 文件
    print(f'File size: {len(data)} bytes')
    
    # 检查 SOI (Start of Image)
    if data[:2] != b'\xff\xd8':
        print('Not a valid JPEG')
        return
    
    print('Valid JPEG file')
    
    # 简单提取 EXIF 或其他元数据
    pos = 2
    while pos < len(data) - 1:
        if data[pos] != 0xFF:
            pos += 1
            continue
        
        marker = data[pos + 1]
        
        # SOF (Start of Frame) markers
        if marker in [0xC0, 0xC1, 0xC2]:
            height = struct.unpack('>H', data[pos + 5:pos + 7])[0]
            width = struct.unpack('>H', data[pos + 7:pos + 9])[0]
            components = data[pos + 9]
            print(f'Width: {width}, Height: {height}, Components: {components}')
            break
        
        # 跳过其他 marker
        if marker in [0xD8, 0xD9]:  # SOI, EOI
            pos += 2
        elif marker == 0xDA:  # SOS - 实际图像数据开始
            break
        else:
            if pos + 4 <= len(data):
                length = struct.unpack('>H', data[pos + 2:pos + 4])[0]
                pos += 2 + length
            else:
                break

analyze_jpeg(r'C:\Users\15206\.qclaw\workspace\creature_of_habit_cover.jpg')
