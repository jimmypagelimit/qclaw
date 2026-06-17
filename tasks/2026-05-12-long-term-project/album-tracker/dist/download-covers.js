#!/usr/bin/env node
"use strict";
/**
 * 批量专辑封面下载脚本
 *
 * 用法: node dist/download-covers.js [--count 10] [--offset 0]
 *
 * 优先级: iTunes > Deezer > 网易云音乐
 * 按排名（收听次数+评分）顺序下载无封面专辑
 *
 * 流程:
 * 1. 查询数据库中 cover_image_url 为空的专辑，按排名排序
 * 2. 依次尝试 iTunes / Deezer / 网易云 API 获取封面
 * 3. 下载到 covers/ 目录，命名: {序号}-{艺术家}-{专辑名}.jpg
 * 4. 更新数据库中所有表（albums + 年份表）的 cover_image_url
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
const sql_js_1 = __importDefault(require("sql.js"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const https_1 = __importDefault(require("https"));
const http_1 = __importDefault(require("http"));
const DB_PATH = path.join(__dirname, '..', 'music');
const COVERS_DIR = path.join(__dirname, '..', 'covers');
const DB_TABLES = ['albums', 'albums_2024', 'albums_2025', 'albums_2026'];
// ==================== CLI 参数 ====================
const args = process.argv.slice(2);
let count = 10;
let offset = 0;
for (let i = 0; i < args.length; i++) {
    if (args[i] === '--count' && args[i + 1]) {
        count = parseInt(args[i + 1], 10);
        i++;
    }
    else if (args[i] === '--offset' && args[i + 1]) {
        offset = parseInt(args[i + 1], 10);
        i++;
    }
}
// ==================== 工具函数 ====================
/** HTTP GET 请求，返回 JSON */
function fetchJSON(url, timeout = 10000) {
    return new Promise((resolve, reject) => {
        const mod = url.startsWith('https') ? https_1.default : http_1.default;
        const req = mod.get(url, { timeout }, (res) => {
            if (res.statusCode && res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
                return fetchJSON(res.headers.location, timeout).then(resolve).catch(reject);
            }
            if (res.statusCode && (res.statusCode < 200 || res.statusCode >= 300)) {
                res.resume();
                return reject(new Error(`HTTP ${res.statusCode}: ${url}`));
            }
            const chunks = [];
            res.on('data', (chunk) => chunks.push(chunk));
            res.on('end', () => {
                try {
                    resolve(JSON.parse(Buffer.concat(chunks).toString('utf-8')));
                }
                catch (e) {
                    reject(new Error(`JSON parse error: ${e.message}`));
                }
            });
        });
        req.on('error', reject);
        req.on('timeout', () => { req.destroy(); reject(new Error('Timeout')); });
    });
}
/** 下载二进制文件 */
function downloadFile(url, destPath, timeout = 15000) {
    return new Promise((resolve, reject) => {
        const mod = url.startsWith('https') ? https_1.default : http_1.default;
        const req = mod.get(url, {
            timeout,
            headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }
        }, (res) => {
            if (res.statusCode && res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
                return downloadFile(res.headers.location, destPath, timeout).then(resolve).catch(reject);
            }
            if (res.statusCode && (res.statusCode < 200 || res.statusCode >= 300)) {
                res.resume();
                return reject(new Error(`HTTP ${res.statusCode}`));
            }
            const file = fs.createWriteStream(destPath);
            res.pipe(file);
            file.on('finish', () => {
                file.close();
                resolve(fs.statSync(destPath).size);
            });
        });
        req.on('error', (e) => { fs.existsSync(destPath) && fs.unlinkSync(destPath); reject(e); });
        req.on('timeout', () => { req.destroy(); reject(new Error('Timeout')); });
    });
}
/** 文件名安全化 */
function sanitizeFilename(s) {
    return s.replace(/[\\/:*?"<>|]/g, '_').replace(/\s+/g, '_').substring(0, 60);
}
/** iTunes Search API */
async function searchITunes(albumName, artist) {
    try {
        const query = encodeURIComponent(`${albumName} ${artist}`);
        const data = await fetchJSON(`https://itunes.apple.com/search?term=${query}&entity=album&limit=5`);
        const results = data.results || [];
        for (const r of results) {
            const name = (r.collectionName || '').toLowerCase();
            const art = (r.artistName || '').toLowerCase();
            if (r.artworkUrl100 &&
                (name.includes(albumName.toLowerCase()) || albumName.toLowerCase().includes(name)) &&
                (art.includes(artist.toLowerCase()) || artist.toLowerCase().includes(art))) {
                return {
                    url: r.artworkUrl100.replace('100x100', '600x600'),
                    source: 'itunes'
                };
            }
        }
        // Fallback: 取第一个有 artwork 的
        for (const r of results) {
            if (r.artworkUrl100 && (r.artistName || '').toLowerCase().includes(artist.toLowerCase().split(' ')[0])) {
                return {
                    url: r.artworkUrl100.replace('100x100', '600x600'),
                    source: 'itunes'
                };
            }
        }
        return null;
    }
    catch {
        return null;
    }
}
/** Deezer Search API */
async function searchDeezer(albumName, artist) {
    try {
        const query = encodeURIComponent(`${albumName} ${artist}`);
        const data = await fetchJSON(`https://api.deezer.com/search/album?q=${query}&limit=5`);
        const results = data.data || [];
        for (const r of results) {
            const title = (r.title || '').toLowerCase();
            const art = (r.artist?.name || '').toLowerCase();
            if (r.cover_big &&
                (title.includes(albumName.toLowerCase()) || albumName.toLowerCase().includes(title)) &&
                (art.includes(artist.toLowerCase()) || artist.toLowerCase().includes(art))) {
                return { url: r.cover_big, source: 'deezer' };
            }
        }
        // Fallback
        for (const r of results) {
            if (r.cover_big) {
                return { url: r.cover_big, source: 'deezer' };
            }
        }
        return null;
    }
    catch {
        return null;
    }
}
/** 网易云音乐 API (外部: music.163.com) */
async function searchNetease(albumName, artist) {
    try {
        const query = encodeURIComponent(`${albumName} ${artist}`);
        const data = await fetchJSON(`https://music.163.com/api/search/get?s=${query}&type=10&limit=5`);
        const results = data.result?.albums || [];
        for (const r of results) {
            const name = (r.name || '').toLowerCase();
            const art = (r.artist?.name || '').toLowerCase();
            if (r.picUrl &&
                (name.includes(albumName.toLowerCase()) || albumName.toLowerCase().includes(name))) {
                return { url: r.picUrl + '?param=500y500', source: 'netease' };
            }
        }
        // Fallback
        for (const r of results) {
            if (r.picUrl) {
                return { url: r.picUrl + '?param=500y500', source: 'netease' };
            }
        }
        return null;
    }
    catch {
        return null;
    }
}
/** 按优先级搜索封面 */
async function searchCover(albumName, artist) {
    // 1. iTunes
    let result = await searchITunes(albumName, artist);
    if (result)
        return result;
    // 2. Deezer
    result = await searchDeezer(albumName, artist);
    if (result)
        return result;
    // 3. 网易云
    result = await searchNetease(albumName, artist);
    if (result)
        return result;
    return null;
}
// ==================== 主流程 ====================
async function main() {
    // 确保 covers 目录存在
    if (!fs.existsSync(COVERS_DIR)) {
        fs.mkdirSync(COVERS_DIR, { recursive: true });
    }
    // 初始化数据库
    const SQL = await (0, sql_js_1.default)();
    const fileBuffer = fs.readFileSync(DB_PATH);
    const db = new SQL.Database(fileBuffer);
    // 查询无封面专辑，按排名排序（收听次数 DESC, 评分 DESC）
    const sql = `
    SELECT album_id, album_name, artist, total_listen_count, rating
    FROM albums
    WHERE cover_image_url IS NULL OR cover_image_url = ''
    ORDER BY total_listen_count DESC, rating DESC
    LIMIT ? OFFSET ?
  `;
    const stmt = db.prepare(sql);
    stmt.bind([count, offset]);
    const albums = [];
    while (stmt.step()) {
        albums.push(stmt.getAsObject());
    }
    stmt.free();
    console.log(`🔍 找到 ${albums.length} 张需要封面的专辑（offset=${offset}, count=${count}）`);
    console.log('');
    let success = 0;
    let failed = 0;
    for (const album of albums) {
        const idx = String(success + failed + 1).padStart(2, '0');
        process.stdout.write(`[${idx}] ${album.album_name} - ${album.artist} ... `);
        try {
            const cover = await searchCover(album.album_name, album.artist);
            if (!cover) {
                console.log('❌ 所有源均未找到');
                failed++;
                continue;
            }
            // 生成文件名
            const safeArtist = sanitizeFilename(album.artist);
            const safeAlbum = sanitizeFilename(album.album_name);
            const filename = `${album.album_id}-${safeArtist}-${safeAlbum}.jpg`;
            const filepath = path.join(COVERS_DIR, filename);
            // 下载封面
            const size = await downloadFile(cover.url, filepath);
            if (size < 1000) {
                console.log(`⚠️ 文件太小(${size}B)，可能无效`);
                fs.existsSync(filepath) && fs.unlinkSync(filepath);
                failed++;
                continue;
            }
            const coverUrl = `covers/${filename}`;
            // 更新所有表中的 cover_image_url
            for (const table of DB_TABLES) {
                try {
                    db.run(`UPDATE ${table} SET cover_image_url = ? WHERE album_name = ? AND artist = ?`, [coverUrl, album.album_name, album.artist]);
                }
                catch {
                    // 表可能没有该记录，忽略
                }
            }
            console.log(`✅ (${cover.source}, ${size}B)`);
            success++;
            // 请求间隔，避免限流
            await new Promise(r => setTimeout(r, 500));
        }
        catch (e) {
            console.log(`❌ ${e.message}`);
            failed++;
        }
    }
    // 保存数据库
    const data = db.export();
    const buffer = Buffer.from(data);
    fs.writeFileSync(DB_PATH, buffer);
    console.log('');
    console.log(`💾 数据库已保存`);
    console.log(`📊 结果: ✅ ${success} 成功 / ❌ ${failed} 失败 / 📋 ${albums.length} 总计`);
    db.close();
}
main().catch(e => {
    console.error('Fatal error:', e);
    process.exit(1);
});
