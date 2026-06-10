const sql = require('sql.js');
const fs = require('fs');

const DB_PATH = 'C:/Users/qujt/.qclaw/workspace/_music_latest.db';

// Debug: check if file exists
if (!fs.existsSync(DB_PATH)) {
    console.error('Database not found at:', DB_PATH);
    process.exit(1);
}

// Load database
const fileBuffer = fs.readFileSync(DB_PATH);
const db = new sql.Database(fileBuffer);

// Get albums without covers
const result = db.exec(`
    SELECT album_id, album_name, artist 
    FROM albums 
    WHERE cover_image_url IS NULL OR cover_image_url = "" 
    ORDER BY total_listen_count DESC, rating DESC
`);

if (result.length === 0 || !result[0].values) {
    console.log('No albums without covers found');
    process.exit(0);
}

const albums = result[0].values;
console.log(`Total albums without covers: ${albums.length}`);
console.log('='.repeat(80));

// Mark each as UNAVAILABLE
const updateStmt = db.prepare('UPDATE albums SET cover_image_url = "UNAVAILABLE" WHERE album_id = ?');
const yearlyTables = ['albums_2024', 'albums_2025', 'albums_2026'];

for (const [albumId, albumName, artist] of albums) {
    console.log(`${albumId}: ${artist} - ${albumName}`);
    
    // Update main table
    updateStmt.run([albumId]);
    
    // Update yearly tables if they exist
    for (const table of yearlyTables) {
        try {
            db.run(`UPDATE ${table} SET cover_image_url = "UNAVAILABLE" WHERE album_id = ?`, [albumId]);
        } catch (e) {
            // Table might not exist or album not in table
        }
    }
}

updateStmt.free();

// Save database
const data = db.export();
fs.writeFileSync(DB_PATH, Buffer.from(data));
console.log('='.repeat(80));
console.log(`Marked ${albums.length} albums as UNAVAILABLE`);
console.log('Database saved to', DB_PATH);

db.close();
