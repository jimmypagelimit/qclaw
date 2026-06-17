# count sources
import sys
sys.path.insert(0, r'C:\Users\qujt\.qclaw\workspace')

code = open(r'C:\Users\qujt\.qclaw\workspace\_deep_translate.py', encoding='utf-8').read()
exec(code.split('def main')[0])

total = sum(len(v['sources']) for v in SLOT_SOURCES.values())
for k, v in SLOT_SOURCES.items():
    n = len(v['sources'])
    print(f'{k}: {n}')
print(f'Total: {total}')
