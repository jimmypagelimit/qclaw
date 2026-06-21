#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pf_query.py - Query Pitchfork review for a single album

Usage:
    C:\Python311\python.exe pf_query.py "Car Seat Headrest" "Twin Fantasy"
    C:\Python311\python.exe pf_query.py "Sonic Youth" "Daydream Nation"

Output (JSON):
    {
        "found": true,
        "score": 8.6,
        "bnm": "Best New Album",   # or null
        "review_url": "https://pitchfork.com/reviews/albums/...",
        "author": "Natalie Weiner",
        "publish_date": "2026-06-19",
        "excerpt": "..."
    }
"""

import sys
import os
import urllib.request
import urllib.parse
import re
import json
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9',
}

TIMEOUT = 15  # seconds

def fetch(url, sleep=1):
    """Fetch URL, return HTML string. Sleep before request to be polite."""
    time.sleep(sleep)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return None

def search_pitchfork(artist, album):
    """Search Pitchfork and return list of review URLs."""
    query = f"{artist} {album}"
    encoded = urllib.parse.quote(query)
    url = f"https://pitchfork.com/search/?query={encoded}"
    html = fetch(url, sleep=0)
    if not html:
        return []

    # Extract /reviews/albums/... links
    links = re.findall(r'["\'](/reviews/albums/[^"\']+)["\']', html)
    # Deduplicate, keep order
    seen = set()
    unique = []
    for link in links:
        if link not in seen:
            seen.add(link)
            unique.append(link)
    return unique

def extract_score(html):
    """Extract Pitchfork score from review page HTML.
    
    The page contains multiple 'score' fields:
    - Topic/keyword scores (decimal < 1.0, not the review score)
    - Review score (0.0-10.0) near 'isBestNewMusic' field
    
    Strategy: Look for 'score' after 'isBestNewMusic' or 'isBestNewReissue'
    """
    # Pattern 1: score near BNM tags (most reliable)
    m = re.search(r'"isBestNewMusic":\s*(true|false),\s*"isBestNewReissue":\s*(true|false),\s*"score":\s*(\d+\.?\d*)', html)
    if m:
        return float(m.group(3))
    
    # Pattern 2: fallback - find all 'score' values, pick the one in valid PF range
    # that's NOT in the topics/keywords section
    all_scores = re.findall(r'"score":\s*(\d+\.?\d*)', html)
    valid_scores = []
    for s in all_scores:
        val = float(s)
        # Valid PF score: 0.0 - 10.0, and NOT a decimal < 1 (those are topic scores)
        if 0.0 <= val <= 10.0 and val >= 1.0:
            valid_scores.append(val)
    
    if valid_scores:
        # Return the first valid score found
        return valid_scores[0]
    
    return None

def extract_bnm(html):
    """Extract Best New Music tag if present."""
    tags = []
    for tag in ['Best New Album', 'Best New Reissue', 'Best New Track']:
        if tag in html:
            tags.append(tag)
    return tags[0] if tags else None

def extract_author(html):
    """Extract author from JSON-LD or page."""
    m = re.search(r'"author":\s*\[\s*{\s*"@type":\s*"Person",\s*"name":\s*"([^"]+)"', html, re.S)
    if m:
        return m.group(1)
    return None

def extract_date(html):
    """Extract publish date."""
    # Pattern 1: JSON-LD datePublished
    m = re.search(r'"datePublished":\s*"(\d{4}-\d{2}-\d{2})"', html)
    if m:
        return m.group(1)
    
    # Pattern 2: pubdate in page data
    m2 = re.search(r'"pubdate":"(\d{4}-\d{2}-\d{2})', html)
    if m2:
        return m2.group(1)
    
    # Pattern 3: ISO datetime
    m3 = re.search(r'"pubdate":"(\d{4}-\d{2}-\d{2})T', html)
    if m3:
        return m3.group(1)
    
    return None

def extract_excerpt(html):
    """Extract review excerpt/description."""
    m = re.search(r'"description":\s*"([^"]{0,300})"', html, re.S)
    if m:
        desc = m.group(1).strip()
        desc = re.sub(r'\s+', ' ', desc)
        return desc[:200]
    return None

def query_album(artist, album):
    """Main query function. Returns dict with results."""
    result = {
        "artist": artist,
        "album": album,
        "found": False,
        "score": None,
        "bnm": None,
        "review_url": None,
        "author": None,
        "publish_date": None,
        "excerpt": None,
        "error": None,
    }

    # Step 1: Search
    links = search_pitchfork(artist, album)
    if not links:
        result["error"] = "No Pitchfork review found in search results"
        return result

    # Step 2: Pick the best match (first link that contains artist/album keywords)
    artist_lower = artist.lower()
    album_lower = album.lower()
    best_link = links[0]  # Default: first result

    for link in links[:5]:  # Check first 5 results
        link_lower = link.lower()
        # Simple heuristic: link should contain artist or album words
        artist_words = [w for w in artist_lower.split() if len(w) > 2]
        album_words = [w for w in album_lower.split() if len(w) > 2]
        score = 0
        for w in artist_words + album_words:
            if w in link_lower:
                score += 1
        if score > 0:
            best_link = link
            break

    review_url = f"https://pitchfork.com{best_link}"
    result["review_url"] = review_url

    # Step 3: Fetch review page
    html = fetch(review_url, sleep=1)
    if not html:
        result["error"] = "Failed to fetch review page"
        return result

    # Step 4: Extract data
    score = extract_score(html)
    if score is not None:
        result["score"] = score
        result["found"] = True

    bnm = extract_bnm(html)
    if bnm:
        result["bnm"] = bnm
        result["found"] = True

    result["author"] = extract_author(html)
    result["publish_date"] = extract_date(html)
    result["excerpt"] = extract_excerpt(html)

    if not result["found"]:
        result["error"] = "Review page found but no score/BNM extracted"

    return result

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: pf_query.py <artist> <album>")
        sys.exit(1)

    artist = sys.argv[1]
    album = sys.argv[2]

    result = query_album(artist, album)
    print(json.dumps(result, ensure_ascii=False, indent=2))
