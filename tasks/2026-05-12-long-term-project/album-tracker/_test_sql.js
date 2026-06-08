const Database = require('better-sqlite3');
const db = new Database('C:\\Users\\qujt\\.qclaw\\workspace\\_music_latest.db');
// 测试新 SQL
const sql = `SELECT a.*, COALESCE(lh.cnt, 0) as year_listen_count
             FROM albums a
             LEFT JOIN (SELECT album_id, COUNT(id) as cnt FROM listen_history WHERE listen_year = ? GROUP BY album_id) lh ON a.album_id = lh.album_id
             WHERE a.release_year = ?`;
const countSql = `SELECT COUNT(*) as total FROM albums a WHERE a.release_year = ?`;

const count = db.prepare(countSql).get(2026);
console.log('Count:', count);

const rows = db.prepare(sql).all(2026, 2026);
console.log('Rows:', rows.length);
for (const r of rows.slice(0, 3)) {
    console.log(`  ${r.album_name} - ${r.artist} (yl:${r.year_listen_count})`);
}
db.close();
