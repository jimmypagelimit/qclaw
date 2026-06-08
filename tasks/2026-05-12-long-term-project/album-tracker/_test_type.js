const Database = require('better-sqlite3');
const db = new Database('C:\\Users\\qujt\\.qclaw\\workspace\\_music_latest.db');

// 检查 release_year 类型
const sample = db.prepare('SELECT album_id, release_year, typeof(release_year) as t FROM albums WHERE album_id = 540').get();
console.log('Sample:', sample);

// 检查有哪些类型
const types = db.prepare('SELECT DISTINCT typeof(release_year) as t, release_year, COUNT(*) as c FROM albums GROUP BY t').all();
console.log('Types:', types);

db.close();
