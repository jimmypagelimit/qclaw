"use strict";
/**
 * 专辑服务层
 * 处理专辑的 CRUD 操作
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.getTableName = getTableName;
exports.getAlbums = getAlbums;
exports.getAlbumById = getAlbumById;
exports.getAlbumsByArtist = getAlbumsByArtist;
exports.searchAlbums = searchAlbums;
exports.addAlbum = addAlbum;
exports.updateAlbum = updateAlbum;
exports.deleteAlbum = deleteAlbum;
exports.recordListen = recordListen;
exports.getAllTableCounts = getAllTableCounts;
exports.getStatsOverview = getStatsOverview;
exports.getTopAlbums = getTopAlbums;
exports.getGenreStats = getGenreStats;
exports.getCountryStats = getCountryStats;
exports.getYearStats = getYearStats;
const database_1 = require("../db/database");
// 表名映射
const TABLE_NAMES = {
    albums: 'albums',
    '2024': 'albums_2024',
    '2025': 'albums_2025',
    '2026': 'albums_2026',
    default: 'albums',
};
/**
 * 获取正确的表名
 */
function getTableName(table) {
    if (!table)
        return 'albums';
    return TABLE_NAMES[table] || table;
}
/**
 * 获取所有专辑（分页）
 */
function getAlbums(params = {}, tableName = 'albums') {
    const { keyword, artist, genre, year, limit = 20, offset = 0 } = params;
    let sql = `SELECT * FROM ${tableName} WHERE 1=1`;
    const paramsList = [];
    if (keyword) {
        sql += ` AND (album_name LIKE ? OR artist LIKE ?)`;
        paramsList.push(`%${keyword}%`, `%${keyword}%`);
    }
    if (artist) {
        sql += ` AND artist LIKE ?`;
        paramsList.push(`%${artist}%`);
    }
    if (genre) {
        sql += ` AND genre LIKE ?`;
        paramsList.push(`%${genre}%`);
    }
    if (year) {
        sql += ` AND release_year = ?`;
        paramsList.push(year);
    }
    sql += ` ORDER BY album_id DESC LIMIT ? OFFSET ?`;
    paramsList.push(limit, offset);
    return (0, database_1.query)(sql, paramsList);
}
/**
 * 根据 ID 获取专辑
 */
function getAlbumById(id, tableName = 'albums') {
    return (0, database_1.queryOne)(`SELECT * FROM ${tableName} WHERE album_id = ?`, [id]);
}
/**
 * 根据艺术家获取专辑
 */
function getAlbumsByArtist(artistName, tableName = 'albums') {
    return (0, database_1.query)(`SELECT * FROM ${tableName} WHERE artist LIKE ? ORDER BY album_id DESC`, [`%${artistName}%`]);
}
/**
 * 搜索专辑（多表搜索）
 */
function searchAlbums(keyword, tables = ['albums', 'albums_2024', 'albums_2025', 'albums_2026']) {
    const results = [];
    for (const table of tables) {
        if (!['albums', 'albums_2024', 'albums_2025', 'albums_2026'].includes(table)) {
            continue;
        }
        const albums = (0, database_1.query)(`SELECT *, '${table}' as source_table FROM ${table} 
       WHERE album_name LIKE ? OR artist LIKE ?`, [`%${keyword}%`, `%${keyword}%`]);
        results.push(...albums);
    }
    // 按 album_id 降序排序
    return results.sort((a, b) => b.album_id - a.album_id);
}
/**
 * 添加专辑
 */
function addAlbum(input, tableName = 'albums') {
    const { album_name, artist, country = null, region = null, genre = null, rating = null, description = null, is_compilation = 0, first_listen_date = new Date().toISOString().split('T')[0], total_listen_count = 1, release_company = null, cover_image_url = null, duration = null, composition_score = null, lyrics_meaning_score = null, creativity_score = null, arrangement_score = null, vocal_performance_score = null, instrumental_performance_score = null, sincerity_score = null, subjective_score = null, overall_score = null, release_year = null, style = null, producer = null, } = input;
    const sql = `
    INSERT INTO ${tableName} (
      album_name, artist, country, region, genre, rating, description,
      is_compilation, first_listen_date, total_listen_count, release_company,
      cover_image_url, duration, composition_score, lyrics_meaning_score,
      creativity_score, arrangement_score, vocal_performance_score,
      instrumental_performance_score, sincerity_score, subjective_score,
      overall_score, release_year, style, producer
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `;
    const params = [
        album_name, artist, country, region, genre, rating, description,
        is_compilation, first_listen_date, total_listen_count, release_company,
        cover_image_url, duration, composition_score, lyrics_meaning_score,
        creativity_score, arrangement_score, vocal_performance_score,
        instrumental_performance_score, sincerity_score, subjective_score,
        overall_score, release_year, style, producer,
    ];
    (0, database_1.execute)(sql, params);
    // 获取刚插入的记录
    const lastId = (0, database_1.queryOne)('SELECT last_insert_rowid() as id');
    return getAlbumById(lastId.id, tableName);
}
/**
 * 更新专辑
 */
function updateAlbum(id, input, tableName = 'albums') {
    const fields = [];
    const params = [];
    for (const [key, value] of Object.entries(input)) {
        // 排除 album_id 和 undefined 值
        if (key !== 'album_id' && value !== undefined) {
            fields.push(`${key} = ?`);
            params.push(value);
        }
    }
    if (fields.length === 0) {
        return getAlbumById(id, tableName);
    }
    params.push(id);
    const sql = `UPDATE ${tableName} SET ${fields.join(', ')} WHERE album_id = ?`;
    (0, database_1.execute)(sql, params);
    return getAlbumById(id, tableName);
}
/**
 * 删除专辑
 */
function deleteAlbum(id, tableName = 'albums') {
    const sql = `DELETE FROM ${tableName} WHERE album_id = ?`;
    const affected = (0, database_1.execute)(sql, [id]);
    return affected > 0;
}
/**
 * 记录收听（增加收听次数）
 */
function recordListen(id, count = 1, tableName = 'albums') {
    const album = getAlbumById(id, tableName);
    if (!album) {
        return null;
    }
    const newCount = album.total_listen_count + count;
    const sql = `UPDATE ${tableName} SET total_listen_count = ? WHERE album_id = ?`;
    (0, database_1.execute)(sql, [newCount, id]);
    // 如果是首次收听，设置日期
    if (!album.first_listen_date) {
        const today = new Date().toISOString().split('T')[0];
        (0, database_1.execute)(`UPDATE ${tableName} SET first_listen_date = ? WHERE album_id = ?`, [today, id]);
    }
    return getAlbumById(id, tableName);
}
/**
 * 获取所有表的记录数
 */
function getAllTableCounts() {
    const tableNames = ['albums', 'albums_2024', 'albums_2025', 'albums_2026'];
    const tables = {};
    for (const table of tableNames) {
        tables[table] = (0, database_1.getTableCount)(table);
    }
    return tables;
}
/**
 * 获取统计概览（只查询指定表）
 */
function getStatsOverview(tableName = 'albums') {
    const total = (0, database_1.getTableCount)(tableName);
    const listens = (0, database_1.query)(`SELECT SUM(total_listen_count) as total FROM ${tableName}`);
    const totalListens = listens[0]?.total || 0;
    // 找出该表收听最多的专辑
    const topAlbum = (0, database_1.queryOne)(`SELECT * FROM ${tableName} ORDER BY total_listen_count DESC LIMIT 1`);
    return {
        tableName,
        total,
        totalListens,
        avgListens: total > 0 ? Math.round((totalListens / total) * 10) / 10 : 0,
        maxListen: topAlbum ? { album: topAlbum, count: topAlbum.total_listen_count } : null,
    };
}
/**
 * 获取收听排行榜
 */
function getTopAlbums(limit = 10, tables = ['albums', 'albums_2024', 'albums_2025', 'albums_2026']) {
    const results = [];
    for (const table of tables) {
        if (!['albums', 'albums_2024', 'albums_2025', 'albums_2026'].includes(table)) {
            continue;
        }
        const albums = (0, database_1.query)(`SELECT *, '${table}' as source_table FROM ${table} ORDER BY total_listen_count DESC LIMIT ?`, [limit]);
        results.push(...albums);
    }
    // 合并并排序
    return results.sort((a, b) => b.total_listen_count - a.total_listen_count).slice(0, limit);
}
/**
 * 获取风格分布
 */
function getGenreStats(tableName = 'albums', limit = 10) {
    const total = (0, database_1.getTableCount)(tableName);
    const results = (0, database_1.query)(`SELECT genre, COUNT(*) as count FROM ${tableName} 
     WHERE genre IS NOT NULL AND genre != '' 
     GROUP BY genre ORDER BY count DESC LIMIT ?`, [limit]);
    return results.map((r) => ({
        genre: r.genre || '未知',
        count: r.count,
        percentage: Math.round((r.count / total) * 1000) / 10,
    }));
}
/**
 * 获取国家分布
 */
function getCountryStats(tableName = 'albums', limit = 10) {
    const total = (0, database_1.getTableCount)(tableName);
    const results = (0, database_1.query)(`SELECT country, COUNT(*) as count FROM ${tableName} 
     WHERE country IS NOT NULL AND country != '' 
     GROUP BY country ORDER BY count DESC LIMIT ?`, [limit]);
    return results.map((r) => ({
        country: r.country || '未知',
        count: r.count,
        percentage: Math.round((r.count / total) * 1000) / 10,
    }));
}
/**
 * 获取年份分布（发行年份）
 */
function getYearStats(tableName = 'albums', limit = 20) {
    return (0, database_1.query)(`SELECT release_year as year, COUNT(*) as count FROM ${tableName} 
     WHERE release_year IS NOT NULL AND release_year != '' 
     GROUP BY release_year ORDER BY release_year DESC LIMIT ?`, [limit]);
}
