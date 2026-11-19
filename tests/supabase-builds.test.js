import assert from 'node:assert/strict';
import test from 'node:test';
import { RevisionConflict } from '../apps/api/src/repository.js';
import { createSupabaseBuildRepository } from '../apps/api/src/supabase-builds.js';

const projectUrl = 'https://voltmodd.supabase.invalid';
const publishableKey = 'test-publishable-key';
const accessToken = 'test-user-access-token';
const build = { id: 'g4-build', name: 'KuKirin G4' };

function repository(fetcher) {
  return createSupabaseBuildRepository({
    url: projectUrl,
    key: publishableKey,
    fetcher,
  });
}

test('hosted build storage forwards the authenticated user token and preserves the API results', async () => {
  const saved = { ...build, updated: 1, revision: 1 };
  const exchanges = [
    ['list_builds', {}, [saved]],
    ['save_build', { p_build: build, p_expected_revision: 0 }, { build: saved, created: true }],
    ['import_builds', { p_builds: [build] }, { builds: [saved], imported: 0, skipped: 1 }],
    ['delete_build', { p_id: build.id }, false],
  ];
  let requests = 0;
  const storage = repository(async (url, options) => {
    const [rpc, parameters, data] = exchanges[requests++];
    assert.equal(String(url), projectUrl + '/rest/v1/rpc/voltmodd_' + rpc);
    assert.equal(options.method, 'POST');
    assert.equal(options.redirect, 'error');
    assert.deepEqual(options.headers, {
      apikey: publishableKey,
      Authorization: 'Bearer ' + accessToken,
      'Content-Type': 'application/json',
    });
    assert.deepEqual(JSON.parse(options.body), parameters);
    return Response.json(data);
  });

  assert.deepEqual(await storage.listBuilds(accessToken), exchanges[0][2]);
  assert.deepEqual(await storage.saveBuild(accessToken, build, 0), exchanges[1][2]);
  assert.deepEqual(await storage.importBuilds(accessToken, [build]), exchanges[2][2]);
  assert.equal(await storage.deleteBuild(accessToken, build.id), false);
  assert.equal(requests, exchanges.length);
});

test('hosted saves preserve zero-valued and non-zero revision conflicts', async () => {
  for (const currentRevision of [0, 2]) {
    const storage = repository(async () => Response.json({ conflict: currentRevision }));
    await assert.rejects(
      storage.saveBuild(accessToken, build, 1),
      (error) => error instanceof RevisionConflict && error.currentRevision === currentRevision,
    );
  }
});

test('hosted storage rejects missing authentication and sanitizes upstream errors', async () => {
  const storage = repository(async () =>
    assert.fail('A missing user token must never reach Supabase'),
  );
  await assert.rejects(storage.listBuilds(), { status: 401, code: 'AUTH_REQUIRED' });

  for (const [status, code, expectedStatus] of [
    [401, 'AUTH_REQUIRED', 401],
    [403, 'BUILD_ACCESS_DENIED', 403],
    [500, 'BUILD_STORAGE_UNAVAILABLE', 503],
  ]) {
    const failing = repository(async () =>
      Response.json({ message: 'upstream details' }, { status }),
    );
    await assert.rejects(
      failing.listBuilds(accessToken),
      (error) =>
        error.status === expectedStatus &&
        error.code === code &&
        !error.message.includes('upstream details'),
    );
  }

  const offline = repository(async () => {
    throw new Error('upstream details');
  });
  await assert.rejects(offline.listBuilds(accessToken), {
    status: 503,
    code: 'BUILD_STORAGE_UNAVAILABLE',
  });
});
