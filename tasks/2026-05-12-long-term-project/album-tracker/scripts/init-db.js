#!/usr/bin/env node
"use strict";

/**
 * 从 database.sql 初始化 _music_latest.db
 */

const sql = require("sql.js");
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");
const SQL_FILE = path.join(ROOT, "database.sql");
const DB_FILE = path.join(ROOT, "_music_latest.db");

console.log("SQL 文件:", SQL_FILE);
console.log("目标数据库:", DB_FILE);

// 读取 SQL 文件
const sqlContent = fs.readFileSync(SQL_FILE, "utf-8");
console.log("SQL 文件大小:", sqlContent.length, "字节");

// 初始化 sql.js
console.log("正在初始化 sql.js...");
sql.default({
  locateFile: file => path.join(ROOT, "node_modules/sql.js/dist", file)
}).then(SQL => {
  console.log("sql.js 初始化成功");
  
  // 创建空数据库
  const db = new SQL.Database();
  
  // 执行 SQL
  console.log("正在执行 SQL...");
  try {
    db.run(sqlContent);
    console.log("SQL 执行成功");
  } catch (e) {
    console.error("SQL 执行失败:", e.message);
    process.exit(1);
  }
  
  // 写入数据库文件
  console.log("正在写入数据库文件...");
  const data = db.export();
  const buffer = Buffer.from(data);
  fs.writeFileSync(DB_FILE, buffer);
  console.log("数据库已写入:", DB_FILE, "大小:", buffer.length, "字节");
  
  // 验证
  console.log("验证数据库...");
  const db2 = new SQL.Database(buffer);
  const tables = db2.exec("SELECT name FROM sqlite_master WHERE type='table'");
  console.log("数据库表:", JSON.stringify(tables, null, 2));
  
  db.close();
  db2.close();
  console.log("完成！");
}).catch(err => {
  console.error("初始化失败:", err);
  process.exit(1);
});
