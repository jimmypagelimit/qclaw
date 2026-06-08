#!/usr/bin/env node

/**
 * 专辑数据库 Web 服务器
 * 用法: node dist/server.js
 * 默认端口: 3456
 *
 * 架构：单表 albums + listen_history
 * 年度数据通过 listen_history JOIN albums 查询
 * 不再使用 albums_YYYY 年度表
 */

import express from 'express';
import { initDatabase, closeDatabase, query, queryOne, execute, getTableCount, saveDatabase } from './db/database';
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

/** 获取所有有 listen_history 的年份 */
function getListenYears(): number[] {
  const rows = query<{ listen_year: number }>(
    'SELECT DISTINCT listen_year FROM listen_history ORDER BY listen_year'
  );
  return rows.map(r => r.listen_year);
}

// ==================== API 路由 ====================

// 年度收听排行（各年 Top 3，从 listen_history 查询）
app.get('/api/top-by-year', async (_req, res) => {
  try {
    const result: Record<string, any> = {};
    for (const year of getListenYears()) {
      const top = query(
        `SELECT a.album_name, a.artist, COUNT(lh.id) as listen_count, a.cover_image_url
         FROM listen_history lh
         JOIN albums a ON lh.album_id = a.album_id
         WHERE lh.listen_year = ?
         GROUP BY lh.album_id
         ORDER BY listen_count DESC
         LIMIT 3`,
        [year]
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
    const result: Record<string, any> = {};

    // 总表统计
    const albumCount = getTableCount('albums');
    const totalListens = queryOne<{ total: number }>(
      'SELECT COALESCE(SUM(total_listen_count), 0) as total FROM albums'
    );
    const topAlbum = queryOne<any>(
      'SELECT * FROM albums ORDER BY total_listen_count DESC LIMIT 1'
    );
    result.albums = {
      count: albumCount,
      totalListens: totalListens?.total || 0,
      topAlbum: topAlbum || null,
    };

    // 使用 album_genres 中间表统计 genre 分布
    const genres = query<any>(
      `SELECT g.name as genre, COUNT(*) as count 
       FROM albums a 
       JOIN album_genres ag ON a.album_id = ag.album_id 
       JOIN genres g ON ag.genre_id = g.genre_id 
       WHERE g.name IS NOT NULL AND g.name != '' 
       GROUP BY g.name 
       ORDER BY count DESC 
       LIMIT 10`
    );

    // 使用 album_styles 中间表统计 style 分布
    const styles = query<any>(
      `SELECT s.name as style, COUNT(*) as count 
       FROM albums a 
       JOIN album_styles ast ON a.album_id = ast.album_id 
       JOIN styles s ON ast.style_id = s.style_id 
       WHERE s.name IS NOT NULL AND s.name != '' 
       GROUP BY s.name 
       ORDER BY count DESC 
       LIMIT 10`
    );

    const countries = query<any>(
      `SELECT country, COUNT(*) as count FROM albums WHERE country IS NOT NULL AND country != '' GROUP BY country ORDER BY count DESC LIMIT 10`
    );

    // 各年份收听次数（从 listen_history 查询）
    const yearListens: Record<string, number> = {};
    const yearRows = query<{ listen_year: number; total: number }>(
      'SELECT listen_year, COUNT(*) as total FROM listen_history GROUP BY listen_year ORDER BY listen_year'
    );
    for (const row of yearRows) {
      yearListens[String(row.listen_year)] = row.total;
    }

    result.genres = genres;
    result.styles = styles;
    result.countries = countries;
    result.yearListens = yearListens;

    res.json(result);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// 搜索专辑（始终查 albums 表）
app.get('/api/albums', async (req, res) => {
  try {
    const {
      search, genre, country, artist, year,
      limit = 20, offset = 0,
      sort = 'listen',  // listen | score | name | artist | year
      dir = 'desc',     // asc | desc
    } = req.query;

    const yearNum = year ? Number(year) : null;

    let sql: string;
    let countSql: string;
    const params: any[] = [];

    if (yearNum) {
      // 按年份筛选：从 listen_history 查
      sql = `SELECT a.*, COUNT(lh.id) as year_listen_count
             FROM albums a
             JOIN listen_history lh ON a.album_id = lh.album_id
             WHERE lh.listen_year = ?`;
      countSql = `SELECT COUNT(DISTINCT a.album_id) as total
                  FROM albums a
                  JOIN listen_history lh ON a.album_id = lh.album_id
                  WHERE lh.listen_year = ?`;
      params.push(yearNum);
    } else {
      sql = 'SELECT a.* FROM albums a WHERE 1=1';
      countSql = 'SELECT COUNT(*) as total FROM albums a WHERE 1=1';
    }

    const filterParams: any[] = [];

    if (search) {
      sql += ' AND (a.album_name LIKE ? OR a.artist LIKE ?)';
      countSql += ' AND (a.album_name LIKE ? OR a.artist LIKE ?)';
      filterParams.push(`%${search}%`, `%${search}%`);
    }
    if (genre) {
      sql += ' AND EXISTS (SELECT 1 FROM album_genres ag JOIN genres g ON ag.genre_id = g.genre_id WHERE ag.album_id = a.album_id AND g.name LIKE ?)';
      countSql += ' AND EXISTS (SELECT 1 FROM album_genres ag JOIN genres g ON ag.genre_id = g.genre_id WHERE ag.album_id = a.album_id AND g.name LIKE ?)';
      filterParams.push(`%${genre}%`);
    }
    if (country) {
      sql += ' AND a.country = ?';
      countSql += ' AND a.country = ?';
      filterParams.push(country);
    }
    if (artist) {
      sql += ' AND a.artist LIKE ?';
      countSql += ' AND a.artist LIKE ?';
      filterParams.push(`%${artist}%`);
    }

    const allParams = [...params, ...filterParams];
    const countResult = query<any>(countSql, allParams);
    const total = countResult[0]?.total || 0;

    // 排序
    const sortMap: Record<string, string> = {
      listen: yearNum ? 'year_listen_count' : 'a.total_listen_count',
      score:  'a.overall_score',
      name:   'a.album_name',
      artist: 'a.artist',
      year:   'a.release_year',
    };
    const direction = dir === 'asc' ? 'ASC' : 'DESC';
    const sortCol = sortMap[sort as string] || (yearNum ? 'year_listen_count' : 'a.total_listen_count');

    if (yearNum) {
      sql += ` GROUP BY a.album_id`;
    }
    sql += ` ORDER BY ${sortCol} IS NULL, ${sortCol} ${direction} LIMIT ? OFFSET ?`;
    allParams.push(Number(limit), Number(offset));

    const albums = query(sql, allParams);
    res.json({ albums, total, limit: Number(limit), offset: Number(offset) });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// 专辑详情（始终查 albums 表）
app.get('/api/albums/:id', async (req, res) => {
  try {
    const album = queryOne<any>(
      'SELECT * FROM albums WHERE album_id = ?',
      [Number(req.params.id)]
    );
    if (!album) { res.status(404).json({ error: '专辑未找到' }); return; }

    // 附加年度收听统计
    const yearStats = query<{ listen_year: number; count: number }>(
      'SELECT listen_year, COUNT(*) as count FROM listen_history WHERE album_id = ? GROUP BY listen_year ORDER BY listen_year',
      [Number(req.params.id)]
    );
    (album as any).yearStats = yearStats;

    res.json(album);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// 艺术家专辑列表
app.get('/api/artist/:name', async (req, res) => {
  try {
    const { limit = 50 } = req.query;
    const albums = query(
      'SELECT * FROM albums WHERE artist LIKE ? ORDER BY total_listen_count DESC LIMIT ?',
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
    const { limit = 10, year } = req.query;

    if (year) {
      const yearNum = Number(year);
      const albums = query(
        `SELECT a.*, COUNT(lh.id) as year_listen_count
         FROM albums a
         JOIN listen_history lh ON a.album_id = lh.album_id
         WHERE lh.listen_year = ?
         GROUP BY a.album_id
         ORDER BY year_listen_count DESC
         LIMIT ?`,
        [yearNum, Number(limit)]
      );
      res.json({ year: yearNum, albums });
    } else {
      const albums = query(
        'SELECT * FROM albums ORDER BY total_listen_count DESC LIMIT ?',
        [Number(limit)]
      );
      res.json({ year: null, albums });
    }
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// 风格分布
app.get('/api/genres', async (req, res) => {
  try {
    const { limit = 20 } = req.query;
    const genres = query<any>(
      `SELECT g.name as genre, COUNT(*) as count 
       FROM albums a 
       JOIN album_genres ag ON a.album_id = ag.album_id 
       JOIN genres g ON ag.genre_id = g.genre_id 
       WHERE g.name IS NOT NULL AND g.name != '' 
       GROUP BY g.name 
       ORDER BY count DESC 
       LIMIT ?`,
      [Number(limit)]
    );
    res.json(genres);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// 风格分布
app.get('/api/styles', async (req, res) => {
  try {
    const { limit = 20 } = req.query;
    const styles = query<any>(
      `SELECT s.name as style, COUNT(*) as count 
       FROM albums a 
       JOIN album_styles ast ON a.album_id = ast.album_id 
       JOIN styles s ON ast.style_id = s.style_id 
       WHERE s.name IS NOT NULL AND s.name != '' 
       GROUP BY s.name 
       ORDER BY count DESC 
       LIMIT ?`,
      [Number(limit)]
    );
    res.json(styles);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// 国家分布
app.get('/api/countries', async (req, res) => {
  try {
    const { limit = 20 } = req.query;
    const countries = query<any>(
      'SELECT country, COUNT(*) as count FROM albums WHERE country IS NOT NULL AND country != ? GROUP BY country ORDER BY count DESC LIMIT ?',
      ['', Number(limit)]
    );
    res.json(countries);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// 艺人排行榜
app.get('/api/artists', async (req, res) => {
  try {
    const { sort = 'listen', dir = 'desc', limit = 10 } = req.query;
    const sortMap: Record<string, string> = {
      listen: 'total_listen_count',
      score:  'avg_rating',
      name:    'artist',
    };
    const direction = dir === 'asc' ? 'ASC' : 'DESC';
    const sortCol = sortMap[sort as string] || 'total_listen_count';

    const sql = `
      SELECT 
        artist, 
        SUM(total_listen_count) as total_listen_count,
        AVG(overall_score) as avg_rating
      FROM albums 
      GROUP BY artist 
      ORDER BY ${sortCol} IS NULL, ${sortCol} ${direction}
      LIMIT ?
    `;
    const artists = query<any>(sql, [Number(limit)]);

    // 为每个艺人附加一张封面（取收听次数最多的有封面专辑）
    for (const ar of artists) {
      const coverRow = queryOne<{ cover_image_url: string }>(
        `SELECT cover_image_url FROM albums WHERE artist = ? AND cover_image_url IS NOT NULL AND cover_image_url != '' ORDER BY total_listen_count DESC LIMIT 1`,
        [ar.artist]
      );
      (ar as any).cover_image_url = coverRow?.cover_image_url || null;
    }

    res.json({ artists });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// ==================== 写操作（单表 albums + listen_history） ====================

/**
 * 新增专辑
 * body: { ..., year: 2026 }
 * 逻辑：
 *   1. 写入 albums 表（判重：album_name + artist，已存在则 +1 total_listen_count）
 *   2. 写入 listen_history
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

    // 查找是否已存在
    const existing = queryOne<any>(
      'SELECT * FROM albums WHERE album_name = ? AND artist = ?',
      [album_name, artist]
    );

    if (existing) {
      // 已存在，+1 total_listen_count
      const newCount = existing.total_listen_count + 1;
      execute('UPDATE albums SET total_listen_count = ? WHERE album_id = ?', [newCount, existing.album_id]);
    } else {
      // 新增
      const fields = [
        'album_name', 'artist', 'country', 'region', 'genre', 'rating',
        'description', 'is_compilation', 'first_listen_date', 'total_listen_count',
        'release_company', 'cover_image_url', 'duration', 'release_year', 'style', 'producer'
      ];
      const values = fields.map(f => {
        const val = (f === 'album_name' ? album_name : f === 'artist' ? artist : 
                     f === 'country' ? country : f === 'region' ? region : f === 'genre' ? genre :
                     f === 'rating' ? rating : f === 'description' ? description : 
                     f === 'is_compilation' ? is_compilation : f === 'first_listen_date' ? first_listen_date :
                     f === 'total_listen_count' ? total_listen_count : f === 'release_company' ? release_company :
                     f === 'cover_image_url' ? cover_image_url : f === 'duration' ? duration :
                     f === 'release_year' ? release_year : f === 'style' ? style : f === 'producer' ? producer : null) ?? null;
        return val;
      });
      // 确保 total_listen_count 至少为 1
      const tlcIndex = fields.indexOf('total_listen_count');
      if (!values[tlcIndex]) values[tlcIndex] = 1;
      // 确保 first_listen_date 有值
      const fldIndex = fields.indexOf('first_listen_date');
      if (!values[fldIndex]) values[fldIndex] = new Date().toISOString().split('T')[0];

      execute(
        `INSERT INTO albums (${fields.join(', ')}) VALUES (${fields.map(() => '?').join(', ')})`,
        values
      );
    }

    // 写入 listen_history
    const album = queryOne<any>(
      'SELECT * FROM albums WHERE album_name = ? AND artist = ?',
      [album_name, artist]
    );
    if (album) {
      execute(
        'INSERT INTO listen_history (album_id, listen_date, listen_year, notes, source) VALUES (?, ?, ?, ?, ?)',
        [album.album_id, new Date().toISOString().split('T')[0], yr, '', '']
      );
    }

    saveDatabase();
    res.json({ success: true, album });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * 更新专辑（只操作 albums 表）
 */
app.put('/api/albums/:id', async (req, res) => {
  try {
    const id = Number(req.params.id);
    const fields = req.body;

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

    params.push(id);
    execute(`UPDATE albums SET ${setClauses.join(', ')} WHERE album_id = ?`, params);

    const updated = queryOne<any>('SELECT * FROM albums WHERE album_id = ?', [id]);
    saveDatabase();
    res.json({ success: true, album: updated });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * 删除专辑
 */
app.delete('/api/albums/:id', async (req, res) => {
  try {
    const id = Number(req.params.id);

    const album = queryOne<any>('SELECT * FROM albums WHERE album_id = ?', [id]);
    if (!album) { res.status(404).json({ error: '专辑未找到' }); return; }

    // 先删 listen_history
    execute('DELETE FROM listen_history WHERE album_id = ?', [id]);
    // 再删 albums
    execute('DELETE FROM albums WHERE album_id = ?', [id]);

    saveDatabase();
    res.json({ success: true, deleted: album });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

/**
 * 记录收听
 * body: { count: 1, year: 2026 }
 * 逻辑：
 *   1. albums 表 +1 total_listen_count
 *   2. 写入 listen_history
 */
app.post('/api/albums/:id/listen', async (req, res) => {
  try {
    const id = Number(req.params.id);
    const { count = 1, year = currentYear() } = req.body;
    const yr = Number(year);

    const album = queryOne<any>('SELECT * FROM albums WHERE album_id = ?', [id]);
    if (!album) { res.status(404).json({ error: '专辑未找到' }); return; }

    // +1 total_listen_count
    const newCount = album.total_listen_count + Number(count);
    execute('UPDATE albums SET total_listen_count = ? WHERE album_id = ?', [newCount, id]);

    // 设置首次收听日期（如果为空）
    if (!album.first_listen_date) {
      const today = new Date().toISOString().split('T')[0];
      execute('UPDATE albums SET first_listen_date = ? WHERE album_id = ?', [today, id]);
    }

    // 写入 listen_history
    for (let i = 0; i < Number(count); i++) {
      execute(
        'INSERT INTO listen_history (album_id, listen_date, listen_year, notes, source) VALUES (?, ?, ?, ?, ?)',
        [id, new Date().toISOString().split('T')[0], yr, '', '']
      );
    }

    const updated = queryOne<any>('SELECT * FROM albums WHERE album_id = ?', [id]);
    saveDatabase();
    res.json({ success: true, album: updated });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// ==================== 启动服务器 ====================

async function start() {
  await initDatabase();
  console.log(`\n🎧 专辑数据库 Web 服务器已启动`);
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
