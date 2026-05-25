const initSqlJs = require('sql.js');
const fs = require('fs');

initSqlJs().then(SQL => {
  const buf = fs.readFileSync('G:/原创计划/music');
  const db = new SQL.Database(buf);
  
  // Check cover_image_url values
  const samples = db.exec("SELECT album_id, album_name, artist, cover_image_url FROM albums LIMIT 10");
  console.log('Samples with cover_image_url:', JSON.stringify(samples, null, 2));
  
  // Count null vs non-null
  const nulls = db.exec("SELECT COUNT(*) FROM albums WHERE cover_image_url IS NULL OR cover_image_url = ''");
  const nonNulls = db.exec("SELECT COUNT(*) FROM albums WHERE cover_image_url IS NOT NULL AND cover_image_url != ''");
  console.log('Null/empty:', JSON.stringify(nulls));
  console.log('Non-null:', JSON.stringify(nonNulls));
  
  // Check if non-null values look like local paths or URLs
  const nonNullSamples = db.exec("SELECT DISTINCT SUBSTR(cover_image_url, 1, 30) as prefix FROM albums WHERE cover_image_url IS NOT NULL LIMIT 10");
  console.log('Non-null prefixes:', JSON.stringify(nonNullSamples, null, 2));
  
  db.close();
}).catch(err => console.error(err));
