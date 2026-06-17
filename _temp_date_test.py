from datetime import datetime, timezone
s = "Tue, 16 Jun 2026 04:03:00 +0000"
try:
    d = datetime.strptime(s, '%a, %d %b %Y %H:%M:%S %z')
    print(f"Parsed: {d}")
except Exception as e:
    print(f"Error: {e}")

# Try without %z
try:
    d = datetime.strptime(s, '%a, %d %b %Y %H:%M:%S %z')
    print(f"OK with %z")
except:
    # Try stripping timezone
    s2 = s.rsplit(' ', 1)[0]
    d = datetime.strptime(s2, '%a, %d %b %Y %H:%M:%S')
    d = d.replace(tzinfo=timezone.utc)
    print(f"Parsed (manual tz): {d}")
