#!/usr/bin/env node
"use strict";
// @ts-nocheck
Object.defineProperty(exports, "__esModule", { value: true });
/**
 * 专辑数据库 CLI 工具
 * 用法: node dist/cli.js <command> [options]
 */
const commander_1 = require("commander");
const database_1 = require("./db/database");
const album_service_1 = require("./services/album.service");
// CLI 版本
const VERSION = '1.0.0';
// 创建命令
const program = new commander_1.Command();
program
    .name('album-tracker')
    .description('专辑数据库管理工具 - 维护、查询、统计')
    .version(VERSION);
// ==================== 查询命令 ====================
// 搜索专辑
program
    .command('search')
    .description('搜索专辑（支持多表）')
    .argument('[keyword]', '搜索关键词（专辑名或艺术家）')
    .option('-a, --artist <name>', '按艺术家筛选')
    .option('-g, --genre <genre>', '按风格筛选')
    .option('-y, --year <year>', '按发行年份筛选')
    .option('-t, --table <name>', '指定表名', 'albums')
    .option('-l, --limit <number>', '返回数量', '20')
    .action(async (keyword, options) => {
    try {
        await (0, database_1.initDatabase)();
        let albums;
        if (keyword) {
            albums = (0, album_service_1.searchAlbums)(keyword, ['albums', 'albums_2024', 'albums_2025', 'albums_2026']);
        }
        else {
            albums = (0, album_service_1.getAlbums)({
                artist: options.artist,
                genre: options.genre,
                year: options.year,
                limit: parseInt(options.limit),
            }, options.table);
        }
        if (albums.length === 0) {
            console.log('未找到匹配的专辑');
        }
        else {
            console.log(`找到 ${albums.length} 张专辑:\n`);
            console.log('ID     表            专辑名                      艺术家        风格       收听');
            console.log('─'.repeat(95));
            for (const album of albums.slice(0, parseInt(options.limit))) {
                const name = album.album_name.padEnd(24).slice(0, 24);
                const artist = album.artist.padEnd(12).slice(0, 12);
                const genre = (album.genre || '-').padEnd(10).slice(0, 10);
                const table = (album.source_table || options.table || 'albums').padEnd(12);
                console.log(`${String(album.album_id).padStart(5)} ${table} ${name} ${artist} ${genre} ${album.total_listen_count}`);
            }
            console.log('\n💡 提示：用 `listen -i <ID> -t <表名>` 更新收听（如 -t 2026 表示 albums_2026 表）');
        }
        (0, database_1.closeDatabase)();
    }
    catch (error) {
        console.error('错误:', error);
        process.exit(1);
    }
});
// 查看专辑详情
program
    .command('info')
    .description('查看专辑详情（自动检测专辑所在表）')
    .option('-i, --id <id>', '专辑 ID', (val) => parseInt(val))
    .option('-t, --table <name>', '表名（省略则自动扫描所有表检测）')
    .action(async (options) => {
    try {
        await (0, database_1.initDatabase)();
        // 自动检测专辑所在表（年份表优先）
        const tables = options.table
            ? [options.table]
            : ['albums_2026', 'albums_2025', 'albums_2024', 'albums'];
        let foundTable = null;
        let album = null;
        for (const tbl of tables) {
            const a = (0, album_service_1.getAlbumById)(options.id, tbl);
            if (a) {
                foundTable = tbl;
                album = a;
                break;
            }
        }
        if (!album || !foundTable) {
            console.log(`❌ 未找到 ID 为 ${options.id} 的专辑（已扫描: ${tables.join(', ')}）`);
            process.exit(1);
        }
        console.log('\n📀 专辑详情');
        console.log(`所在表: ${foundTable}`);
        console.log('─'.repeat(50));
        console.log(`ID:            ${album.album_id}`);
        console.log(`专辑名:        ${album.album_name}`);
        console.log(`艺术家:        ${album.artist}`);
        console.log(`国家:          ${album.country || '-'}`);
        console.log(`风格:          ${album.genre || '-'}`);
        console.log(`发行年份:      ${album.release_year || '-'}`);
        console.log(`发行公司:      ${album.release_company || '-'}`);
        console.log(`制作人:        ${album.producer || '-'}`);
        console.log(`风格细分:      ${album.style || '-'}`);
        console.log('─'.repeat(50));
        console.log(`总收听次数:    ${album.total_listen_count}`);
        console.log(`首次收听:      ${album.first_listen_date || '-'}`);
        console.log(`评分:          ${album.rating || '-'}`);
        console.log(`封面:          ${album.cover_image_url || '-'}`);
        console.log('─'.repeat(50));
        if (album.composition_score)
            console.log(`作曲评分:      ${album.composition_score}`);
        if (album.lyrics_meaning_score)
            console.log(`歌词意境:      ${album.lyrics_meaning_score}`);
        if (album.creativity_score)
            console.log(`创意评分:      ${album.creativity_score}`);
        if (album.arrangement_score)
            console.log(`编曲评分:      ${album.arrangement_score}`);
        if (album.vocal_performance_score)
            console.log(`演唱评分:      ${album.vocal_performance_score}`);
        if (album.overall_score)
            console.log(`综合评分:      ${album.overall_score}`);
        console.log('─'.repeat(50));
        if (album.description)
            console.log(`描述:\n${album.description}`);
        (0, database_1.closeDatabase)();
    }
    catch (error) {
        console.error('错误:', error);
        process.exit(1);
    }
});
// 查看艺术家的专辑
program
    .command('artist')
    .description('查看艺术家的所有专辑')
    .option('-n, --name <name>', '艺术家名称', required)
    .option('-t, --table <name>', '表名', 'albums')
    .action(async (options) => {
    try {
        await (0, database_1.initDatabase)();
        const albums = (0, album_service_1.getAlbumsByArtist)(options.name, options.table);
        if (albums.length === 0) {
            console.log(`未找到艺术家 "${options.name}" 的专辑`);
            process.exit(1);
        }
        const totalListens = albums.reduce((sum, a) => sum + a.total_listen_count, 0);
        console.log(`\n🎤 ${options.name}`);
        console.log(`专辑数量: ${albums.length} | 总收听: ${totalListens}`);
        console.log('─'.repeat(70));
        console.log('ID     专辑名                      年份    风格       收听');
        console.log('─'.repeat(70));
        for (const album of albums) {
            const name = album.album_name.padEnd(24).slice(0, 24);
            const year = (album.release_year || '-').padStart(6);
            const genre = (album.genre || '-').padEnd(10).slice(0, 10);
            console.log(`${String(album.album_id).padStart(5)} ${name} ${year} ${genre} ${album.total_listen_count}`);
        }
        (0, database_1.closeDatabase)();
    }
    catch (error) {
        console.error('错误:', error);
        process.exit(1);
    }
});
// ==================== 维护命令 ====================
// 添加专辑
program
    .command('add')
    .description('添加新专辑')
    .requiredOption('-n, --name <name>', '专辑名')
    .requiredOption('-a, --artist <artist>', '艺术家')
    .option('-c, --country <country>', '国家')
    .option('-g, --genre <genre>', '风格')
    .option('-y, --year <year>', '发行年份')
    .option('-r, --rating <rating>', '评分', parseFloat)
    .option('-d, --description <desc>', '描述')
    .option('-t, --table <name>', '表名', 'albums')
    .action(async (options) => {
    try {
        await (0, database_1.initDatabase)();
        const album = (0, album_service_1.addAlbum)({
            album_name: options.name,
            artist: options.artist,
            country: options.country,
            genre: options.genre,
            release_year: options.year,
            rating: options.rating,
            description: options.description,
        }, options.table);
        console.log(`\n✅ 专辑添加成功!`);
        console.log(`ID: ${album.album_id}`);
        console.log(`表: ${options.table}`);
        console.log(`专辑名: ${album.album_name}`);
        console.log(`艺术家: ${album.artist}`);
        (0, database_1.closeDatabase)();
    }
    catch (error) {
        console.error('错误:', error);
        process.exit(1);
    }
});
// 编辑专辑
program
    .command('edit')
    .description('编辑专辑信息（自动检测专辑所在表）')
    .requiredOption('-i, --id <id>', '专辑 ID', parseInt)
    .option('-n, --name <name>', '专辑名')
    .option('-a, --artist <artist>', '艺术家')
    .option('-c, --country <country>', '国家')
    .option('-g, --genre <genre>', '风格')
    .option('-y, --year <year>', '发行年份')
    .option('-r, --rating <rating>', '评分', parseFloat)
    .option('-d, --description <desc>', '描述')
    .option('-t, --table <name>', '表名（省略则自动扫描所有表检测）')
    .action(async (options) => {
    try {
        await (0, database_1.initDatabase)();
        const updates = {};
        if (options.name)
            updates.album_name = options.name;
        if (options.artist)
            updates.artist = options.artist;
        if (options.country)
            updates.country = options.country;
        if (options.genre)
            updates.genre = options.genre;
        if (options.year)
            updates.release_year = options.year;
        if (options.rating)
            updates.rating = options.rating;
        if (options.description)
            updates.description = options.description;
        if (Object.keys(updates).length === 0) {
            console.log('没有需要更新的字段');
            process.exit(1);
        }
        // 自动检测专辑所在表（年份表优先）
        const tables = options.table
            ? [options.table]
            : ['albums_2026', 'albums_2025', 'albums_2024', 'albums'];
        let foundTable = null;
        let album = null;
        for (const tbl of tables) {
            const a = (0, album_service_1.getAlbumById)(options.id, tbl);
            if (a) {
                foundTable = tbl;
                album = a;
                break;
            }
        }
        if (!album || !foundTable) {
            console.log(`❌ 未找到 ID 为 ${options.id} 的专辑（已扫描: ${tables.join(', ')}）`);
            process.exit(1);
        }
        const updated = (0, album_service_1.updateAlbum)(options.id, updates, foundTable);
        console.log(`\n✅ 专辑更新成功!`);
        console.log(`ID: ${album.album_id}`);
        console.log(`所在表: ${foundTable}`);
        console.log(`专辑名: ${updated.album_name}`);
        (0, database_1.closeDatabase)();
    }
    catch (error) {
        console.error('错误:', error);
        process.exit(1);
    }
});
// 删除专辑
program
    .command('delete')
    .description('删除专辑（自动检测专辑所在表）')
    .requiredOption('-i, --id <id>', '专辑 ID', parseInt)
    .option('-t, --table <name>', '表名（省略则自动扫描所有表检测）')
    .option('-y, --yes', '确认删除（跳过确认提示）')
    .action(async (options) => {
    try {
        await (0, database_1.initDatabase)();
        // 自动检测专辑所在表（年份表优先）
        const tables = options.table
            ? [options.table]
            : ['albums_2026', 'albums_2025', 'albums_2024', 'albums'];
        let foundTable = null;
        let album = null;
        for (const tbl of tables) {
            const a = (0, album_service_1.getAlbumById)(options.id, tbl);
            if (a) {
                foundTable = tbl;
                album = a;
                break;
            }
        }
        if (!album || !foundTable) {
            console.log(`❌ 未找到 ID 为 ${options.id} 的专辑（已扫描: ${tables.join(', ')}）`);
            process.exit(1);
        }
        if (!options.yes) {
            console.log(`\n⚠️  确认删除?`);
            console.log(`专辑: ${album.album_name}`);
            console.log(`艺术家: ${album.artist}`);
            console.log(`所在表: ${foundTable}`);
            console.log(`\n输入 y 确认删除:`);
            console.log('(使用 --yes 参数跳过确认)');
            process.exit(1);
        }
        const deleted = (0, album_service_1.deleteAlbum)(options.id, foundTable);
        if (deleted) {
            console.log(`\n✅ 专辑已删除: ${album.album_name}（来自 ${foundTable}）`);
        }
        (0, database_1.closeDatabase)();
    }
    catch (error) {
        console.error('错误:', error);
        process.exit(1);
    }
});
// 记录收听
program
    .command('listen')
    .description('记录收听次数（自动检测专辑所在表）')
    .requiredOption('-i, --id <id>', '专辑 ID', parseInt)
    .option('-c, --count <count>', '收听次数', parseInt, 1)
    .option('-t, --table <name>', '表名（省略则自动扫描所有表检测）')
    .action(async (options) => {
    try {
        await (0, database_1.initDatabase)();
        // 自动检测专辑所在表（年份表优先，因为数据更近）
        const tables = options.table
            ? [options.table]
            : ['albums_2026', 'albums_2025', 'albums_2024', 'albums'];
        let foundTable = null;
        let foundAlbum = null;
        for (const tbl of tables) {
            const album = (0, album_service_1.getAlbumById)(options.id, tbl);
            if (album) {
                foundTable = tbl;
                foundAlbum = album;
                break;
            }
        }
        if (!foundAlbum || !foundTable) {
            console.log(`❌ 未找到 ID 为 ${options.id} 的专辑（已扫描: ${tables.join(', ')}）`);
            process.exit(1);
        }
        // 记录收听
        const updated = (0, album_service_1.recordListen)(options.id, options.count, foundTable);
        console.log(`\n✅ 收听记录已更新`);
        console.log(`专辑: ${updated.album_name}`);
        console.log(`艺术家: ${updated.artist}`);
        console.log(`收听次数: ${updated.total_listen_count} (+${options.count})`);
        console.log(`首次收听: ${updated.first_listen_date}`);
        console.log(`所在表: ${foundTable}`);
        (0, database_1.closeDatabase)();
    }
    catch (error) {
        console.error('错误:', error);
        process.exit(1);
    }
});
// ==================== 统计命令 ====================
// 统计概览（只查 albums 表）
program
    .command('stats')
    .description('统计信息（总览）- 只查 albums 表')
    .option('-t, --table <name>', '指定表名', 'albums')
    .action(async (options) => {
    try {
        await (0, database_1.initDatabase)();
        const tableName = options.table || 'albums';
        const stats = (0, album_service_1.getStatsOverview)(tableName);
        const allCounts = (0, album_service_1.getAllTableCounts)();
        console.log(`\n📊 ${tableName} 表统计`);
        console.log('═'.repeat(50));
        console.log('\n📈 各表专辑数量');
        for (const [table, count] of Object.entries(allCounts)) {
            const label = table.padEnd(12);
            const marker = table === tableName ? ' ◀' : '';
            console.log(`   ${label} ${count}${marker}`);
        }
        console.log('\n🎵 收听统计');
        console.log(`   本表专辑数: ${stats.total}`);
        console.log(`   总收听次数: ${stats.totalListens}`);
        console.log(`   平均每张:   ${stats.avgListens}次`);
        if (stats.maxListen) {
            console.log(`   最高收听:   ${stats.maxListen.count}次`);
            console.log(`   专辑: ${stats.maxListen.album.album_name} - ${stats.maxListen.album.artist}`);
        }
        // 风格分布
        console.log('\n🎸 风格 Top 5');
        const genres = (0, album_service_1.getGenreStats)(tableName, 5);
        for (const g of genres) {
            console.log(`   ${g.genre.padEnd(15)} ${g.count} (${g.percentage}%)`);
        }
        // 国家分布
        console.log('\n🌍 国家 Top 5');
        const countries = (0, album_service_1.getCountryStats)(tableName, 5);
        for (const c of countries) {
            console.log(`   ${c.country.padEnd(10)} ${c.count} (${c.percentage}%)`);
        }
        // 年份分布
        console.log('\n📅 发行年份 Top 10');
        const years = (0, album_service_1.getYearStats)(tableName, 10);
        for (const y of years) {
            console.log(`   ${y.year.padEnd(6)} ${y.count}`);
        }
        (0, database_1.closeDatabase)();
    }
    catch (error) {
        console.error('错误:', error);
        process.exit(1);
    }
});
// 排行榜
// 规则：默认查 albums 表（总排行），可用 --year 指定年表
program
    .command('top')
    .description('收听排行榜（默认只查 albums 表）')
    .option('-l, --limit <number>', '数量', '10')
    .option('-y, --year <year>', '指定年份（2024/2025），查询对应年表')
    .option('-t, --table <name>', '直接指定表名')
    .action(async (options) => {
    try {
        await (0, database_1.initDatabase)();
        // 确定查询的表
        let tableName = 'albums';
        let title = '总排行（albums 表）';
        if (options.table) {
            tableName = options.table;
            title = `${tableName} 表`;
        }
        else if (options.year) {
            tableName = `albums_${options.year}`;
            title = `${options.year}年表（albums_${options.year} 表）`;
        }
        const albums = (0, album_service_1.getTopAlbums)(parseInt(options.limit), [tableName]);
        console.log(`\n🏆 收听次数 Top ${albums.length} - ${title}`);
        console.log('═'.repeat(60));
        for (let i = 0; i < albums.length; i++) {
            const album = albums[i];
            const bar = '█'.repeat(Math.min(album.total_listen_count, 20));
            console.log(`${String(i + 1).padStart(2)}. ${album.album_name.slice(0, 20).padEnd(20)} ${album.total_listen_count} ${bar}`);
            console.log(`    ${album.artist} [${album.source_table}]`);
        }
        (0, database_1.closeDatabase)();
    }
    catch (error) {
        console.error('错误:', error);
        process.exit(1);
    }
});
// ==================== 启动 ====================
// Helper function
function required(val) {
    if (!val) {
        throw new Error('此参数为必填');
    }
    return val;
}
// 解析命令行参数
program.parse();
