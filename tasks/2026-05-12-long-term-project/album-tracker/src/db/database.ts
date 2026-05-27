/**
 * 数据库连接模块
 * 使用 sql.js 操作 SQLite 数据库
 */

import initSqlJs, { Database as SqlJsDatabase } from 'sql.js';
import * as fs from 'fs';
import * as path from 'path';

// 默认数据库路径（网络位置）
const DEFAULT_DB_PATH = '\\\\10.0.2.4\\qemu\\原创计划\\music';

let db: SqlJsDatabase | null = null;

/**
 * 初始化数据库连接
 */
export async function initDatabase(dbPath?: string): Promise<SqlJsDatabase> {
  if (db) {
    return db;
  }

  const dbFilePath = dbPath || DEFAULT_DB_PATH;

  // 检查文件是否存在
  if (!fs.existsSync(dbFilePath)) {
    throw new Error(`数据库文件不存在: ${dbFilePath}`);
  }

  // 初始化 sql.js
  const SQL = await initSqlJs();

  // 读取数据库文件
  const fileBuffer = fs.readFileSync(dbFilePath);
  db = new SQL.Database(fileBuffer);

  console.log(`✅ 已连接数据库: ${dbFilePath}`);
  console.log(`   表: albums, albums_2024, albums_2025, albums_2026`);

  return db;
}

/**
 * 获取数据库实例
 */
export function getDatabase(): SqlJsDatabase {
  if (!db) {
    throw new Error('数据库未初始化，请先调用 initDatabase()');
  }
  return db;
}

/**
 * 执行查询并返回结果
 */
export function query<T>(sql: string, params: unknown[] = []): T[] {
  const database = getDatabase();
  const stmt = database.prepare(sql);
  stmt.bind(params);

  const results: T[] = [];
  while (stmt.step()) {
    const row = stmt.getAsObject();
    results.push(row as T);
  }
  stmt.free();

  return results;
}

/**
 * 执行单行查询
 */
export function queryOne<T>(sql: string, params: unknown[] = []): T | null {
  const results = query<T>(sql, params);
  return results.length > 0 ? results[0] : null;
}

/**
 * 执行插入/更新/删除
 * @returns 受影响的行数
 */
export function execute(sql: string, params: unknown[] = []): number {
  const database = getDatabase();
  database.run(sql, params);
  return database.getRowsModified();
}

/**
 * 持久化数据库到文件
 */
export function saveDatabase(): void {
  if (!db) {
    throw new Error('数据库未初始化');
  }

  const data = db.export();
  const buffer = Buffer.from(data);

  // 同步写入
  fs.writeFileSync(DEFAULT_DB_PATH, buffer);
  console.log(`💾 数据库已保存: ${DEFAULT_DB_PATH}`);
}

/**
 * 关闭数据库连接
 */
export function closeDatabase(): void {
  if (db) {
    // 关闭前先保存
    saveDatabase();
    db.close();
    db = null;
    console.log('🔌 数据库连接已关闭');
  }
}

/**
 * 获取表名列表
 */
export function getTableNames(): string[] {
  const results = query<{ name: string }>(
    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
  );
  return results.map((r) => r.name);
}

/**
 * 检查表是否存在
 */
export function tableExists(tableName: string): boolean {
  const result = queryOne<{ count: number }>(
    'SELECT COUNT(*) as count FROM sqlite_master WHERE type=? AND name=?',
    ['table', tableName]
  );
  return (result?.count ?? 0) > 0;
}

/**
 * 获取表记录数
 */
export function getTableCount(tableName: string): number {
  const result = queryOne<{ count: number }>(
    `SELECT COUNT(*) as count FROM ${tableName}`
  );
  return result?.count ?? 0;
}
