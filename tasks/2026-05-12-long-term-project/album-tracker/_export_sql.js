const Module = require('module');
const path = require('path');
// Add album-tracker node_modules to require path
Module.globalPaths.push('C:/Users/qujt/.qclaw/workspace/tasks/2026-05-12-long-term-project/album-tracker/node_modules');

const sqlite3 = require('better-sqlite3');
const fs = require('fs');
const db = sqlite3('C:/Users/qujt/.qclaw/workspace/_music_latest.db');
const tables = ['albums', 'artists', 'listen_history', 'genres', 'styles', 'sub_genres'];
let out = '-- Album Tracker Database Export\n-- Generated: ' + new Date().toISOString() + '\n\n';
for (const t of tables) {
  try {
    const exists = db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name=?").get(t);
    if (!exists) continue;
    const count = db.prepare(`SELECT COUNT(*) as c FROM ${t}`).get().c;
    out += `-- === ${t} (${count} rows) ===\n`;
    const cols = db.prepare(`PRAGMA table_info(${t})`).all();
    const colNames = cols.map(c => c.name);
    const rows = db.prepare(`SELECT * FROM ${t}`).all();
    if (rows.length === 0) continue;
    for (const row of rows) {
      const vals = colNames.map(c => {
        const v = row[c];
        if (v === null || v === undefined) return 'NULL';
        if (typeof v === 'number') return v;
        return "'" + String(v).replace(/'/g, "''") + "'";
      });
      out += `INSERT INTO ${t} (${colNames.join(', ')}) VALUES (${vals.join(', ')});\n`;
    }
    out += '\n';
  } catch (e) { console.log('Table error', t, e.message); }
}
db.close();
fs.writeFileSync('C:/Users/qujt/.qclaw/workspace/tasks/2026-05-12-long-term-project/album-tracker/database.sql', out, 'utf8');
console.log('Wrote database.sql:', out.length, 'bytes');
