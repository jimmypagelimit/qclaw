const feedChecker = require('C:\\Users\\qujt\\.qclaw\\workspace\\tasks\\rss-fetcher\\feed-checker.js');

const feeds = [
  'https://www.lionsroar.com/feed/',
  'https://tricycle.org/feed/',
  'https://www.buddhistinquiry.org/feed/',
  'https://www.dharma.org/feed/',
  'https://buddhism.stackexchange.com/feeds',
  'https://www.christianitytoday.com/feed/',
  'https://religionnews.com/feed/',
  'https://christianity.stackexchange.com/feeds',
  'https://www.islam21c.com/feed/',
  'https://www.aljazeera.com/xml/rss/all.xml',
  'https://islam.stackexchange.com/feeds',
  'https://www.jpost.com/rss',
  'https://www.jns.org/index.rss',
  'https://jewishnewswire.com/feed/',
  'https://www.timesofisrael.com/feed/',
  'https://forward.com/feed/',
  'https://www.theworldsikhnews.com/feed/',
  'https://sikhsiyasatnews.net/feed/',
  'https://www.reddit.com/r/religion/.rss',
  'https://www.reddit.com/r/Buddhism/.rss',
  'https://www.reddit.com/r/Christianity/.rss',
  'https://www.reddit.com/r/islam/.rss',
  'https://www.reddit.com/r/Judaism/.rss',
  'https://www.reddit.com/r/Hinduism/.rss',
];

feedChecker.main({
  feeds: feeds.join('|'),
  hours: 72,
  minScore: 4,
  format: 'json'
}).then(console.log).catch(e => { console.error(e.message); process.exit(1); });
