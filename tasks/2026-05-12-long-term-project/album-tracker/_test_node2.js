const Database = require('better-sqlite3');
const db = new Database('C:\\Users\\qujt\\.qclaw\\workspace\\_music_latest.db');
const r = db.prepare('SELECT COUNT(*) as c FROM albums WHERE release_year = 2026').get();
console.log('2026 albums:', r);
const r2 = db.prepare('SELECT album_name, artist, total_listen_count FROM albums WHERE album_id = 540').get();
console.log('Paul:', r2);
db.close();
