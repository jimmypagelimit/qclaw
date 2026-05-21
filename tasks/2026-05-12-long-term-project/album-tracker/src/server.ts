#!/usr/bin/env node

/**
 * 专辑数据库 Web 服务器
 * 用法: node dist/server.js
 * 默认端口: 3456
 *
 * 核心逻辑：所有写操作（新增/收听/编辑/删除）都同步操作年份表 + 总表
 * 跨表关联依据：album_name + artist
 */

import express from 'express';
import { initDatabase, closeDatabase, query, queryOne, execute, getTableCount } from './db/database';
import path from 'path';

const app = express();
const PORT = process.env.PORT || 3456;

// 中间件
app.use(express.json());
app.use(express.static(path.join(__dirname, '..', 'public')));
// 封面图片静态服务
app.use('/covers', express.static(path.join(__dirname, '..', 'covers')));

// ==================== 工具函数 ====================

/** 获取当前年份 */
function currentYear(): number {
  return new Date().getFullYear();
}

/** 根据年份获取年表名 */
function yearTable(year: number): string {
  return `albums_${year}`;
}

/** 获取所有年表名 */
function getYearTables(): string[] {
  return ['albums_2024', 'albums_2025', 'albums_2026'];
}

/** 在指定表中按 album_name + artist 查找专辑 */
function findAlbumByKeys(table: string, albumName: string, artistName: string): any {
  return queryOne(
    `SELECT * FROM ${table} WHERE album_name = ? AND artist = ?`,
    [albumName, artistName]
  );
}

/** 在指定表中插入专辑记录 */
function insertAlbumInto(table: string, data: Record<string, any>) {
  const fields = [
    'album_name', 'artist', 'country', 'region', 'genre', 'rating',
    'description', 'is_compilation', 'first_listen_date', 'total_listen_count',
    'release_company', 'cover_image_url', 'duration', 'release_year', 'style', 'producer'
  ];
  const values = fields.map(f => data[f] ?? null);
  // 确保 total_listen_count 至少为 1
  const tlcIndex = fields.indexOf('total_listen_count');
  if (!values[tlcIndex]) values[tlcIndex] = 1;
  // 确保 first_listen_date 有值
  const fldIndex = fields.indexOf('first_listen_date');
  if (!values[fldIndex]) values[fldIndex] = new Date().toISOString().split('T')[0];

  execute(
    `INSERT INTO ${table} (${fields.join(', ')}) VALUES (${fields.map(() => '?').join(', ')})`,
    values
  );
}

// ==================== API 路由 ====================

// 年度收听排行（各年表收听次数 Top 3）
app.get('/api/top-by-year', async (_req, res) => {
  try {
    const result: Record<string, any> = {};
    for (const ytbl of getYearTables()) {
      const year = parseInt(ytbl.replace('albums_', ''));
      const top = query(
        `SELECT album_name, artist, total_listen_count, cover_image_url
         FROM ${ytbl} ORDER BY total_listen_count DESC LIMIT 3`
      );
      result[String(year)] = top;
    }
    res.json(result);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// 仪表盘统计
app.get('/api/stats', async (_req, res) => {
  try {
    const tables = ['albums', ...getYearTables()];
    const result: Record<string, any> = { tables: {} };

    for (const table of tables) {
      const count = getTableCount(table);
      const listens = query<{ total: number }>(`SELECT COALESCE(SUM(total_listen_count), 0) as total FROM ${table}`);
      const topAlbum = queryOne(
        `SELECT * FROM ${table} ORDER BY total_listen_count DESC LIMIT 1`
      );
      result.tables[table] = {
        count,
        totalListens: listens[0]?.total || 0,
        topAlbum: topAlbum || null,
      };
    }

    const genres = query<{ genre: string; count: number }>(
      `SELECT genre, COUNT(*) as count FROM albums WHERE genre IS NOT NULL AND genre != '' GROUP BY genre ORDER BY count DESC LIMIT 10`
    );
    const countries = query<{ country: string; count: number }>(
      `SELECT country, COUNT(*) as count FROM albums WHERE country IS NOT NULL AND country != '' GROUP BY country ORDER BY count DESC LIMIT 10`
    );

    // 各年份收听次数（从年份表汇总）
    const yearListens: Record<string, number> = {};
    for (const ytbl of getYearTables()) {
      const year = parseInt(ytbl.replace('albums_', ''));
      const r = query<{ total: number }>(
        `SELECT COALESCE(SUM(total_listen_count), 0) as total FROM ${ytbl}`
      );
      yearListens[String(year)] = r[0]?.total || 0;
    }

    result.genres = genres;
    result.countries = countries;
    result.yearListens = yearListens;

    res.json(result);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// 搜索专辑
app.get('/api/albums', async (req, res) => {
  try {
    const {
      search, genre, country, artist,
      table = 'albums', limit = 20, offset = 0,
      sort = 'listen',  // listen | score | name | artist | year
      dir = 'desc',     // asc | desc
    } = req.query;

    let sql = `SELECT * FROM ${table} WHERE 1=1`;
    const params: any[] = [];

    if (search) {
      sql += ` AND (album_name LIKE ? OR artist LIKE ?)`;
      params.push(`%${search}%`, `%${search}%`);
    }
    if (genre) { sql += ` AND genre LIKE ?`; params.push(`%${genre}%`); }
    if (country) { sql += ` AND country = ?`; params.push(country); }
    if (artist) { sql += ` AND artist LIKE ?`; params.push(`%${artist}%`); }

    const countResult = query<{ total: number }>(
      sql.replace('SELECT *', 'SELECT COUNT(*) as total'), params
    );
    const total = countResult[0]?.total || 0;

    // 排序映射
    const sortMap: Record<string, string> = {
      listen: 'total_listen_count',
      score:  'overall_score',
      name:   'album_name',
      artist: 'artist',
      year:   'release_year',
    };
    const direction = dir === 'asc' ? 'ASC' : 'DESC';
    const sortCol = sortMap[sort as string] || 'total_listen_count';
    // NULL 值排最后
    sql += ` ORDER BY ${sortCol} IS NULL, ${sortCol} ${direction} LIMIT ? OFFSET ?`;
    params.push(Number(limit), Number(offset));

    const albums = query(sql, params);
    res.json({ albums, total, limit: Number(limit), offset: Number(offset) });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// 专辑详情
app.get('/api/albums/:id', async (req, res) => {
  try {
    const { table = 'albums' } = req.query;
    const album = queryOne(
      `SELECT * FROM ${table} WHERE album_id = ?`,
      [Number(req.params.id)]
    );
    if (!album) { res.status(404).json({ error: '专辑未找到' }); return; }
    res.json(album);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// 艺术家专辑列表
app.get('/api/artist/:name', async (req, res) => {
  try {
    const { table = 'albums', limit = 50 } = req.query;
    const albums = query(
      `SELECT * FROM ${table} WHERE artist LIKE ? ORDER BY total_listen_count DESC LIMIT ?`,
      [`%${req.params.name}%`, Number(limit)]
    );
    res.json(albums);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// 排行榜
app.get('/api/top', async (req, res) => {
  try {
    const { limit = 10, year, table } = req.query;
    let tableName = 'albums';
    if (table) tableName = table as string;
    else if (year) tableName = `albums_${year}`;

    const albums = query(
      `SELECT * FROM ${tableName} ORDER BY total_listen_count DESC LIMIT ?`,
      [Number(limit)]
    );
    res.json({ tableName, albums });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// 风格分布
app.get('/api/genres', async (req, res) => {
  try {
    const { table = 'albums', limit = 20 } = req.query;
    const genres = query<{ genre: string; count: number }>(
      `SELECT genre, COUNT(*) as count FROM ${table} WHERE genre IS NOT NULL AND genre != '' GROUP BY genre ORDER BY count DESC LIMIT ?`,
      [Number(limit)]
    );
    res.json(genres);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// 国家分布
app.get('/api/countries', async (req, res) => {
  try {
    const { table = 'albums', limit = 20 } = req.query;
    const countries = query<{ country: string; count: number }>(
      `SELECT country, COUNT(*) as count FROM ${table} WHERE country IS NOT NULL AND country != '' GROUP BY country ORDER BY count DESC LIMIT ?`,
      [Number(limit)]
    );
    res.json(countries);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// ==================== 写操作（双表同步） ====================

/**
 * 新增专辑
 * body: { ..., year: 2026 }
 * 逻辑：
 *   1. 写入年份表 albums_YYYY
 *   2. 写入总表 albums（如已存在则只 +1 total_listen_count）
 */
app.post('/api/albums', async (req, res) => {
  try {
    const {
      album_name, artist, country, region, genre, rating,
      description, is_compilation, first_listen_date, total_listen_count,
      release_company, cover_image_url, duration, release_year, style, producer,
      year = currentYear(),
    } = req.body;

    if (!album_name || !artist) {
      res.status(400).json({ error: 'album_name 和 artist 为必填项' });
      return;
    }

    const yr = Number(year);
    const yt = yearTable(yr);

    const record = {
      album_name, artist, country, region, genre, rating,
      description, is_compilation, first_listen_date, total_listen_count,
      release_company, cover_image_url, duration, release_year, style, producer,
    };

    // 1. 写入年份表（判重：album_name + artist）
    const existingInYear = findAlbumByKeys(yt, album_name, artist);
    if (existingInYear) {
      // 年份表已存在，只 +1
      const newCount = existingInYear.total_listen_count + 1;
      execute(`UPDATE ${yt} SET total_listen_count = ? WHERE album_id = ?`, [newCount, existingInYear.album_id]);
    } else {
      // 年份表不存在，新增
      insertAlbumInto(yt, record);
    }

    // 2. 写入总表 albums（判重：album_name + artist）
    const existingInTotal = findAlbumByKeys('albums', album_name, artist);
    if (existingInTotal) {
      // 总表已存在，只 +1
      const newCount = existingInTotal.total_listen_count + 1;
      execute(`UPDATE albums SET total_listen_count = ? WHERE album_id = ?`, [newCount, existingInTotal.album_id]);
    } else {
      // 总表不存在，新增
      insertAlbumInto('albums', record);
    }

    const result = findAlbumByKeys('albums', album_name, artist);
    res.json({ success: true, album: result, yearTable: yt });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * 更新专辑
 * body: { album_name, artist, ..., year: 2026 }
 * 逻辑：用 album_name + artist 在两张表里找到对应记录，分别更新
 */
app.put('/api/albums/:id', async (req, res) => {
  try {
    const sourceTable = req.query.table as string || 'albums';
    const id = Number(req.params.id);
    const fields = req.body;
    const year = fields.year || currentYear();
    delete fields.year; // 不写入 year 字段

    const allowedFields = [
      'album_name', 'artist', 'country', 'region', 'genre', 'rating',
      'description', 'is_compilation', 'first_listen_date', 'total_listen_count',
      'release_company', 'cover_image_url', 'duration', 'release_year', 'style', 'producer'
    ];

    const setClauses: string[] = [];
    const params: any[] = [];
    for (const [key, value] of Object.entries(fields)) {
      if (allowedFields.includes(key)) {
        setClauses.push(`${key} = ?`);
        params.push(value);
      }
    }
    if (setClauses.length === 0) {
      res.status(400).json({ error: '没有有效的更新字段' });
      return;
    }

    // 获取原始记录，用于跨表关联
    const original = queryOne(`SELECT * FROM ${sourceTable} WHERE album_id = ?`, [id]);
    if (!original) { res.status(404).json({ error: '专辑未找到' }); return; }

    // 用 album_name + artist 在两张表里都找到并更新
    const lookupName = fields.album_name || original.album_name;
    const lookupArtist = fields.artist || original.artist;

    // 更新来源表
    params.push(id);
    execute(`UPDATE ${sourceTable} SET ${setClauses.join(', ')} WHERE album_id = ?`, params);

    // 更新另一张表
    const otherTable = sourceTable === 'albums' ? yearTable(Number(year)) : 'albums';
    const otherAlbum = findAlbumByKeys(otherTable, original.album_name, original.artist);
    if (otherAlbum) {
      const otherParams = setClauses.map(clause => {
        const field = clause.split(' = ')[0];
        return fields[field];
      });
      otherParams.push(otherAlbum.album_id);
      execute(`UPDATE ${otherTable} SET ${setClauses.join(', ')} WHERE album_id = ?`, otherParams);
    }

    const updated = queryOne(`SELECT * FROM ${sourceTable} WHERE album_id = ?`, [id]);
    res.json({ success: true, album: updated });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * 删除专辑
 * 逻辑：从总表和所有年份表中删除（通过 album_name + artist 关联）
 */
app.delete('/api/albums/:id', async (req, res) => {
  try {
    const sourceTable = req.query.table as string || 'albums';
    const id = Number(req.params.id);

    const album = queryOne(`SELECT * FROM ${sourceTable} WHERE album_id = ?`, [id]);
    if (!album) { res.status(404).json({ error: '专辑未找到' }); return; }

    // 从来源表删除
    execute(`DELETE FROM ${sourceTable} WHERE album_id = ?`, [id]);

    // 从另一张表删除（如果来源是年份表，也删总表；如果来源是总表，也删所有年份表）
    if (sourceTable === 'albums') {
      for (const yt of getYearTables()) {
        const found = findAlbumByKeys(yt, album.album_name, album.artist);
        if (found) execute(`DELETE FROM ${yt} WHERE album_id = ?`, [found.album_id]);
      }
    } else {
      const found = findAlbumByKeys('albums', album.album_name, album.artist);
      if (found) execute(`DELETE FROM albums WHERE album_id = ?`, [found.album_id]);
    }

    res.json({ success: true, deleted: album });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * 记录收听
 * body: { count: 1, year: 2026, table: 'albums' }
 * 逻辑：
 *   1. 在年份表中找到该专辑（album_name + artist），如不存在则新增，+1
 *   2. 在总表中找到该专辑，+1
 */
app.post('/api/albums/:id/listen', async (req, res) => {
  try {
    const sourceTable = req.query.table as string || 'albums';
    const id = Number(req.params.id);
    const { count = 1, year = currentYear() } = req.body;
    const yr = Number(year);
    const yt = yearTable(yr);

    // 从来源表获取专辑信息
    const album = queryOne(`SELECT * FROM ${sourceTable} WHERE album_id = ?`, [id]);
    if (!album) { res.status(404).json({ error: '专辑未找到' }); return; }

    const albumName = album.album_name;
    const artistName = album.artist;

    // 1. 更新年份表
    const yearAlbum = findAlbumByKeys(yt, albumName, artistName);
    if (yearAlbum) {
      // 年份表中已存在，+1
      const newCount = yearAlbum.total_listen_count + Number(count);
      execute(`UPDATE ${yt} SET total_listen_count = ? WHERE album_id = ?`, [newCount, yearAlbum.album_id]);
    } else {
      // 年份表中不存在，新增记录
      insertAlbumInto(yt, { ...album, total_listen_count: Number(count) });
    }

    // 2. 更新总表 albums
    const totalAlbum = findAlbumByKeys('albums', albumName, artistName);
    if (totalAlbum) {
      const newCount = totalAlbum.total_listen_count + Number(count);
      execute(`UPDATE albums SET total_listen_count = ? WHERE album_id = ?`, [newCount, totalAlbum.album_id]);
      // 设置首次收听日期（如果为空）
      if (!totalAlbum.first_listen_date) {
        const today = new Date().toISOString().split('T')[0];
        execute(`UPDATE albums SET first_listen_date = ? WHERE album_id = ?`, [today, totalAlbum.album_id]);
      }
    } else {
      // 总表中不存在（理论上不应该），新增
      insertAlbumInto('albums', { ...album, total_listen_count: Number(count) });
    }

    // 返回来源表的更新结果
    const updated = queryOne(`SELECT * FROM ${sourceTable} WHERE album_id = ?`, [id]);
    res.json({ success: true, album: updated, yearTable: yt });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// ==================== 启动服务器 ====================

async function start() {
  await initDatabase();
  console.log(`\n🎧 专辑数据库 Web 服务器已启动`);
  console.log(`   数据库: G:/原创计划/music`);
  console.log(`   访问: http://localhost:${PORT}`);
  console.log(`\n按 Ctrl+C 停止服务器\n`);

  app.listen(PORT, () => {
    console.log(`✅ 服务器运行中: http://localhost:${PORT}`);
  });
}

start().catch((err) => {
  console.error('启动失败:', err);
  process.exit(1);
});

process.on('SIGINT', () => {
  console.log('\n正在关闭服务器...');
  closeDatabase();
  process.exit(0);
});
