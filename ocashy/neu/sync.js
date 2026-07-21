const fs = require('fs');
const path = require('path');

const srcDir = path.join(__dirname, '../svelte-app/public');
const destDir = path.join(__dirname, 'resources');

console.log(`Syncing frontend assets from ${srcDir} to ${destDir}...`);

// Copy files recursively from srcDir to destDir
try {
  fs.cpSync(srcDir, destDir, {
    recursive: true,
    force: true
  });
  console.log('Sync completed successfully.');
} catch (err) {
  console.error('Error syncing assets:', err);
  process.exit(1);
}
