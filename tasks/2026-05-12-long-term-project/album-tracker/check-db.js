const Database = require('better-sqlite3');
const db = new Database('data/covers.db');

const total = db.prepare('SELECT COUNT(*) as count FROM albums').get();
const withCovers = db.prepare("SELECT COUNT(*) as count FROM albums WHERE cover_path IS NOT NULL AND cover_path != ''").get();
const withoutCovers = db.prepare("SELECT COUNT(*) as count FROM albums WHERE cover_path IS NULL OR cover_path = ''").get();

console.log('Total albums:', total.count);
console.log('Albums with covers:', withCovers.count);
console.log('Albums without covers:', withoutCovers.count);

// Show a few albums without covers
const samples = db.prepare("SELECT id, name, artist FROM albums WHERE cover_path IS NULL OR cover_path = '' LIMIT 5").all();
console.log('\nSample albums without covers:');
samples.forEach(a => console.log(`  - ${a.name} by ${a.artist} (id: ${a.id})`));

db.close();
