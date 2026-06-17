#!/usr/bin/env python3
"""一键加听歌记录 - 直接调 Web API，不停服务不操作数据库"""
import urllib.request, json, sys

PORT = 3456

def add_listen(album_id, count=1):
    url = f"http://localhost:{PORT}/api/albums/{album_id}/listen"
    data = json.dumps({"count": count}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        result = json.loads(resp.read())
        name = result.get("album", {}).get("album_name", "?")
        artist = result.get("album", {}).get("artist", "?")
        print(f"OK: {artist} - {name} (album_id={album_id}, +{count} listen)")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_listen.py <album_id> [count]")
        sys.exit(1)
    album_id = int(sys.argv[1])
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    add_listen(album_id, count)