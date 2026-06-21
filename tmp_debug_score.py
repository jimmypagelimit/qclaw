import urllib.request
import re

url = "https://pitchfork.com/reviews/albums/car-seat-headrest-twin-fantasy/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='replace')

print("=== All 'score' occurrences ===")
for m in re.finditer(r'"score":\s*([\d.]+)', html):
    start = max(0, m.start()-50)
    end = min(len(html), m.end()+50)
    print(f"Pos {m.start()}: ...{html[start:end]}...")
    print(f"  Matched value: {m.group(1)}")
    print()

print("=== All 'ratingValue' occurrences ===")
for m in re.finditer(r'"ratingValue"', html):
    start = max(0, m.start()-100)
    end = min(len(html), m.end()+100)
    print(f"Pos {m.start()}: ...{html[start:end]}...")
    print()
