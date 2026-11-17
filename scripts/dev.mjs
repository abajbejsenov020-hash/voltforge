import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
const root = fileURLToPath(new URL('../', import.meta.url));
const api = spawn(process.execPath, ['--watch', 'apps/api/src/index.js'], {
  cwd: root,
  stdio: 'inherit',
});
const web = spawn(
  process.execPath,
  [root + 'node_modules/vite/bin/vite.js', '--host', '127.0.0.1'],
  {
    cwd: root + '/apps/web',
    stdio: 'inherit',
  },
);
let stopping = false;
function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  api.kill();
  web.kill();
  process.exitCode = code;
}
process.on('SIGINT', () => stop());
process.on('SIGTERM', () => stop());
for (const child of [api, web]) child.on('exit', (code) => stop(code || 0));
