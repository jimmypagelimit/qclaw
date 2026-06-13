# Task Artifact: Fix Religion RSS Fetcher

## Objective
Fix the failing `temp-religion.js` script that crashed with a Node.js module loading error (code 1).

## Problem
The script `C:\Users\qujt\.qclaw\workspace\tasks\rss-fetcher\temp-religion.js` was trying to require a non-existent module `feed-checker.js`, causing the error:
```
Error: Cannot find module 'C:\Users\qujt\.qclaw\workspace\tasks\rss-fetcher\feed-checker.js'
```

## Solution
Created `feed-checker.js` module with the following capabilities:
- Fetches RSS/Atom feeds via HTTP/HTTPS
- Parses XML to extract items (title, link, pubDate, description, content)
- Handles both RSS 2.0 and Atom formats
- Calculates relevance scores for items
- Filters by date (within specified hours)
- Returns JSON or text formatted output

## Key Features Implemented
1. **RSS/Atom Parser**: Regex-based parser that extracts items from both RSS 2.0 (`<item>`) and Atom (`<entry>`) feeds
2. **HTTP(S) Fetcher**: Uses Node.js built-in `http` and `https` modules with proper headers and timeout handling
3. **Score Calculator**: Simple scoring algorithm (base 5, +2 for descriptions, +2 for content, +1 for short titles, +1 for feed URLs)
4. **Date Filter**: Filters items by publication date (default 72 hours)
5. **Sorting**: Sorts by score (descending), then by date (descending)

## Result
- Script now runs successfully (exit code 0)
- Successfully fetched 48 items from 24 religious RSS feeds
- Output includes items from: Christianity Today, Forward, Tricycle (Buddhism), Al Jazeera, JNS, Sikh Siyasat News, and Stack Exchange sites

## Next Steps
- Process the output to filter for actual religious content (remove World Cup/politics)
- Format and send to Feishu group as specified in HEARTBEAT.md
- Consider improving the scoring algorithm to better identify religious content
