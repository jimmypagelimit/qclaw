const fs = require("fs");
const src = fs.readFileSync("dist/server.js", "utf-8");
// 查找数据库路径配置
const lines = src.split("\n");
for (let i = 0; i < lines.length; i++) {
  const l = lines[i];
  if (l.includes("dataSource") || l.includes("filename") || l.includes("db")) {
    console.log(i+1, l.trim());
  }
}