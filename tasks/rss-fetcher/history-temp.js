const { main } = require('C:/Users/qujt/.qclaw/workspace/tasks/rss-fetcher/feed-checker.js');
const fs = require('fs');
const feeds = [
  'https://www.historytoday.com/rss.xml',
  'https://www.historyextra.com/feed',
  'https://historyworkshop.org.uk/feed/',
  'https://www.smithsonianmag.com/rss/latest_articles/',
  'https://blog.oup.com/category/history/feed/',
  'https://www.reddit.com/r/AskHistorians/.rss',
  'https://www.reddit.com/r/history/.rss',
  'https://www.reddit.com/r/HistoryofIdeas/.rss',
  'https://www.reddit.com/r/ChineseHistory/.rss'
].join('|');

main({feeds, hours: 72, minScore: 4, format: 'json'}).then(r => {
  const items = JSON.parse(r);
  console.log('COUNT:' + items.length);
  items.slice(0, 25).forEach(i => {
    console.log(i.score + '|' + i.title.substring(0, 100) + '|' + i.link + '|' + (i.pubDate || ''));
  });
  // save full results
  fs.writeFileSync('C:/Users/qujt/.qclaw/workspace/tasks/rss-fetcher/history-output.json', JSON.stringify(items, null, 2));
}).catch(e => { console.error('ERROR:' + e.message); process.exit(1); });