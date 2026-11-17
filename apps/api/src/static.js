import { createReadStream } from 'node:fs';
import { realpath, stat } from 'node:fs/promises';
import { extname, resolve, sep } from 'node:path';
import { pipeline } from 'node:stream/promises';
import { HttpError } from './http.js';

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.map': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.avif': 'image/avif',
  '.gif': 'image/gif',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.txt': 'text/plain; charset=utf-8',
};

const within = (root, target) => target === root || target.startsWith(root + sep);

export async function serveStatic(request, response, pathname, webDist) {
  if (!webDist) throw new HttpError(404, 'NOT_FOUND', 'The requested resource does not exist.');
  if (!['GET', 'HEAD'].includes(request.method)) {
    response.setHeader('Allow', 'GET, HEAD');
    throw new HttpError(405, 'METHOD_NOT_ALLOWED', 'This resource supports GET and HEAD.');
  }
  let decoded;
  try {
    decoded = decodeURIComponent(pathname);
  } catch {
    throw new HttpError(400, 'INVALID_PATH', 'The request path is invalid.');
  }
  if (
    decoded.includes('\0') ||
    decoded.includes('\\') ||
    decoded.split('/').some((piece) => piece.startsWith('.'))
  ) {
    throw new HttpError(404, 'NOT_FOUND', 'The requested resource does not exist.');
  }
  let root;
  try {
    root = await realpath(webDist);
  } catch {
    throw new HttpError(
      404,
      'WEB_NOT_BUILT',
      'Build the web app before serving the production site.',
    );
  }
  let file = resolve(root, '.' + decoded);
  if (!within(root, file))
    throw new HttpError(404, 'NOT_FOUND', 'The requested resource does not exist.');
  let info;
  try {
    info = await stat(file);
  } catch (error) {
    if (!['ENOENT', 'ENOTDIR'].includes(error.code)) throw error;
  }
  if (info?.isDirectory() || (!info && !extname(decoded))) {
    file = resolve(root, 'index.html');
    try {
      info = await stat(file);
    } catch {
      info = undefined;
    }
  }
  if (!info?.isFile())
    throw new HttpError(404, 'NOT_FOUND', 'The requested resource does not exist.');
  file = await realpath(file);
  if (!within(root, file))
    throw new HttpError(404, 'NOT_FOUND', 'The requested resource does not exist.');
  response.writeHead(200, {
    'Content-Type': MIME_TYPES[extname(file).toLowerCase()] || 'application/octet-stream',
    'Content-Length': info.size,
    'Cache-Control': file.endsWith('.html') ? 'no-cache' : 'public, max-age=3600',
  });
  if (request.method === 'HEAD') response.end();
  else await pipeline(createReadStream(file), response);
}
