const Database = require('better-sqlite3');
const db = new Database('_music_latest.db');

const row = db.prepare(`SELECT COUNT(*) as total, SUM(CASE WHEN cover_image_url IS NULL OR cover_image_url = '' THEN 1 ELSE 0 END) as without_covers FROM albums`).get();
console.log('Total albums:', row.total);
console.log('Without covers:', row.without_covers);

const albums = db.prepare(`SELECT album_id as id, album_name as name, artist FROM albums WHERE cover_image_url IS NULL OR cover_image_url = '' LIMIT 20`).all();
console.log('\nFirst 20 albums without covers:');
albums.forEach((a, i) => console.log(`[${i+1}] ${a.artist} - ${a.name}`));

db.close();
