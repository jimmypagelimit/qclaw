const https = require('https');
const http = require('http');
const { URL } = require('url');

/**
 * Parse RSS/Atom feed XML and extract items
 */
function parseFeed(xml, feedUrl) {
  const items = [];
  
  // Simple regex-based parser (handles both RSS 2.0 and Atom)
  // RSS 2.0 format
  const rssItemRegex = /<item>([\s\S]*?)<\/item>/g;
  let match;
  
  while ((match = rssItemRegex.exec(xml)) !== null) {
    const itemXml = match[1];
    const item = {
      title: extractTag(itemXml, 'title'),
      link: extractTag(itemXml, 'link'),
      pubDate: extractTag(itemXml, 'pubDate') || extractTag(itemXml, 'dc:date') || extractTag(itemXml, 'published'),
      description: extractTag(itemXml, 'description') || extractTag(itemXml, 'content:encoded') || '',
      content: extractTag(itemXml, 'content:encoded') || extractTag(itemXml, 'content') || ''
    };
    
    if (item.title && item.link) {
      items.push(item);
    }
  }
  
  // Atom format
  const atomEntryRegex = /<entry>([\s\S]*?)<\/entry>/g;
  while ((match = atomEntryRegex.exec(xml)) !== null) {
    const entryXml = match[1];
    const linkMatch = entryXml.match(/<link[^>]*href=["']([^"']+)["']/);
    const item = {
      title: extractTag(entryXml, 'title'),
      link: linkMatch ? linkMatch[1] : '',
      pubDate: extractTag(entryXml, 'published') || extractTag(entryXml, 'updated'),
      description: extractTag(entryXml, 'summary') || extractTag(entryXml, 'content') || '',
      content: extractTag(entryXml, 'content') || ''
    };
    
    if (item.title && item.link) {
      items.push(item);
    }
  }
  
  return items;
}

function extractTag(xml, tagName) {
  const regex = new RegExp(`<${tagName}[^>]*>([\\s\\S]*?)<\\/${tagName}>`, 'i');
  const match = xml.match(regex);
  if (match) {
    return match[1]
      .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, '$1')
      .replace(/<[^>]+>/g, '')
      .trim();
  }
  return '';
}

/**
 * Fetch a single RSS feed
 */
function fetchFeed(feedUrl) {
  return new Promise((resolve, reject) => {
    const url = new URL(feedUrl);
    const protocol = url.protocol === 'https:' ? https : http;
    
    const options = {
      hostname: url.hostname,
      port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: url.pathname + url.search,
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (RSS Reader)',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*'
      },
      timeout: 10000
    };
    
    const req = protocol.request(options, (res) => {
      if (res.statusCode !== 200) {
        return reject(new Error(`HTTP ${res.statusCode} for ${feedUrl}`));
      }
      
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const items = parseFeed(data, feedUrl);
          resolve({ url: feedUrl, items });
        } catch (e) {
          reject(new Error(`Parse error for ${feedUrl}: ${e.message}`));
        }
      });
    });
    
    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error(`Timeout for ${feedUrl}`));
    });
    
    req.end();
  });
}

/**
 * Calculate simple relevance score for an item
 */
function calculateScore(item, feedUrl) {
  let score = 5; // base score
  
  // Prefer items with descriptions
  if (item.description && item.description.length > 100) score += 2;
  if (item.content && item.content.length > 500) score += 2;
  
  // Prefer shorter, more readable titles (not too long)
  if (item.title && item.title.length < 100) score += 1;
  
  // Boost official/news sources
  if (feedUrl.includes('feeds') || feedUrl.includes('rss') || feedUrl.includes('feed')) score += 1;
  
  return Math.min(score, 10);
}

/**
 * Main function
 */
async function main(options) {
  const { feeds, hours = 72, minScore = 4, format = 'json' } = options;
  const feedList = feeds.split('|').map(f => f.trim()).filter(Boolean);
  
  const cutoffTime = Date.now() - (hours * 60 * 60 * 1000);
  const allItems = [];
  
  // Fetch all feeds (in parallel)
  const results = await Promise.allSettled(
    feedList.map(url => fetchFeed(url))
  );
  
  for (const result of results) {
    if (result.status === 'fulfilled') {
      const { url, items } = result.value;
      
      for (const item of items) {
        const pubTime = parseDate(item.pubDate);
        
        // Filter by date
        if (pubTime && pubTime.getTime() < cutoffTime) continue;
        
        const score = calculateScore(item, url);
        if (score < minScore) continue;
        
        allItems.push({
          title: item.title,
          link: item.link,
          pubDate: item.pubDate,
          description: item.description.substring(0, 300),
          source: url,
          score
        });
      }
    }
  }
  
  // Sort by score (descending), then by date (descending)
  allItems.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score;
    const dateA = parseDate(a.pubDate);
    const dateB = parseDate(b.pubDate);
    return (dateB || 0) - (dateA || 0);
  });
  
  if (format === 'json') {
    return JSON.stringify(allItems, null, 2);
  }
  
  // Text format
  return allItems.map(item => 
    `## ${item.title}\n${item.link}\n${item.description}\nSource: ${item.source}\nScore: ${item.score}\n`
  ).join('\n---\n\n');
}

function parseDate(dateStr) {
  if (!dateStr) return null;
  try {
    return new Date(dateStr);
  } catch (e) {
    return null;
  }
}

module.exports = { main, fetchFeed, parseFeed, calculateScore };
