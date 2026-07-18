"use strict";
/**
 * 数据库连接模块
 * 使用 sql.js 操作 SQLite 数据库
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.initDatabase = initDatabase;
exports.getDatabase = getDatabase;
exports.query = query;
exports.queryOne = queryOne;
exports.execute = execute;
exports.saveDatabase = saveDatabase;
exports.closeDatabase = closeDatabase;
exports.getTableNames = getTableNames;
exports.tableExists = tableExists;
exports.getTableCount = getTableCount;
const sql_js_1 = __importDefault(require("sql.js"));
const fs = __importStar(require("fs"));
// 默认数据库路径（本地副本）
const DEFAULT_DB_PATH = '/root/qclaw/tasks/2026-05-12-long-term-project/album-tracker/_music_latest.db';
let db = null;
/**
 * 初始化数据库连接
 */
async function initDatabase(dbPath) {
    if (db) {
        return db;
    }
    const dbFilePath = dbPath || DEFAULT_DB_PATH;
    // 检查文件是否存在
    if (!fs.existsSync(dbFilePath)) {
        throw new Error(`数据库文件不存在: ${dbFilePath}`);
    }
    // 初始化 sql.js
    const SQL = await (0, sql_js_1.default)();
    // 读取数据库文件
    const fileBuffer = fs.readFileSync(dbFilePath);
    db = new SQL.Database(fileBuffer);
    console.log(`✅ 已连接数据库: ${dbFilePath}`);
    console.log(`   表: albums, listen_history, artists, genres, styles`);
    return db;
}
/**
 * 获取数据库实例
 */
function getDatabase() {
    if (!db) {
        throw new Error('数据库未初始化，请先调用 initDatabase()');
    }
    return db;
}
/**
 * 执行查询并返回结果
 */
function query(sql, params = []) {
    const database = getDatabase();
    const stmt = database.prepare(sql);
    stmt.bind(params);
    const results = [];
    while (stmt.step()) {
        const row = stmt.getAsObject();
        results.push(row);
    }
    stmt.free();
    return results;
}
/**
 * 执行单行查询
 */
function queryOne(sql, params = []) {
    const results = query(sql, params);
    return results.length > 0 ? results[0] : null;
}
/**
 * 执行插入/更新/删除
 * @returns 受影响的行数
 */
function execute(sql, params = []) {
    const database = getDatabase();
    database.run(sql, params);
    return database.getRowsModified();
}
/**
 * 持久化数据库到文件
 */
function saveDatabase() {
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
function closeDatabase() {
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
function getTableNames() {
    const results = query("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'");
    return results.map((r) => r.name);
}
/**
 * 检查表是否存在
 */
function tableExists(tableName) {
    const result = queryOne('SELECT COUNT(*) as count FROM sqlite_master WHERE type=? AND name=?', ['table', tableName]);
    return (result?.count ?? 0) > 0;
}
/**
 * 获取表记录数
 */
function getTableCount(tableName) {
    const result = queryOne(`SELECT COUNT(*) as count FROM ${tableName}`);
    return result?.count ?? 0;
}
