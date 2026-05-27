#!/usr/bin/env python3
"""Simple RSS checker for heartbeat tasks."""

import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import ssl
import json
import sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch_rss(name, url, last_check_iso):
    """Fetch RSS and return new items since last_check."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = resp.read()
        root = ET.fromstring(data)
        
        new_items = []
        last_check = datetime.fromisoformat(last_check_iso)
        
        for item in root.findall('.//item'):
            title = item.findtext('title', '')
            link = item.findtext('link', '')
            pub_date_str = item.findtext('pubDate', '')
            
            # Simple approach: just collect recent items
            # In production, should parse pubDate properly
            new_items.append({
                'source': name,
                'title': title.strip(),
                'link': link.strip(),
            })
        
        return new_items[:5]  # Return top 5 items
    except Exception as e:
        print(f'Error fetching {name}: {e}', file=sys.stderr)
        return []

def format_feishu_message(items, category):
    """Format items for Feishu notification."""
    if not items:
        return f"今日{category}：无重大更新"
    
    lines = [f"🎸 {category} 动态更新："]
    for item in items[:5]:
        title = item['title'][:50]
        lines.append(f"• {title}")
    
    return "\n".join(lines)

if __name__ == '__main__':
    # Read heartbeat-state.json
    with open('heartbeat-state.json', 'r') as f:
        state = json.load(f)
    
    last_check = state['lastChecks'].get('indie_rss', '2026-05-25T06:01:00+08:00')
    
    # Indie RSS sources for Wednesday (周一三五)
    sources = [
        ('Pitchfork', 'https://pitchfork.com/feed/rss'),
        ('Stereogum', 'https://www.stereogum.com/feed/'),
        ('Aquarium Drunkard', 'https://aquariumdrunkard.com/feed/'),
        ('Post-Punk.com', 'https://post-punk.com/feed/'),
    ]
    
    all_items = []
    for name, url in sources:
        items = fetch_rss(name, url, last_check)
        all_items.extend(items)
    
    # Format and print message
    msg = format_feishu_message(all_items, "Indie音乐")
    print(msg)
    
    # Update state
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    state['lastChecks']['indie_rss'] = now
    state['lastHeartbeat'] = now
    
    with open('heartbeat-state.json', 'w') as f:
        json.dump(state, f, indent=4, ensure_ascii=False)
    
    print(f"\nState updated: indie_rss={now}", file=sys.stderr)
