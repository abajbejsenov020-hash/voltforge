import test from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { once } from 'node:events';
import { BuildStore } from '../apps/web/src/state/build-store.js';
import { createApiClient } from '../apps/web/src/services/api.js';
import { createApp } from '../apps/api/src/app.js';

const KEY = 'voltforge-v1';
const SYNC = 'voltforge-sync-v1';
const build = (id = 'x', changes = {}) => ({
  id,
  name: 'Original',
  type: 'scooter',
  mode: 'new',
  vehicle: '',
  selected: {},
  specs: { dropout: '', fullV: '', bms: '', batteryLimit: '', motorCount: 1 },
  performance: { schema: 2 },
  updated: 100,
  revision: 1,
  ...changes,
});

function storage(builds = [build()], sync = { revisions: { x: 1 }, pending: [] }) {
  const data = new Map([
    [KEY, JSON.stringify({ active: builds[0]?.id, builds })],
    [SYNC, JSON.stringify(sync)],
  ]);
  return {
    get length() {
      return data.size;
    },
    key(index) {
      return [...data.keys()][index] ?? null;
    },
    getItem(key) {
      return data.get(key) ?? null;
    },
    setItem(key, value) {
      if (this.failKey === key) throw new Error('Quota exceeded');
      data.set(key, value);
    },
    data,
  };
}

function deferred() {
  let resolve;
  const promise = new Promise((done) => {
    resolve = done;
  });
  return { promise, resolve };
}

async function settle(store) {
  for (let attempt = 0; attempt < 30; attempt++) {
    const work = [store.initializing, store.flushing].filter(Boolean);
    if (!work.length) return;
    await Promise.all(work);
  }
  assert.fail('Autosave did not settle.');
}

test('a stale tab persist preserves a newer offline build and edits to other builds', () => {
  const disk = storage();
  const first = new BuildStore({ storage: disk });
  const second = new BuildStore({ storage: disk });
  second.current = build('z', { name: 'New offline build', revision: 0 });
  second.save();
  first.persist();
  assert.deepEqual(
    new Set(JSON.parse(disk.getItem(KEY)).builds.map((value) => value.id)),
    new Set(['x', 'z']),
  );
  first.current.name = 'Edited first build';
  first.save();
  second.persist();
  const saved = JSON.parse(disk.getItem(KEY)).builds;
  assert.equal(saved.find((value) => value.id === 'x').name, 'Edited first build');
  assert.equal(saved.find((value) => value.id === 'z').name, 'New offline build');
});

test('equal timestamps never erase pending content that differs from a newer server revision', async () => {
  const disk = storage([build('x', { name: 'Local edit' })], {
    revisions: { x: 1 },
    pending: ['x'],
  });
  const store = new BuildStore({
    storage: disk,
    api: { listBuilds: async () => [build('x', { name: 'Different remote edit', revision: 2 })] },
  });
  await store.initialize();
  assert.equal(store.current.name, 'Local edit');
  assert.ok(store.pending.has('x'));
  assert.ok(store.conflicts.has('x'));
});

test('the next edit retries a transient save failure and sends the newest contents', async () => {
  let remote = build();
  let calls = 0;
  const store = new BuildStore({
    storage: storage(),
    api: {
      listBuilds: async () => [structuredClone(remote)],
      saveBuild: async (value, revision) => {
        calls++;
        if (calls === 1) throw new Error('Temporary outage');
        assert.equal(revision, remote.revision);
        remote = { ...value, revision: revision + 1 };
        return structuredClone(remote);
      },
    },
  });
  await store.initialize();
  store.current.name = 'First edit';
  store.save();
  await settle(store);
  store.current.name = 'Newest edit';
  store.save();
  await settle(store);
  assert.equal(calls, 2);
  assert.equal(remote.name, 'Newest edit');
  assert.equal(store.pending.size, 0);
  assert.equal(store.ready, true);
});

test('a lost commit response reconciles identical contents before the next edit', async () => {
  let remote = build();
  let calls = 0;
  const store = new BuildStore({
    storage: storage(),
    api: {
      listBuilds: async () => [structuredClone(remote)],
      saveBuild: async (value, revision) => {
        calls++;
        assert.equal(revision, remote.revision);
        remote = { ...value, updated: value.updated + 100, revision: revision + 1 };
        if (calls === 1) throw new Error('Response lost after commit');
        return structuredClone(remote);
      },
    },
  });
  await store.initialize();
  store.current.name = 'Committed edit';
  store.save();
  await settle(store);
  await store.initialize();
  assert.equal(store.conflicts.size, 0);
  assert.equal(store.pending.size, 0);
  assert.equal(store.revisions.x, 2);
  store.current.name = 'Next edit';
  store.save();
  await settle(store);
  assert.equal(calls, 2);
  assert.equal(remote.name, 'Next edit');
});

test('a conflict for one build does not block independent pending builds', async () => {
  const local = build('x', { name: 'Local edit', updated: 200 });
  const fresh = build('z', { revision: 0 });
  const calls = [];
  const store = new BuildStore({
    storage: storage([local, fresh], { revisions: { x: 1 }, pending: ['x', 'z'] }),
    api: {
      listBuilds: async () => [build('x', { name: 'Server edit', revision: 2, updated: 300 })],
      saveBuild: async (value, revision) => {
        calls.push({ id: value.id, revision });
        return { ...value, revision: 1 };
      },
    },
  });
  await store.initialize();
  await settle(store);
  assert.ok(store.conflicts.has('x'));
  assert.deepEqual(calls, [{ id: 'z', revision: 0 }]);
  assert.ok(!store.pending.has('z'));
});

test('serialized autosave keeps the newest edit while the first request is in flight', async () => {
  let remote = build();
  let active = 0;
  let maxActive = 0;
  const gate = deferred();
  const calls = [];
  const store = new BuildStore({
    storage: storage(),
    api: {
      listBuilds: async () => [structuredClone(remote)],
      saveBuild: async (value, revision) => {
        active++;
        maxActive = Math.max(maxActive, active);
        calls.push({ name: value.name, revision });
        if (calls.length === 1) await gate.promise;
        assert.equal(revision, remote.revision);
        remote = { ...value, revision: revision + 1 };
        active--;
        return structuredClone(remote);
      },
    },
  });
  await store.initialize();
  store.current.name = 'First edit';
  store.save();
  store.current.name = 'Latest edit';
  store.save();
  gate.resolve();
  await settle(store);
  assert.equal(maxActive, 1);
  assert.deepEqual(calls, [
    { name: 'First edit', revision: 1 },
    { name: 'Latest edit', revision: 2 },
  ]);
  assert.equal(remote.name, 'Latest edit');
  assert.equal(store.pending.size, 0);
});

test('a partial legacy metadata write cannot mark an unsynced edit clean after reload', async () => {
  const disk = storage();
  let remote = build();
  let failSave = true;
  const api = {
    listBuilds: async () => [structuredClone(remote)],
    saveBuild: async (value, revision) => {
      if (failSave) throw new Error('Offline');
      remote = { ...value, revision: revision + 1 };
      return structuredClone(remote);
    },
  };
  const first = new BuildStore({ storage: disk, api });
  await first.initialize();
  disk.failKey = SYNC;
  first.current.name = 'Recoverable local edit';
  first.save();
  await settle(first);
  disk.failKey = undefined;
  failSave = false;
  const reloaded = new BuildStore({ storage: disk, api });
  await reloaded.initialize();
  await settle(reloaded);
  assert.equal(reloaded.current.name, 'Recoverable local edit');
  assert.equal(remote.name, 'Recoverable local edit');
});

test('stale edits to the same build remain available as a named local copy', () => {
  const disk = storage();
  const first = new BuildStore({ storage: disk });
  first.current.name = 'First edit';
  first.save();
  const second = new BuildStore({ storage: disk });
  second.current.name = 'Second edit';
  second.save();
  first.refreshFromStorage();
  const reloaded = new BuildStore({ storage: disk });
  assert.equal(reloaded.builds.length, 2);
  assert.ok(reloaded.builds.some((value) => value.name === 'Second edit'));
  assert.ok(reloaded.builds.some((value) => value.name === 'First edit (local copy)'));
  assert.notEqual(first.current.id, 'x');
  assert.equal(first.current.name, 'First edit (local copy)');
  second.refreshFromStorage();
  first.refreshFromStorage();
  assert.equal(new BuildStore({ storage: disk }).builds.length, 2);
});

test('individual records recover even when the legacy snapshot is missing or malformed', () => {
  const disk = storage();
  const first = new BuildStore({ storage: disk });
  first.current = build('z', { name: 'Recoverable record', revision: 0 });
  first.save();
  disk.setItem(KEY, '{');
  const reloaded = new BuildStore({ storage: disk });
  assert.equal(reloaded.builds.length, 2);
  assert.ok(reloaded.builds.some((value) => value.name === 'Recoverable record'));
  assert.ok(reloaded.pending.has('z'));
});

test('an edit during an unsuccessful request triggers one recovery attempt', async () => {
  let remote = build();
  let calls = 0;
  const gate = deferred();
  const store = new BuildStore({
    storage: storage(),
    api: {
      listBuilds: async () => [structuredClone(remote)],
      saveBuild: async (value, revision) => {
        calls++;
        if (calls === 1) {
          await gate.promise;
          throw new Error('Temporary outage');
        }
        remote = { ...value, revision: revision + 1 };
        return structuredClone(remote);
      },
    },
  });
  await store.initialize();
  store.current.name = 'First edit';
  store.save();
  store.current.name = 'Latest edit';
  store.save();
  gate.resolve();
  await settle(store);
  assert.equal(calls, 2);
  assert.equal(remote.name, 'Latest edit');
  assert.equal(store.pending.size, 0);
});

test('the next edit can recover an unacknowledged commit without an explicit reconnect', async () => {
  let remote = build();
  let calls = 0;
  const store = new BuildStore({
    storage: storage(),
    api: {
      listBuilds: async () => [structuredClone(remote)],
      saveBuild: async (value, revision) => {
        calls++;
        assert.equal(revision, remote.revision);
        remote = { ...value, revision: revision + 1 };
        if (calls === 1) throw new Error('Lost response after commit');
        return structuredClone(remote);
      },
    },
  });
  await store.initialize();
  store.current.name = 'Committed edit';
  store.save();
  await settle(store);
  store.current.name = 'Next edit';
  store.save();
  await settle(store);
  assert.equal(calls, 2);
  assert.equal(remote.name, 'Next edit');
  assert.equal(store.conflicts.size, 0);
});

test('overlapping reconnects serialize and do not erase an edit made while loading', async () => {
  const gate = deferred();
  let lists = 0;
  let saved;
  const store = new BuildStore({
    storage: storage(),
    api: {
      listBuilds: async () => {
        lists++;
        return gate.promise;
      },
      saveBuild: async (value, revision) => {
        saved = { ...value, revision: revision + 1 };
        return saved;
      },
    },
  });
  const first = store.initialize();
  assert.equal(store.initialize(), first);
  store.current.name = 'Edited while loading';
  store.save();
  gate.resolve([build()]);
  await first;
  await settle(store);
  assert.equal(lists, 1);
  assert.equal(saved.name, 'Edited while loading');
  assert.equal(store.pending.size, 0);
});

test('a 409 with identical committed contents does not create a false conflict', async () => {
  let remote = build();
  let calls = 0;
  const store = new BuildStore({
    storage: storage(),
    api: {
      listBuilds: async () => [structuredClone(remote)],
      saveBuild: async (value, revision) => {
        calls++;
        remote = { ...value, revision: revision + 1 };
        throw Object.assign(new Error('Already committed'), { status: 409 });
      },
    },
  });
  await store.initialize();
  store.current.name = 'Identical concurrent edit';
  store.save();
  await settle(store);
  assert.equal(calls, 1);
  assert.equal(store.revisions.x, 2);
  assert.equal(store.pending.size, 0);
  assert.equal(store.conflicts.size, 0);
});

test('the real API client and SQLite API recover a lost commit response then save the next edit', async (t) => {
  const app = createApp();
  const server = createServer(app.handler);
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  t.after(async () => {
    await new Promise((resolve, reject) =>
      server.close((error) => (error ? reject(error) : resolve())),
    );
    app.close();
  });
  const base = `http://127.0.0.1:${server.address().port}`;
  let cookie;
  let loseResponse = true;
  const api = createApiClient(async (path, options) => {
    const response = await fetch(base + path, {
      ...options,
      headers: { ...options.headers, ...(cookie && { Cookie: cookie }) },
    });
    cookie = response.headers.get('set-cookie')?.split(';')[0] || cookie;
    if (options.method === 'PUT' && loseResponse) {
      loseResponse = false;
      await response.arrayBuffer();
      throw new Error('Committed response lost in transit');
    }
    return response;
  });
  const disk = storage();
  const store = new BuildStore({ storage: disk, api });
  await store.initialize();
  store.current.name = 'Committed through HTTP';
  store.save();
  await settle(store);
  assert.equal(store.ready, false);
  store.current.name = 'Next HTTP edit';
  store.save();
  await settle(store);
  assert.equal(store.conflicts.size, 0);
  assert.equal(store.pending.size, 0);
  assert.equal(store.revisions.x, 3);
  const remote = await api.listBuilds();
  assert.equal(remote[0].name, 'Next HTTP edit');
  const reloaded = new BuildStore({ storage: disk, api });
  await reloaded.initialize();
  assert.equal(reloaded.current.name, 'Next HTTP edit');
  assert.equal(reloaded.pending.size, 0);
});

test('an edit during a failing reconnect autosave retries after that reconnect settles', async () => {
  let remote = build();
  let calls = 0;
  const entered = deferred();
  const gate = deferred();
  const store = new BuildStore({
    storage: storage([build('x', { name: 'Offline edit' })], {
      revisions: { x: 1 },
      pending: ['x'],
    }),
    api: {
      listBuilds: async () => [structuredClone(remote)],
      saveBuild: async (value, revision) => {
        calls++;
        if (calls === 1) {
          entered.resolve();
          await gate.promise;
          throw new Error('Temporary outage');
        }
        remote = { ...value, revision: revision + 1 };
        return structuredClone(remote);
      },
    },
  });
  const reconnecting = store.initialize();
  await entered.promise;
  store.current.name = 'Latest edit during reconnect';
  store.save();
  gate.resolve();
  await reconnecting;
  await settle(store);
  assert.equal(calls, 2);
  assert.equal(remote.name, 'Latest edit during reconnect');
  assert.equal(store.pending.size, 0);
});

test('a denied localStorage getter still permits editing and exporting the in-memory build', () => {
  const original = Object.getOwnPropertyDescriptor(globalThis, 'localStorage');
  const statuses = [];
  Object.defineProperty(globalThis, 'localStorage', {
    configurable: true,
    get() {
      throw new Error('SecurityError');
    },
  });
  try {
    const store = new BuildStore({ onStatus: (status) => statuses.push(status) });
    store.current.name = 'In-memory edit';
    store.save();
    assert.equal(store.builds[0].name, 'In-memory edit');
    assert.equal(JSON.parse(JSON.stringify(store.current)).name, 'In-memory edit');
    assert.ok(statuses.some((status) => status.kind === 'error'));
    assert.ok(!statuses.some((status) => status.label === 'Saved on this device'));
  } finally {
    if (original) Object.defineProperty(globalThis, 'localStorage', original);
    else delete globalThis.localStorage;
  }
});
