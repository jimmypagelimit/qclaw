const Database = require('better-sqlite3');
const db = new Database('C:/Users/qujt/.qclaw/workspace/tasks/2026-05-12-long-term-project/album-tracker/data/covers.db');

const withoutCovers = db.prepare('SELECT COUNT(*) as count FROM albums WHERE cover_path IS NULL OR cover_path = ""').get();
const withCovers = db.prepare('SELECT COUNT(*) as count FROM albums WHERE cover_path IS NOT NULL AND cover_path != ""').get();
const total = db.prepare('SELECT COUNT(*) as count FROM albums').get();

console.log('Total albums:', total.count);
console.log('Albums with covers:', withCovers.count);
console.log('Albums without covers:', withoutCovers.count);

db.close();
