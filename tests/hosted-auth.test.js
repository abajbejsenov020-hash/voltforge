import test from 'node:test';
import assert from 'node:assert/strict';
import { once } from 'node:events';
import { createHash } from 'node:crypto';
import { createServer } from 'node:http';
import { createBuild } from '@voltforge/shared/build';
import { createApp } from '../apps/api/src/app.js';

const origin = 'https://studio.example';
const users = {
  alice: { id: 'alice', email: 'alice@example.com' },
  bob: { id: 'bob', email: 'bob@example.com' },
};
const tokens = (user) => ({
  access_token: `access.${user.id}.token`,
  refresh_token: `refresh-${user.id}`,
  expires_in: 3600,
  user,
});
const cookies = (response) =>
  Object.fromEntries(
    response.headers.getSetCookie().map((cookie) => cookie.split(';')[0].split('=')),
  );
const cookieHeader = (values) =>
  Object.entries(values)
    .filter(([, value]) => value)
    .map(([name, value]) => `${name}=${value}`)
    .join('; ');

async function fixture(t) {
  const calls = [];
  const garages = new Map();
  const fetcher = (input, options) => {
    const url = new URL(input);
    assert.equal(url.origin, 'https://provider.example');
    assert.equal(options.headers.apikey, 'public_test_key');
    const body = options.body ? JSON.parse(options.body) : null;
    const token = options.headers.Authorization?.slice(7);
    const user = users[token?.split('.')[1]];
    calls.push({ path: url.pathname, query: url.searchParams, method: options.method, body, user });
    if (url.pathname === '/auth/v1/token') {
      const grant = url.searchParams.get('grant_type');
      if (grant === 'pkce') return Response.json(tokens(users.alice));
      if (grant === 'refresh_token') {
        const refreshed = users[body.refresh_token.replace('refresh-', '')];
        return refreshed ? Response.json(tokens(refreshed)) : Response.json({}, { status: 401 });
      }
      const signedIn = Object.values(users).find(({ email }) => email === body.email);
      return signedIn
        ? Response.json(tokens(signedIn))
        : Response.json({ code: 'invalid_credentials' }, { status: 400 });
    }
    if (url.pathname === '/auth/v1/user')
      return user ? Response.json(user) : Response.json({}, { status: 401 });
    if (url.pathname === '/auth/v1/signup' || url.pathname === '/auth/v1/recover')
      return Response.json({});
    if (url.pathname === '/auth/v1/logout') return new Response(null, { status: 204 });
    if (url.pathname === '/rest/v1/rpc/voltmodd_save_build' && user) {
      const build = { ...body.p_build, revision: 1 };
      garages.set(user.id, [build]);
      return Response.json({ created: true, build });
    }
    if (url.pathname === '/rest/v1/rpc/voltmodd_list_builds' && user)
      return Response.json(garages.get(user.id) || []);
    throw new Error('Unexpected provider call');
  };
  const app = createApp({
    appOrigin: origin,
    supabase: { url: 'https://provider.example', key: 'public_test_key', fetcher },
  });
  const server = createServer(app.handler).listen(0, '127.0.0.1');
  await once(server, 'listening');
  t.after(async () => {
    await new Promise((resolve) => server.close(resolve));
    app.close();
  });
  async function request(path, { method = 'GET', body, session, account, from = origin } = {}) {
    return fetch(`http://127.0.0.1:${server.address().port}/api${path}`, {
      method,
      redirect: 'manual',
      headers: {
        Origin: from,
        ...(body && { 'Content-Type': 'application/json' }),
        ...(session && { Cookie: cookieHeader(session) }),
        ...(account && { 'X-Voltmodd-Account': account }),
      },
      body: body && JSON.stringify(body),
    });
  }
  const login = (email) =>
    request('/auth/login', { method: 'POST', body: { email, password: 'example secret' } });
  return { request, login, calls };
}

test('hosted garage requests validate the signed-in account before accessing storage', async (t) => {
  const { request, login, calls } = await fixture(t);
  const loggedOut = await request('/auth/session');
  assert.deepEqual(await loggedOut.json(), { enabled: true, user: null, recovering: false });
  assert.equal((await request('/builds', { account: 'alice' })).status, 401);
  const alice = await login(' ALICE@example.com ');
  assert.deepEqual(await alice.json(), { user: users.alice });
  assert.ok(
    alice.headers
      .getSetCookie()
      .every((value) => /HttpOnly; SameSite=Lax; Max-Age=\d+; Secure/.test(value)),
  );
  const aliceSession = cookies(alice);
  const bobSession = cookies(await login('bob@example.com'));
  const build = createBuild('scooter', 'Private build');
  assert.equal(
    (
      await request('/builds/' + build.id, {
        method: 'PUT',
        body: { build, expectedRevision: 0 },
        session: aliceSession,
        account: 'alice',
      })
    ).status,
    201,
  );
  assert.deepEqual(
    (
      await (await request('/builds', { session: aliceSession, account: 'alice' })).json()
    ).builds.map(({ id }) => id),
    [build.id],
  );
  assert.deepEqual(
    await (await request('/builds', { session: bobSession, account: 'bob' })).json(),
    { builds: [] },
  );
  const rpcCount = calls.filter(({ path }) => path.startsWith('/rest/')).length;
  const wrong = await request('/builds', { session: bobSession, account: 'alice' });
  assert.equal(wrong.status, 409);
  assert.equal((await wrong.json()).error.code, 'ACCOUNT_CHANGED');
  assert.equal((await request('/builds', { session: aliceSession })).status, 401);
  const crossOrigin = await request('/auth/logout', {
    method: 'POST',
    session: aliceSession,
    from: 'http://localhost:5173',
  });
  assert.equal(crossOrigin.status, 403);
  assert.equal(calls.filter(({ path }) => path.startsWith('/rest/')).length, rpcCount);
  const refresh = await request('/auth/session', {
    session: { voltmodd_refresh: aliceSession.voltmodd_refresh },
  });
  assert.equal(cookies(refresh).voltmodd_access, 'access.alice.token');
  assert.deepEqual((await refresh.json()).user, users.alice);
  const logout = await request('/auth/logout', { method: 'POST', session: aliceSession });
  assert.equal(logout.status, 200);
  assert.equal(cookies(logout).voltmodd_access, '');
  assert.equal(cookies(logout).voltmodd_refresh, '');
  assert.equal(calls.at(-1).query.get('scope'), 'local');
});

test('confirmation and recovery exchange browser-bound codes and restrict the recovery session', async (t) => {
  const { request, calls } = await fixture(t);
  const signup = await request('/auth/signup', {
    method: 'POST',
    body: { email: users.alice.email, password: 'long signup secret' },
  });
  assert.deepEqual(await signup.json(), { confirmationRequired: true, user: null });
  const signupSession = cookies(signup);
  const signupCall = calls.at(-1);
  assert.equal(signupCall.query.get('redirect_to'), origin + '/api/auth/callback/confirm');
  assert.equal(
    signupCall.body.code_challenge,
    createHash('sha256').update(signupSession.voltmodd_confirm_flow).digest('base64url'),
  );
  const withoutVerifier = await request('/auth/callback/confirm?code=email-code');
  assert.equal(withoutVerifier.headers.get('location'), '/?auth=error');
  assert.equal(calls.at(-1), signupCall);
  const confirmed = await request('/auth/callback/confirm?code=email-code', {
    session: signupSession,
  });
  assert.equal(confirmed.headers.get('location'), '/?auth=confirmed');
  assert.equal(calls.at(-1).body.code_verifier, signupSession.voltmodd_confirm_flow);
  assert.equal(cookies(confirmed).voltmodd_access, 'access.alice.token');

  const reset = await request('/auth/reset', {
    method: 'POST',
    body: { email: users.alice.email },
  });
  assert.equal(calls.at(-1).query.get('redirect_to'), origin + '/api/auth/callback/reset');
  const callback = await request('/auth/callback/reset?code=recovery-code', {
    session: { ...cookies(confirmed), ...cookies(reset) },
  });
  assert.equal(callback.headers.get('location'), '/?auth=reset');
  const recovering = cookies(callback);
  assert.equal(recovering.voltmodd_access, '');
  assert.equal(recovering.voltmodd_refresh, '');
  assert.equal((await request('/builds', { session: recovering, account: 'alice' })).status, 401);
  const newPassword = { method: 'POST', body: { password: 'replacement secret' } };
  assert.equal(
    (await request('/auth/password', { ...newPassword, session: cookies(confirmed) })).status,
    401,
  );
  const changed = await request('/auth/password', { ...newPassword, session: recovering });
  assert.deepEqual(await changed.json(), { user: users.alice });
  assert.equal(cookies(changed).voltmodd_recovery, '');
  assert.equal(cookies(changed).voltmodd_access, 'access.alice.token');
});
