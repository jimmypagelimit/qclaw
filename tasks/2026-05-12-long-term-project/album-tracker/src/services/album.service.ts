/**
 * 专辑服务层
 * 处理专辑的 CRUD 操作
 */

import { query, queryOne, execute, getTableCount } from '../db/database';
import { Album, CreateAlbumInput, UpdateAlbumInput, QueryAlbumsParams } from '../types';

// 表名映射
const TABLE_NAMES: Record<string, string> = {
  albums: 'albums',
  '2024': 'albums_2024',
  '2025': 'albums_2025',
  '2026': 'albums_2026',
  default: 'albums',
};

/**
 * 获取正确的表名
 */
export function getTableName(table?: string): string {
  if (!table) return 'albums';
  return TABLE_NAMES[table] || table;
}

/**
 * 获取所有专辑（分页）
 */
export function getAlbums(
  params: QueryAlbumsParams = {},
  tableName: string = 'albums'
): Album[] {
  const { keyword, artist, genre, year, limit = 20, offset = 0 } = params;

  let sql = `SELECT * FROM ${tableName} WHERE 1=1`;
  const paramsList: unknown[] = [];

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

  return query<Album>(sql, paramsList);
}

/**
 * 根据 ID 获取专辑
 */
export function getAlbumById(id: number, tableName: string = 'albums'): Album | null {
  return queryOne<Album>(`SELECT * FROM ${tableName} WHERE album_id = ?`, [id]);
}

/**
 * 根据艺术家获取专辑
 */
export function getAlbumsByArtist(
  artistName: string,
  tableName: string = 'albums'
): Album[] {
  return query<Album>(
    `SELECT * FROM ${tableName} WHERE artist LIKE ? ORDER BY album_id DESC`,
    [`%${artistName}%`]
  );
}

/**
 * 搜索专辑（多表搜索）
 */
export function searchAlbums(
  keyword: string,
  tables: string[] = ['albums', 'albums_2024', 'albums_2025', 'albums_2026']
): Album[] {
  const results: Album[] = [];

  for (const table of tables) {
    if (!['albums', 'albums_2024', 'albums_2025', 'albums_2026'].includes(table)) {
      continue;
    }
    const albums = query<Album>(
      `SELECT *, '${table}' as source_table FROM ${table} 
       WHERE album_name LIKE ? OR artist LIKE ?`,
      [`%${keyword}%`, `%${keyword}%`]
    );
    results.push(...albums);
  }

  // 按 album_id 降序排序
  return results.sort((a, b) => b.album_id - a.album_id);
}

/**
 * 添加专辑
 */
export function addAlbum(input: CreateAlbumInput, tableName: string = 'albums'): Album {
  const {
    album_name,
    artist,
    country = null,
    region = null,
    genre = null,
    rating = null,
    description = null,
    is_compilation = 0,
    first_listen_date = new Date().toISOString().split('T')[0],
    total_listen_count = 1,
    release_company = null,
    cover_image_url = null,
    duration = null,
    composition_score = null,
    lyrics_meaning_score = null,
    creativity_score = null,
    arrangement_score = null,
    vocal_performance_score = null,
    instrumental_performance_score = null,
    sincerity_score = null,
    subjective_score = null,
    overall_score = null,
    release_year = null,
    style = null,
    producer = null,
  } = input;

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

  execute(sql, params);

  // 获取刚插入的记录
  const lastId = queryOne<{ id: number }>('SELECT last_insert_rowid() as id');
  return getAlbumById(lastId!.id, tableName)!;
}

/**
 * 更新专辑
 */
export function updateAlbum(
  id: number,
  input: UpdateAlbumInput,
  tableName: string = 'albums'
): Album | null {
  const fields: string[] = [];
  const params: unknown[] = [];

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
  execute(sql, params);

  return getAlbumById(id, tableName);
}

/**
 * 删除专辑
 */
export function deleteAlbum(id: number, tableName: string = 'albums'): boolean {
  const sql = `DELETE FROM ${tableName} WHERE album_id = ?`;
  const affected = execute(sql, [id]);
  return affected > 0;
}

/**
 * 记录收听（增加收听次数）
 */
export function recordListen(
  id: number,
  count: number = 1,
  tableName: string = 'albums'
): Album | null {
  const album = getAlbumById(id, tableName);
  if (!album) {
    return null;
  }

  const newCount = album.total_listen_count + count;
  const sql = `UPDATE ${tableName} SET total_listen_count = ? WHERE album_id = ?`;
  execute(sql, [newCount, id]);

  // 如果是首次收听，设置日期
  if (!album.first_listen_date) {
    const today = new Date().toISOString().split('T')[0];
    execute(`UPDATE ${tableName} SET first_listen_date = ? WHERE album_id = ?`, [today, id]);
  }

  return getAlbumById(id, tableName);
}

/**
 * 获取所有表的记录数
 */
export function getAllTableCounts(): Record<string, number> {
  const tableNames = ['albums', 'albums_2024', 'albums_2025', 'albums_2026'];
  const tables: Record<string, number> = {};
  for (const table of tableNames) {
    tables[table] = getTableCount(table);
  }
  return tables;
}

/**
 * 获取统计概览（只查询指定表）
 */
export function getStatsOverview(tableName: string = 'albums'): {
  tableName: string;
  total: number;
  totalListens: number;
  avgListens: number;
  maxListen: { album: Album; count: number } | null;
} {
  const total = getTableCount(tableName);
  const listens = query<{ total: number }>(`SELECT SUM(total_listen_count) as total FROM ${tableName}`);
  const totalListens = listens[0]?.total || 0;

  // 找出该表收听最多的专辑
  const topAlbum = queryOne<Album>(
    `SELECT * FROM ${tableName} ORDER BY total_listen_count DESC LIMIT 1`
  );

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
export function getTopAlbums(
  limit: number = 10,
  tables: string[] = ['albums', 'albums_2024', 'albums_2025', 'albums_2026']
): Array<Album & { source_table: string }> {
  const results: Array<Album & { source_table: string }> = [];

  for (const table of tables) {
    if (!['albums', 'albums_2024', 'albums_2025', 'albums_2026'].includes(table)) {
      continue;
    }
    const albums = query<Album & { source_table: string }>(
      `SELECT *, '${table}' as source_table FROM ${table} ORDER BY total_listen_count DESC LIMIT ?`,
      [limit]
    );
    results.push(...albums);
  }

  // 合并并排序
  return results.sort((a, b) => b.total_listen_count - a.total_listen_count).slice(0, limit);
}

/**
 * 获取风格分布
 */
export function getGenreStats(
  tableName: string = 'albums',
  limit: number = 10
): Array<{ genre: string; count: number; percentage: number }> {
  const total = getTableCount(tableName);

  const results = query<{ genre: string; count: number }>(
    `SELECT genre, COUNT(*) as count FROM ${tableName} 
     WHERE genre IS NOT NULL AND genre != '' 
     GROUP BY genre ORDER BY count DESC LIMIT ?`,
    [limit]
  );

  return results.map((r) => ({
    genre: r.genre || '未知',
    count: r.count,
    percentage: Math.round((r.count / total) * 1000) / 10,
  }));
}

/**
 * 获取国家分布
 */
export function getCountryStats(
  tableName: string = 'albums',
  limit: number = 10
): Array<{ country: string; count: number; percentage: number }> {
  const total = getTableCount(tableName);

  const results = query<{ country: string; count: number }>(
    `SELECT country, COUNT(*) as count FROM ${tableName} 
     WHERE country IS NOT NULL AND country != '' 
     GROUP BY country ORDER BY count DESC LIMIT ?`,
    [limit]
  );

  return results.map((r) => ({
    country: r.country || '未知',
    count: r.count,
    percentage: Math.round((r.count / total) * 1000) / 10,
  }));
}

/**
 * 获取年份分布（发行年份）
 */
export function getYearStats(
  tableName: string = 'albums',
  limit: number = 20
): Array<{ year: string; count: number }> {
  return query<{ year: string; count: number }>(
    `SELECT release_year as year, COUNT(*) as count FROM ${tableName} 
     WHERE release_year IS NOT NULL AND release_year != '' 
     GROUP BY release_year ORDER BY release_year DESC LIMIT ?`,
    [limit]
  );
}
