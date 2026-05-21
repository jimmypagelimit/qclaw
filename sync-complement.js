// sync-complement.js — 互相补充模式增量同步
// 将其写入 C:\Users\15206\.qclaw\workspace\sync-complement.js 并执行

const fs = require('fs');
const path = require('path');

const WORKSPACE = 'C:\\Users\\15206\\.qclaw\\workspace';
const TARGET = 'H:\\荒岛唱片';
const LOG_FILE = path.join(WORKSPACE, 'SyncLog.txt');

const logs = [];
const timePrefix = () => new Date().toISOString().replace('T', ' ').slice(0, 19);

function log(msg) {
  const line = `[${timePrefix()}] ${msg}`;
  console.log(line);
  logs.push(line);
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function getAllFilesSync(dir, base = dir) {
  let files = [];
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.name === '.git' || entry.name === 'SyncLog.txt' ||
          entry.name === 'sync.sh' || entry.name === 'sync.bat' ||
          entry.name === 'sync-complement.js') continue;
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        files = files.concat(getAllFilesSync(fullPath, base));
      } else {
        files.push({ full: fullPath, rel: path.relative(base, fullPath) });
      }
    }
  } catch (e) {
    // skip inaccessible dirs
  }
  return files;
}

function copyFile(src, dst) {
  ensureDir(path.dirname(dst));
  const srcStat = fs.statSync(src);
  let needCopy = true;
  if (fs.existsSync(dst)) {
    const dstStat = fs.statSync(dst);
    // compare by mtime and size
    if (srcStat.mtimeMs <= dstStat.mtimeMs && srcStat.size === dstStat.size) {
      needCopy = false;
    }
  }
  if (needCopy) {
    fs.copyFileSync(src, dst);
    return true;
  }
  return false;
}

async function main() {
  log('=== 互相补充模式同步开始 ===');
  log(`源: ${WORKSPACE}`);
  log(`目标: ${TARGET}`);

  // Step 1: Workspace → H:\荒岛唱片
  const wsFiles = getAllFilesSync(WORKSPACE);
  log(`Workspace 共 ${wsFiles.length} 个文件`);
  let syncedToH = 0;
  for (const f of wsFiles) {
    const dst = path.join(TARGET, f.rel);
    try {
      if (copyFile(f.full, dst)) {
        log(`  → 同步到H盘: ${f.rel}`);
        syncedToH++;
      }
    } catch (e) {
      log(`  ✗ 失败(H): ${f.rel} — ${e.message}`);
    }
  }

  // Step 2: H:\荒岛唱片 → Workspace
  const hFiles = getAllFilesSync(TARGET);
  log(`H盘荒岛唱片共 ${hFiles.length} 个文件`);
  let syncedToWS = 0;
  for (const f of hFiles) {
    const dst = path.join(WORKSPACE, f.rel);
    try {
      if (copyFile(f.full, dst)) {
        log(`  ← 同步到Workspace: ${f.rel}`);
        syncedToWS++;
      }
    } catch (e) {
      log(`  ✗ 失败(WS): ${f.rel} — ${e.message}`);
    }
  }

  log(`同步完成：Workspace→H盘 ${syncedToH} 个，H盘→Workspace ${syncedToWS} 个`);
  log('=== 互相补充模式同步完成 ===\n');

  fs.writeFileSync(LOG_FILE, logs.join('\n'), 'utf8');
}

main().catch(e => {
  console.error('同步出错:', e);
  process.exit(1);
});
