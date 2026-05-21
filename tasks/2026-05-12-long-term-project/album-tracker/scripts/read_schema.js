#!/usr/bin/env node
/**
 * 读取 SQLite 数据库表结构 (使用 sql.js)
 * 用法: node read_schema.js <database_path>
 */

const SQL = require('sql.js');
const fs = require('fs');
const path = require('path');

function readSchema(dbPath) {
    console.log(`📊 读取数据库: ${dbPath}\n`);
    
    try {
        // 读取数据库文件
        const buffer = fs.readFileSync(dbPath);
        const db = new SQL.Database(buffer);
        
        // 获取所有表
        const tablesResult = db.exec("SELECT name FROM sqlite_master WHERE type='table'");
        
        if (!tablesResult || tablesResult.length === 0 || !tablesResult[0].values) {
            console.log('❌ 没有找到任何表');
            return;
        }
        
        const tables = tablesResult[0].values.map(row => row[0]);
        console.log(`📋 找到 ${tables.length} 个表:\n`);
        
        // 遍历每个表
        for (const tableName of tables) {
            console.log('='.repeat(70));
            console.log(`表: ${tableName}`);
            console.log('='.repeat(70));
            
            // 获取表结构 (PRAGMA table_info)
            const schemaResult = db.exec(`PRAGMA table_info(${tableName})`);
            
            if (schemaResult && schemaResult[0] && schemaResult[0].values) {
                const columns = schemaResult[0].values;
                
                console.log(`\n字段 (${columns.length} 个):`);
                console.log(`${'ID':<5} ${'名称':<20} ${'类型':<15} ${'非空':<5} ${'默认值':<15} ${'主键':<5}`);
                console.log('-'.repeat(70));
                
                for (const col of columns) {
                    const [cid, name, dtype, notnull, dflt_value, pk] = col;
                    const notnullStr = notnull ? 'YES' : 'NO';
                    const pkStr = pk ? 'YES' : 'NO';
                    const defaultStr = dflt_value !== null ? String(dflt_value) : 'NULL';
                    console.log(`${cid:<5} ${name:<20} ${dtype:<15} ${notnullStr:<5} ${defaultStr:<15} ${pkStr:<5}`);
                }
            }
            
            // 获取样例数据（前3行）
            try {
                const sampleResult = db.exec(`SELECT * FROM ${tableName} LIMIT 3`);
                
                if (sampleResult && sampleResult[0] && sampleResult[0].values) {
                    const rows = sampleResult[0].values;
                    const columns = sampleResult[0].columns;
                    
                    console.log(`\n样例数据 (前${rows.length}行):`);
                    console.log(`列: ${columns.join(', ')}`);
                    
                    for (let i = 0; i < rows.length; i++) {
                        console.log(`  行${i+1}: ${JSON.stringify(rows[i])}`);
                    }
                }
            } catch (e) {
                console.log(`\n⚠️  无法读取样例数据: ${e.message}`);
            }
            
            // 获取记录总数
            try {
                const countResult = db.exec(`SELECT COUNT(*) as count FROM ${tableName}`);
                if (countResult && countResult[0] && countResult[0].values) {
                    const count = countResult[0].values[0][0];
                    console.log(`\n总记录数: ${count}\n`);
                }
            } catch (e) {
                console.log(`\n⚠️  无法获取记录数: ${e.message}\n`);
            }
        }
        
        db.close();
        console.log('✅ 数据库结构读取完成!');
        
    } catch (error) {
        console.error(`❌ 错误: ${error.message}`);
        process.exit(1);
    }
}

// 主程序
if (require.main === module) {
    if (process.argv.length < 3) {
        console.log('用法: node read_schema.js <database_path>');
        console.log('示例: node read_schema.js "G:\\原创计划\\music"');
        process.exit(1);
    }
    
    const dbPath = process.argv[2];
    
    if (!fs.existsSync(dbPath)) {
        console.error(`❌ 文件不存在: ${dbPath}`);
        process.exit(1);
    }
    
    readSchema(dbPath);
}
