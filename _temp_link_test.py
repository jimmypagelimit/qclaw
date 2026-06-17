import urllib.request
from xml.etree import ElementTree as ET

url = "https://pitchfork.com/feed/rss"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
data = urllib.request.urlopen(req, timeout=15).read()
root = ET.fromstring(data)
items = root.findall('.//item')
for item in items[:3]:
    link_el = item.find('link')
    print(f"link element: {link_el}")
    print(f"link text: {repr(link_el.text) if link_el is not None else 'None'}")
    print(f"link tail: {repr(link_el.tail) if link_el is not None else 'None'}")
    # Print raw XML of first item
    import xml.etree.ElementTree as ET2
    print(ET2.tostring(item, encoding='unicode')[:500])
    print("---")
