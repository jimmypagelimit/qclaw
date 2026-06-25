process.chdir('C:/Users/qujt/.qclaw/workspace/tasks/2026-05-12-long-term-project/album-tracker');
const { execSync } = require('child_process');
try {
  const out = execSync('node dist/cli.js --help', { encoding: 'utf8', timeout: 15000 });
  console.log('STDOUT:', out);
} catch (e) {
  console.log('Error:', e.message);
  console.log('STDOUT:', e.stdout?.toString() || '');
  console.log('STDERR:', e.stderr?.toString() || '');
}
