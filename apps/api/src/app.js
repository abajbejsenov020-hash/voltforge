import { openDatabase } from './database.js';
import { createRepository, RevisionConflict } from './repository.js';
import { HttpError, readJson, sendJson } from './http.js';
import { createBuildValidator, validateRevision } from './validation.js';
import { serveStatic } from './static.js';
import { createHostedAuth } from './supabase-auth.js';
import { createSupabaseBuildRepository } from './supabase-builds.js';

export const SESSION_COOKIE = 'voltforge_session';
const DEV_ORIGINS = new Set(['http://localhost:5173', 'http://127.0.0.1:5173']);
const MUTATING_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

function enforceOrigin(request, response, appOrigin, hosted) {
  const origin = request.headers.origin;
  const protocol = request.socket.encrypted ? 'https:' : 'http:';
  const ownOrigin = `${protocol}//${request.headers.host}`;
  const allowed = hosted
    ? origin === appOrigin
    : origin === ownOrigin || origin === appOrigin || DEV_ORIGINS.has(origin);
  if (origin && !allowed)
    throw new HttpError(403, 'ORIGIN_NOT_ALLOWED', 'This request origin is not allowed.');
  if (
    !origin &&
    MUTATING_METHODS.has(request.method) &&
    request.headers['sec-fetch-site'] === 'cross-site'
  ) {
    throw new HttpError(403, 'ORIGIN_NOT_ALLOWED', 'Cross-site changes are not allowed.');
  }
  if (origin && allowed) {
    response.setHeader('Access-Control-Allow-Origin', origin);
    response.setHeader('Access-Control-Allow-Credentials', 'true');
    response.setHeader('Vary', 'Origin');
  }
}

function cookieToken(header = '') {
  for (const cookie of header.split(';')) {
    const offset = cookie.indexOf('=');
    if (cookie.slice(0, offset).trim() === SESSION_COOKIE) return cookie.slice(offset + 1).trim();
  }
}

function requireMethod(request, response, allowed) {
  if (!allowed.includes(request.method)) {
    response.setHeader('Allow', allowed.join(', '));
    throw new HttpError(405, 'METHOD_NOT_ALLOWED', `This endpoint supports ${allowed.join(', ')}.`);
  }
}

function routeId(pathname) {
  const match = /^\/api\/builds\/([^/]+)$/.exec(pathname);
  if (!match) return;
  let id;
  try {
    id = decodeURIComponent(match[1]);
  } catch {
    throw new HttpError(400, 'INVALID_PATH', 'The build ID is invalid.');
  }
  if (!id.trim() || id.length > 100 || /[\u0000-\u001f\u007f]/.test(id)) {
    throw new HttpError(400, 'INVALID_PATH', 'The build ID is invalid.');
  }
  return id;
}

export function createApp({
  databasePath = ':memory:',
  webDist,
  appOrigin,
  supabase,
  catalog = [],
  categories = [],
  findVehicles = () => [],
  vehicleIndex,
  estimatePerformance = () => ({}),
  onError = console.error,
} = {}) {
  const database = supabase ? null : openDatabase(databasePath);
  const repository = supabase
    ? createSupabaseBuildRepository(supabase)
    : createRepository(database);
  const auth = supabase ? createHostedAuth({ ...supabase, appOrigin }) : null;
  const validateBuild = createBuildValidator(catalog, categories);

  function session(request, response) {
    const resolved = repository.resolveSession(cookieToken(request.headers.cookie));
    if (resolved.token) {
      const secure = appOrigin?.startsWith('https:') || request.socket.encrypted;
      response.setHeader(
        'Set-Cookie',
        `${SESSION_COOKIE}=${resolved.token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=31536000${secure ? '; Secure' : ''}`,
      );
    }
    return resolved.hash;
  }

  async function buildOwner(request, response) {
    if (!auth) return session(request, response);
    const expected = request.headers['x-voltmodd-account'];
    if (typeof expected !== 'string' || !expected)
      throw new HttpError(401, 'LOGIN_REQUIRED', 'Log in to access your saved builds.');
    const active = await auth.session(request, response, expected);
    if (!active) throw new HttpError(401, 'LOGIN_REQUIRED', 'Log in to access your saved builds.');
    if (expected !== active.user.id)
      throw new HttpError(
        409,
        'ACCOUNT_CHANGED',
        'The signed-in account changed. Reload your garage.',
      );
    return active.accessToken;
  }

  async function route(request, response) {
    const url = new URL(request.url, 'http://localhost');
    const { pathname } = url;
    if (!pathname.startsWith('/api/') && pathname !== '/api') {
      return serveStatic(request, response, pathname, webDist);
    }
    enforceOrigin(request, response, appOrigin, Boolean(auth));
    if (request.method === 'OPTIONS') {
      response.writeHead(204, {
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, X-Voltmodd-Account',
        'Access-Control-Max-Age': '600',
        'Cache-Control': 'no-store',
      });
      return response.end();
    }
    if (pathname === '/api/health') {
      requireMethod(request, response, ['GET']);
      return sendJson(response, 200, { ok: true, service: 'voltforge-api' });
    }
    if (pathname.startsWith('/api/auth/')) {
      if (auth) return auth.route(request, response, url, requireMethod);
      if (pathname === '/api/auth/session') {
        requireMethod(request, response, ['GET']);
        return sendJson(response, 200, { enabled: false, user: null });
      }
      throw new HttpError(404, 'NOT_FOUND', 'The API endpoint does not exist.');
    }
    if (pathname === '/api/catalog') {
      requireMethod(request, response, ['GET']);
      return sendJson(response, 200, { catalog, categories });
    }
    if (pathname === '/api/vehicles') {
      requireMethod(request, response, ['GET']);
      const query = url.searchParams.get('q') || '';
      const type = url.searchParams.get('type') || 'all';
      if (query.length > 150 || !['all', 'bike', 'scooter'].includes(type)) {
        throw new HttpError(
          422,
          'INVALID_QUERY',
          'Use a query of at most 150 characters and type all, bike, or scooter.',
        );
      }
      const results =
        !query && type === 'all' && vehicleIndex
          ? vehicleIndex
          : findVehicles(query, { type: type === 'all' ? 'scooter' : type });
      return sendJson(response, 200, {
        vehicles: results.filter((vehicle) => type === 'all' || vehicle.type === type),
      });
    }
    if (pathname === '/api/performance') {
      requireMethod(request, response, ['POST']);
      const { build } = await readJson(request);
      return sendJson(response, 200, { performance: estimatePerformance(validateBuild(build)) });
    }
    if (pathname === '/api/builds') {
      requireMethod(request, response, ['GET']);
      const owner = await buildOwner(request, response);
      return sendJson(response, 200, { builds: await repository.listBuilds(owner) });
    }
    if (pathname === '/api/builds/import') {
      requireMethod(request, response, ['POST']);
      const body = await readJson(request);
      if (!Array.isArray(body.builds) || body.builds.length > 500) {
        throw new HttpError(
          422,
          'INVALID_IMPORT',
          'builds must be an array of at most 500 builds.',
        );
      }
      const builds = body.builds.map((build) => validateBuild(build));
      const owner = await buildOwner(request, response);
      return sendJson(response, 200, await repository.importBuilds(owner, builds));
    }
    const id = routeId(pathname);
    if (id !== undefined) {
      requireMethod(request, response, ['PUT', 'DELETE']);
      if (request.method === 'PUT') {
        const body = await readJson(request);
        const build = validateBuild(body.build, id);
        const expectedRevision = validateRevision(body.expectedRevision);
        const owner = await buildOwner(request, response);
        const result = await repository.saveBuild(owner, build, expectedRevision);
        return sendJson(response, result.created ? 201 : 200, result);
      }
      if (!(await repository.deleteBuild(await buildOwner(request, response), id))) {
        throw new HttpError(404, 'BUILD_NOT_FOUND', 'The build does not exist in this garage.');
      }
      return sendJson(response, 200, { deleted: true });
    }
    throw new HttpError(404, 'NOT_FOUND', 'The API endpoint does not exist.');
  }

  let closed = false;
  return {
    handler(request, response) {
      response.setHeader('X-Content-Type-Options', 'nosniff');
      response.setHeader('Referrer-Policy', 'same-origin');
      response.setHeader('X-Frame-Options', 'DENY');
      route(request, response).catch((error) => {
        if (response.headersSent || response.destroyed) {
          if (!response.destroyed) response.destroy();
          return;
        }
        if (error instanceof RevisionConflict) {
          return sendJson(response, 409, {
            error: {
              code: 'REVISION_CONFLICT',
              message: error.message,
              currentRevision: error.currentRevision,
            },
          });
        }
        if (error instanceof HttpError) {
          return sendJson(response, error.status, {
            error: {
              code: error.code,
              message: error.message,
              ...(error.details && { details: error.details }),
            },
          });
        }
        onError(error);
        return sendJson(response, 500, {
          error: {
            code: 'INTERNAL_ERROR',
            message: 'The request could not be completed. Please try again.',
          },
        });
      });
    },
    close() {
      if (!closed) {
        closed = true;
        database?.close();
      }
    },
  };
}
