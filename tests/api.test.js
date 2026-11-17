import test from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { once } from 'node:events';
import { mkdtemp, mkdir, rm, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { DatabaseSync } from 'node:sqlite';
import { createApp, SESSION_COOKIE } from '../apps/api/src/app.js';
import { readConfig, PROJECT_ROOT } from '../apps/api/src/config.js';

const categories = ['Motors', 'Batteries'];
const catalog = [
  { id: 'motor-a', category: 'Motors', name: 'Test motor', type: 'both' },
  { id: 'battery-a', category: 'Batteries', name: 'Test battery', type: 'both' },
];
const build = (id = 'build-a') => ({
  id,
  name: 'City commuter',
  type: 'scooter',
  mode: 'new',
  vehicle: 'Test scooter',
  selected: { Motors: 'motor-a', Batteries: 'battery-a' },
  specs: { dropout: '', fullV: '84', bms: '80', batteryLimit: 80, motorCount: 2 },
  performance: {
    schema: 2,
    configuration: 'auto',
    rider: '80',
    vehicle: 30,
    cruise: 25,
    wind: -2,
    grade: '',
  },
  updated: 1_700_000_000_000,
});

async function fixture(t, options = {}) {
  const directory = await mkdtemp(join(tmpdir(), 'voltforge-api-'));
  const databasePath = join(directory, 'builds.sqlite');
  const errors = [];
  let app;
  let server;
  let baseUrl;
  async function start(overrides = {}) {
    app = createApp({
      databasePath,
      catalog,
      categories,
      findVehicles: (query, { type }) => [{ id: query || 'all', type }],
      estimatePerformance: (value) => ({
        speed: { value: Number(value.performance.cruise) },
        wh: 1000,
      }),
      onError: (error) => errors.push(error),
      ...options,
      ...overrides,
    });
    server = createServer(app.handler);
    server.listen(0, '127.0.0.1');
    await once(server, 'listening');
    baseUrl = `http://127.0.0.1:${server.address().port}`;
  }
  async function stop() {
    await new Promise((resolve, reject) =>
      server.close((error) => (error ? reject(error) : resolve())),
    );
    app.close();
  }
  await start();
  t.after(async () => {
    await stop();
    await rm(directory, { recursive: true, force: true });
    assert.deepEqual(errors, []);
  });
  return {
    directory,
    databasePath,
    async request(path, { method = 'GET', body, cookie, headers = {}, raw } = {}) {
      const response = await fetch(baseUrl + path, {
        method,
        headers: {
          ...(body !== undefined || raw !== undefined
            ? { 'Content-Type': 'application/json' }
            : {}),
          ...(cookie ? { Cookie: cookie } : {}),
          ...headers,
        },
        body: raw !== undefined ? raw : body !== undefined ? JSON.stringify(body) : undefined,
      });
      const text = await response.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        data = text;
      }
      return {
        status: response.status,
        headers: response.headers,
        data,
        cookie: response.headers.get('set-cookie')?.split(';')[0],
      };
    },
    async restart() {
      await stop();
      await start();
    },
  };
}

test('catalog, vehicles, health, and performance routes use the domain contracts', async (t) => {
  const api = await fixture(t);
  const health = await api.request('/api/health');
  assert.equal(health.status, 200);
  assert.equal(health.data.ok, true);
  assert.equal(health.headers.get('x-content-type-options'), 'nosniff');
  const parts = await api.request('/api/catalog');
  assert.deepEqual(parts.data, { catalog, categories });
  const vehicles = await api.request('/api/vehicles?q=commuter&type=scooter');
  assert.deepEqual(vehicles.data.vehicles, [{ id: 'commuter', type: 'scooter' }]);
  assert.equal((await api.request('/api/vehicles?type=car')).status, 422);
  const estimate = await api.request('/api/performance', {
    method: 'POST',
    body: { build: build() },
  });
  assert.equal(estimate.status, 200);
  assert.equal(estimate.data.performance.speed.value, 25);
  assert.equal((await api.request('/api/catalog', { method: 'DELETE' })).status, 405);
  assert.equal((await api.request('/api/unknown')).status, 404);
});

test('builds persist across restart and every operation stays inside the browser session', async (t) => {
  const api = await fixture(t);
  const initial = await api.request('/api/builds');
  assert.deepEqual(initial.data.builds, []);
  assert.match(initial.headers.get('set-cookie'), /HttpOnly; SameSite=Lax/);
  assert.match(initial.cookie, new RegExp(`^${SESSION_COOKIE}=[A-Za-z0-9_-]{43}$`));
  const saved = await api.request('/api/builds/build-a', {
    method: 'PUT',
    cookie: initial.cookie,
    body: { build: build(), expectedRevision: 0 },
  });
  assert.equal(saved.status, 201);
  assert.equal(saved.data.build.revision, 1);
  assert.equal(saved.data.build.specs.fullV, '84');
  const outsider = await api.request('/api/builds');
  assert.notEqual(outsider.cookie, initial.cookie);
  assert.deepEqual(outsider.data.builds, []);
  assert.equal(
    (await api.request('/api/builds/build-a', { method: 'DELETE', cookie: outsider.cookie }))
      .status,
    404,
  );
  const otherSaved = await api.request('/api/builds/build-a', {
    method: 'PUT',
    cookie: outsider.cookie,
    body: { build: { ...build(), name: 'Separate build' }, expectedRevision: 0 },
  });
  assert.equal(otherSaved.status, 201);
  assert.equal(
    (await api.request('/api/builds', { cookie: initial.cookie })).data.builds[0].name,
    'City commuter',
  );
  const database = new DatabaseSync(api.databasePath);
  const sessions = database.prepare('SELECT token_hash FROM sessions').all();
  database.close();
  assert.equal(sessions.length, 2);
  assert.ok(sessions.every((row) => /^[a-f0-9]{64}$/.test(row.token_hash)));
  assert.ok(!sessions.some((row) => row.token_hash === initial.cookie.split('=')[1]));
  await api.restart();
  const persisted = await api.request('/api/builds', { cookie: initial.cookie });
  assert.equal(persisted.data.builds.length, 1);
  assert.equal(persisted.data.builds[0].revision, 1);
  assert.equal(persisted.headers.get('set-cookie'), null);
  const removed = await api.request('/api/builds/build-a', {
    method: 'DELETE',
    cookie: initial.cookie,
  });
  assert.equal(removed.status, 200);
  assert.deepEqual((await api.request('/api/builds', { cookie: initial.cookie })).data.builds, []);
  assert.equal(
    (await api.request('/api/builds', { cookie: outsider.cookie })).data.builds.length,
    1,
  );
});

test('stale revisions fail with 409 and simultaneous writers cannot overwrite each other', async (t) => {
  const api = await fixture(t);
  const { cookie } = await api.request('/api/builds');
  await api.request('/api/builds/build-a', {
    method: 'PUT',
    cookie,
    body: { build: build(), expectedRevision: 0 },
  });
  const results = await Promise.all(
    ['First', 'Second'].map((name) =>
      api.request('/api/builds/build-a', {
        method: 'PUT',
        cookie,
        body: { build: { ...build(), name }, expectedRevision: 1 },
      }),
    ),
  );
  assert.deepEqual(results.map((result) => result.status).sort(), [200, 409]);
  const conflict = results.find((result) => result.status === 409);
  assert.equal(conflict.data.error.code, 'REVISION_CONFLICT');
  assert.equal(conflict.data.error.currentRevision, 2);
  const saved = (await api.request('/api/builds', { cookie })).data.builds[0];
  assert.equal(saved.revision, 2);
  assert.equal(saved.name, results.find((result) => result.status === 200).data.build.name);
  assert.equal(
    (
      await api.request('/api/builds/build-a', {
        method: 'PUT',
        cookie,
        body: { build: build(), expectedRevision: -1 },
      })
    ).status,
    422,
  );
});

test('legacy imports are idempotent, preserve dates, and validate before any write', async (t) => {
  const api = await fixture(t);
  const { cookie } = await api.request('/api/builds');
  const imported = await api.request('/api/builds/import', {
    method: 'POST',
    cookie,
    body: { builds: [build(), build('build-b'), build()] },
  });
  assert.equal(imported.status, 200);
  assert.equal(imported.data.imported, 2);
  assert.equal(imported.data.skipped, 1);
  assert.equal(imported.data.builds[0].updated, build().updated);
  const repeated = await api.request('/api/builds/import', {
    method: 'POST',
    cookie,
    body: { builds: [{ ...build(), name: 'Must not overwrite' }] },
  });
  assert.equal(repeated.data.imported, 0);
  assert.equal(repeated.data.skipped, 1);
  assert.equal(repeated.data.builds.find((value) => value.id === 'build-a').name, 'City commuter');
  const invalid = await api.request('/api/builds/import', {
    method: 'POST',
    cookie,
    body: {
      builds: [build('build-c'), { ...build('build-d'), selected: { Motors: 'battery-a' } }],
    },
  });
  assert.equal(invalid.status, 422);
  assert.equal((await api.request('/api/builds', { cookie })).data.builds.length, 2);
});

test('real shared catalog, vehicle search, and legacy estimator run through HTTP', async (t) => {
  const [{ CATALOG, CATEGORIES }, { VEHICLE_INDEX, findVehicles }, { estimatePerformance }] =
    await Promise.all([
      import('@voltforge/shared/catalog'),
      import('@voltforge/shared/vehicles'),
      import('@voltforge/shared/performance'),
    ]);
  const api = await fixture(t, {
    catalog: CATALOG,
    categories: CATEGORIES,
    vehicleIndex: VEHICLE_INDEX,
    findVehicles,
    estimatePerformance,
  });
  assert.ok((await api.request('/api/catalog')).data.catalog.length >= 315);
  assert.equal((await api.request('/api/vehicles')).data.vehicles.length, VEHICLE_INDEX.length);
  const bikes = (await api.request('/api/vehicles?type=bike')).data.vehicles;
  assert.ok(bikes.length > 0 && bikes.every((vehicle) => vehicle.type === 'bike'));
  const search = await api.request('/api/vehicles?q=KuKirin%20G4&type=scooter');
  assert.equal(search.data.vehicles[0].name, 'KuKirin G4');
  const legacy = {
    ...build(),
    mode: 'rebuild',
    vehicle: 'KuKirin G4',
    selected: {},
    specs: { motorCount: 1 },
    performance: {},
  };
  const estimate = await api.request('/api/performance', {
    method: 'POST',
    body: { build: legacy },
  });
  assert.equal(estimate.status, 200);
  assert.equal(estimate.data.performance.speed.value, 70);
  assert.equal(estimate.data.performance.wh, 1200);
  assert.equal(estimate.data.performance.energyAtSpeed, undefined);
  const modified = await api.request('/api/performance', {
    method: 'POST',
    body: {
      build: {
        ...legacy,
        selected: { Controllers: 'p37' },
        specs: { motorCount: 1, motorCountOverride: 1 },
        performance: { schema: 2 },
      },
    },
  });
  assert.equal(modified.status, 200);
  assert.equal(modified.data.performance.wh, 1200);
  assert.equal(modified.data.performance.p.Batteries.stock, true);
  assert.equal(modified.data.performance.speed.kind, 'planning');
  assert.ok(modified.data.performance.peak.value > 0);

  const { cookie } = await api.request('/api/builds');
  const oldInputs = { schema: 1, rider: '85', rpm: '1200', oldSetting: 5 };
  const imported = await api.request('/api/builds/import', {
    method: 'POST',
    cookie,
    body: { builds: [{ ...legacy, performance: oldInputs }] },
  });
  assert.equal(imported.status, 200);
  assert.deepEqual(imported.data.builds[0].performance, oldInputs);
  const recalculated = await api.request('/api/performance', {
    method: 'POST',
    body: { build: imported.data.builds[0] },
  });
  assert.equal(recalculated.status, 200);
  assert.equal(recalculated.data.performance.a.schema, 2);
  assert.equal(recalculated.data.performance.a.rider, '85');
});

test('validation rejects invalid types, part category mismatches, and nonfinite numeric fields', async (t) => {
  const api = await fixture(t);
  const invalidBuilds = [
    { ...build(), selected: { Unknown: 'motor-a' } },
    { ...build(), selected: { Motors: 'battery-a' } },
    { ...build(), selected: { Motors: 'missing' } },
    { ...build(), type: 'car' },
    { ...build(), mode: 'replace' },
    { ...build(), name: 'a'.repeat(151) },
    { ...build(), specs: { fullV: 'Infinity' } },
    { ...build(), specs: { motorCount: 3 } },
    { ...build(), specs: { motorCountOverride: 3 } },
    { ...build(), performance: { schema: 2, rider: null } },
    { ...build(), performance: { schema: 2, rider: 'NaN' } },
    { ...build(), performance: { schema: 3 } },
    { ...build(), performance: { schema: 2, configuration: 'untrusted' } },
    { ...build(), performance: { schema: 2, script: 'alert(1)' } },
    { ...build(), updated: -1 },
  ];
  for (const value of invalidBuilds) {
    const response = await api.request('/api/builds/build-a', {
      method: 'PUT',
      body: { build: value },
    });
    assert.equal(response.status, 422, JSON.stringify(value));
    assert.equal(response.data.error.code, 'INVALID_BUILD');
  }
  assert.equal(
    (await api.request('/api/builds/other', { method: 'PUT', body: { build: build() } })).status,
    422,
  );
  assert.deepEqual((await api.request('/api/builds')).data.builds, []);
});

test('HTTP boundary rejects malformed, oversized, and cross-origin writes', async (t) => {
  const api = await fixture(t);
  assert.equal((await api.request('/api/performance', { method: 'POST', raw: '{' })).status, 400);
  assert.equal((await api.request('/api/performance', { method: 'POST', raw: '[]' })).status, 400);
  assert.equal(
    (
      await api.request('/api/performance', {
        method: 'POST',
        raw: '{}',
        headers: { 'Content-Type': 'text/plain' },
      })
    ).status,
    415,
  );
  const oversized = await api.request('/api/performance', {
    method: 'POST',
    raw: JSON.stringify({ padding: 'x'.repeat(1024 * 1024) }),
  });
  assert.equal(oversized.status, 413);
  const foreign = await api.request('/api/builds/build-a', {
    method: 'PUT',
    body: { build: build() },
    headers: { Origin: 'https://unrelated.invalid' },
  });
  assert.equal(foreign.status, 403);
  assert.equal(foreign.headers.get('access-control-allow-origin'), null);
  assert.equal(
    (
      await api.request('/api/builds/build-a', {
        method: 'DELETE',
        headers: { 'Sec-Fetch-Site': 'cross-site' },
      })
    ).status,
    403,
  );
  const preflight = await api.request('/api/builds/build-a', {
    method: 'OPTIONS',
    headers: { Origin: 'http://localhost:5173' },
  });
  assert.equal(preflight.status, 204);
  assert.equal(preflight.headers.get('access-control-allow-origin'), 'http://localhost:5173');
  const local = await api.request('/api/builds/build-a', {
    method: 'PUT',
    body: { build: build() },
    headers: { Origin: 'http://127.0.0.1:5173' },
  });
  assert.equal(local.status, 201);
  assert.equal(local.headers.get('access-control-allow-origin'), 'http://127.0.0.1:5173');
  assert.equal((await api.request('/api/health')).status, 200);
});

test('HTTPS deployment config issues secure cookies and only echoes an allowed origin', async (t) => {
  const api = await fixture(t, { appOrigin: 'https://voltforge.example' });
  const response = await api.request('/api/builds', {
    headers: { Origin: 'https://voltforge.example' },
  });
  assert.match(response.headers.get('set-cookie'), /; Secure$/);
  assert.equal(response.headers.get('access-control-allow-origin'), 'https://voltforge.example');
});

test('production static files support SPA routes and prevent traversal, dotfile, and symlink reads', async (t) => {
  const directory = await mkdtemp(join(tmpdir(), 'voltforge-static-'));
  t.after(() => rm(directory, { recursive: true, force: true }));
  const webDist = join(directory, 'dist');
  await mkdir(join(webDist, 'assets'), { recursive: true });
  await writeFile(join(webDist, 'index.html'), '<html>Voltforge</html>');
  await writeFile(join(webDist, 'assets', 'app.js'), 'console.log("Voltforge")');
  await writeFile(join(directory, 'secret.txt'), 'private');
  await writeFile(join(webDist, '.secret'), 'private');
  await symlink(join(directory, 'secret.txt'), join(webDist, 'secret.txt'));
  const api = await fixture(t, { webDist });
  const root = await api.request('/');
  assert.equal(root.status, 200);
  assert.match(root.data, /Voltforge/);
  assert.equal((await api.request('/planner/build-a')).status, 200);
  const asset = await api.request('/assets/app.js');
  assert.equal(asset.status, 200);
  assert.match(asset.headers.get('content-type'), /javascript/);
  assert.equal((await api.request('/assets/app.js', { method: 'HEAD' })).status, 200);
  assert.equal((await api.request('/missing.js')).status, 404);
  assert.equal((await api.request('/.secret')).status, 404);
  assert.equal((await api.request('/%2e%2e%2fsecret.txt')).status, 404);
  assert.equal((await api.request('/secret.txt')).status, 404);
  assert.equal((await api.request('/api/missing')).data.error.code, 'NOT_FOUND');
});

test('configuration validates network boundaries and resolves durable paths from the project', () => {
  const config = readConfig({});
  assert.equal(config.host, '127.0.0.1');
  assert.equal(config.port, 3001);
  assert.equal(config.databasePath, join(PROJECT_ROOT, 'data/voltforge.sqlite'));
  assert.throws(() => readConfig({ PORT: 'not-a-port' }), /PORT/);
  assert.throws(() => readConfig({ APP_ORIGIN: 'https://example.com/path' }), /APP_ORIGIN/);
  assert.equal(readConfig({ APP_ORIGIN: 'https://example.com/' }).appOrigin, 'https://example.com');
});
