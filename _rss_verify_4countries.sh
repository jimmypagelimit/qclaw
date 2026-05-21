#!/bin/bash
# Verify RSS feeds for Russia, Japan, Germany, France

echo "=== Testing RSS Feeds ==="

# Russia
echo "Russia:"
curl -sI "https://www.culture.ru/news/literature" 2>/dev/null | head -1
curl -sI "https://russiancouncil.ru/en/rss/" 2>/dev/null | head -1
curl -sI "https://litjazras.ru/" 2>/dev/null | head -1

# Japan
echo "Japan:"
curl -sI "https://www.ndl.go.jp/en/service/rssemag.html" 2>/dev/null | head -1
curl -sI "https://japannews.yomiuri.co.jp/culture/books-literature/" 2>/dev/null | head -1

# Germany
echo "Germany:"
curl -sI "https://www.goethe.de/en/feed.html" 2>/dev/null | head -1
curl -sI "https://www.dla-marbach.de/en/informationen/about-us/" 2>/dev/null | head -1

# France (new search)
echo "France:"
curl -sI "https://www.lemonde.fr/culture" 2>/dev/null | head -1
curl -sI "https://www.telerama.fr/livres" 2>/dev/null | head -1
curl -sI "https://www.franceculture.fr/emission/les-chroniques" 2>/dev/null | head -1