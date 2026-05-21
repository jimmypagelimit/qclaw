/**
 * 构建脚本 - 使用 esbuild 编译 TypeScript
 * 构建 CLI 和 Server 两个入口
 */

const esbuild = require('esbuild');
const path = require('path');

const srcDir = path.join(__dirname, '..', 'src');
const distDir = path.join(__dirname, '..', 'dist');

async function build() {
  try {
    // 构建 CLI
    await esbuild.build({
      entryPoints: [path.join(srcDir, 'cli.ts')],
      bundle: true,
      platform: 'node',
      target: 'node18',
      outfile: path.join(distDir, 'cli.js'),
      format: 'cjs',
      sourcemap: true,
      external: ['sql.js'],
    });

    // 构建 Server
    await esbuild.build({
      entryPoints: [path.join(srcDir, 'server.ts')],
      bundle: true,
      platform: 'node',
      target: 'node18',
      outfile: path.join(distDir, 'server.js'),
      format: 'cjs',
      sourcemap: true,
      external: ['sql.js'],
    });

    // 构建封面下载脚本
    await esbuild.build({
      entryPoints: [path.join(srcDir, 'download-covers.ts')],
      bundle: true,
      platform: 'node',
      target: 'node18',
      outfile: path.join(distDir, 'download-covers.js'),
      format: 'cjs',
      sourcemap: true,
      external: ['sql.js'],
    });

    console.log('✅ 构建成功:');
    console.log('   dist/cli.js              - CLI 工具');
    console.log('   dist/server.js           - Web 服务器');
    console.log('   dist/download-covers.js  - 封面下载');
  } catch (error) {
    console.error('❌ 构建失败:', error);
    process.exit(1);
  }
}

build();
