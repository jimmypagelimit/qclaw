#!/bin/bash
for url in \
  "https://tricycle.org/feed/" \
  "https://www.christianitytoday.com/feed/" \
  "https://christianitytoday.com/ct/podcast/feed" \
  "https://www.thegospelcoalition.org/feeds/rss/" \
  "https://www.bibleodyssey.org/feed/" \
  "https://buddhiststudies.com/feed/" \
  "https://www.dharmata.org/feed" \
  "https://www.shambhala.com/feed/" \
  "https://www.lionsroar.com/consumer/feed.xml" \
  "https://islamicaz.com/feed/" \
  "https://www.aljazeera.com/xml/rss/edition.aspx" \
  "https://www.firstthings.com/webfeeds/feed" \
  "https://www.catholicnews.com/rss" \
  "https://www.ncregister.com/cns-blog/rss" \
  "https://www.islamicity.org/feed/" \
  "https://www.islamiq.org/feed/" \
  "https://www.buddhiststudies.net/feed/" \
  "https://www.academia.edu/feed" \
  "https://www.pewresearch.org/religion/feed/" \
  "https://thebuddhistworld.net/feed/" \
  "https://buddhism.stackexchange.com/feeds" \
  "https://christianity.stackexchange.com/feeds" \
  "https://islam.stackexchange.com/feeds" \
  "https://religion.stackexchange.com/feeds"
do
  echo "=== $url ==="
  curl -sI "$url" 2>/dev/null | grep -i "http\|content-type" | head -2
  echo ""
done