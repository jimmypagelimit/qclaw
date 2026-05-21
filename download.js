const https = require('https');
const fs = require('fs');

const url = 'https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/latest.tar.gz';
const outPath = 'C:\\Users\\15206\\.qclaw\\workspace\\latest.tar.gz';

console.log('Downloading...');

const chunks = [];

https.get(url, (response) => {
    console.log('Status:', response.statusCode);
    response.on('data', (chunk) => chunks.push(chunk));
    response.on('end', () => {
        const buffer = Buffer.concat(chunks);
        console.log('Total size:', buffer.length);
        fs.writeFileSync(outPath, buffer);
        console.log('Written to disk, size on disk:', fs.statSync(outPath).size);
    });
}).on('error', (e) => console.error('Error:', e.message));
