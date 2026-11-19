import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';

export const PROJECT_ROOT = fileURLToPath(new URL('../../../', import.meta.url));

export function readConfig(env = process.env) {
  const port = Number(env.PORT || 3001);
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new Error('PORT must be an integer between 1 and 65535.');
  }
  let appOrigin;
  if (env.APP_ORIGIN) {
    const url = new URL(env.APP_ORIGIN);
    if (
      !['http:', 'https:'].includes(url.protocol) ||
      url.username ||
      url.password ||
      url.pathname !== '/' ||
      url.search ||
      url.hash
    ) {
      throw new Error('APP_ORIGIN must be an http or https origin without a path.');
    }
    appOrigin = url.origin;
  }
  let supabase;
  if (env.SUPABASE_URL || env.SUPABASE_PUBLISHABLE_KEY) {
    if (!env.SUPABASE_URL || !env.SUPABASE_PUBLISHABLE_KEY || !appOrigin) {
      throw new Error('Set SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY and APP_ORIGIN together.');
    }
    const url = new URL(env.SUPABASE_URL);
    const local = ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname);
    if (
      (url.protocol !== 'https:' && !(url.protocol === 'http:' && local)) ||
      url.username ||
      url.password ||
      url.pathname !== '/' ||
      url.search ||
      url.hash
    ) {
      throw new Error('SUPABASE_URL must be an HTTPS origin or a local Supabase origin.');
    }
    supabase = { url: url.origin, key: env.SUPABASE_PUBLISHABLE_KEY };
  }
  return {
    host: env.HOST || '127.0.0.1',
    port,
    databasePath: resolve(PROJECT_ROOT, env.DATABASE_PATH || 'data/voltforge.sqlite'),
    webDist: resolve(PROJECT_ROOT, 'apps/web/dist'),
    appOrigin,
    supabase,
  };
}
