#!/usr/bin/env python3
"""测试 album-tracker API，ASCII 输出，结果写文件"""
import urllib.request, json, os

base = 'http://localhost:3456/api'
results = []

def test(name, url):
    try:
        r = urllib.request.urlopen(url, timeout=8)
        data = json.loads(r.read().decode())
        results.append('[OK] %s' % name)
        if 'stats' in url:
            a = data.get('albums', {})
            results.append('  count=%s, totalListens=%s' % (a.get('count'), a.get('totalListens')))
            top = a.get('topAlbum') or {}
            results.append('  top=%s - %s' % (top.get('artist','?'), top.get('album_name','?')))
        elif 'top' in url:
            for alb in (data.get('albums') or [])[:3]:
                results.append('  %s - %s (%s次)' % (alb.get('artist'), alb.get('album_name'), alb.get('total_listen_count','?')))
        elif 'albums' in url:
            for alb in (data.get('albums') or [])[:3]:
                results.append('  %s - %s (%s次)' % (alb.get('artist'), alb.get('album_name'), alb.get('total_listen_count','?')))
    except Exception as e:
        results.append('[FAIL] %s: %s' % (name, e))

test('stats', '%s/stats' % base)
test('top', '%s/top?limit=3' % base)
test('albums-sort-listen', '%s/albums?sort=listen&limit=3' % base)
test('albums-sort-score', '%s/albums?sort=score&limit=3' % base)

output = '\n'.join(results)
print(output)

with open(r'C:\Users\qujt\.qclaw\workspace\_api_test_result.txt', 'w', encoding='utf-8') as f:
    f.write(output)
print('\n-> 结果已写入 _api_test_result.txt')
