import { createHash, randomBytes } from 'node:crypto';
import { HttpError, readJson, sendJson } from './http.js';

const ACCESS = 'voltmodd_access';
const REFRESH = 'voltmodd_refresh';
const RECOVERY = 'voltmodd_recovery';
const FLOW_COOKIE = { confirm: 'voltmodd_confirm_flow', reset: 'voltmodd_reset_flow' };
const TOKEN = /^[A-Za-z0-9._~-]{1,3800}$/;
const WEEK = 60 * 60 * 24 * 7;

function readCookie(request, name) {
  for (const entry of (request.headers.cookie || '').split(';')) {
    const at = entry.indexOf('=');
    if (at < 0 || entry.slice(0, at).trim() !== name) continue;
    const value = entry.slice(at + 1).trim();
    if (TOKEN.test(value)) return value;
  }
}

function emailInput(value) {
  const email = typeof value === 'string' ? value.trim().toLowerCase() : '';
  if (email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
    throw new HttpError(422, 'INVALID_EMAIL', 'Enter a valid email address.');
  return email;
}

function passwordInput(value, minimum = 12) {
  if (typeof value !== 'string' || value.length < minimum || Buffer.byteLength(value) > 72) {
    throw new HttpError(
      422,
      'INVALID_PASSWORD',
      minimum > 1
        ? 'Use a password of at least 12 characters and at most 72 bytes.'
        : 'Enter your password.',
    );
  }
  return value;
}

function account(value) {
  if (!value?.id || !value?.email)
    throw new HttpError(
      502,
      'AUTH_RESPONSE_INVALID',
      'The sign-in service returned an invalid account.',
    );
  return { id: value.id, email: value.email };
}

function authError(status, code, fallback) {
  if (status === 429 || code === 'over_email_send_rate_limit')
    return new HttpError(429, 'AUTH_RATE_LIMIT', 'Too many requests. Try again in a few minutes.');
  if (code === 'email_not_confirmed')
    return new HttpError(403, 'EMAIL_UNCONFIRMED', 'Confirm your email before logging in.');
  if (code === 'weak_password')
    return new HttpError(422, 'INVALID_PASSWORD', 'Choose a stronger password.');
  if (code === 'same_password')
    return new HttpError(
      422,
      'INVALID_PASSWORD',
      'Choose a password you have not used for this account.',
    );
  if (status >= 500 || code === 'email_address_not_authorized')
    return new HttpError(
      503,
      'AUTH_UNAVAILABLE',
      'The account service is temporarily unavailable.',
    );
  return fallback;
}

export function createHostedAuth({ url, key, appOrigin, fetcher = fetch }) {
  const secure = appOrigin.startsWith('https:') ? '; Secure' : '';
  function cookie(response, name, value, maxAge) {
    if (value && !TOKEN.test(value))
      throw new HttpError(
        502,
        'AUTH_RESPONSE_INVALID',
        'The sign-in service returned an invalid session.',
      );
    response.appendHeader(
      'Set-Cookie',
      `${name}=${value}; Path=/api; HttpOnly; SameSite=Lax; Max-Age=${maxAge}${secure}`,
    );
  }

  function clearSession(response) {
    cookie(response, ACCESS, '', 0);
    cookie(response, REFRESH, '', 0);
  }

  async function authRequest(path, { method = 'POST', body, accessToken } = {}) {
    let response;
    try {
      response = await fetcher(`${url}/auth/v1${path}`, {
        method,
        redirect: 'error',
        signal: AbortSignal.timeout(6500),
        headers: {
          apikey: key,
          ...(accessToken && { Authorization: `Bearer ${accessToken}` }),
          ...(body && { 'Content-Type': 'application/json' }),
        },
        body: body && JSON.stringify(body),
      });
    } catch {
      throw new HttpError(
        503,
        'AUTH_UNAVAILABLE',
        'The account service is temporarily unavailable.',
      );
    }
    const data = await response.json().catch(() => null);
    return { ok: response.ok, status: response.status, data };
  }

  function writeSession(response, data) {
    const user = account(data?.user);
    const ttl = Math.max(0, Math.min(3600, Math.floor(Number(data.expires_in) || 0) - 15));
    if (!TOKEN.test(data.access_token || '') || !TOKEN.test(data.refresh_token || '') || !ttl)
      throw new HttpError(
        502,
        'AUTH_RESPONSE_INVALID',
        'The sign-in service returned an invalid session.',
      );
    cookie(response, ACCESS, data.access_token, ttl);
    cookie(response, REFRESH, data.refresh_token, WEEK);
    return { user, accessToken: data.access_token };
  }

  async function session(request, response, expectedAccount) {
    const accessToken = readCookie(request, ACCESS);
    if (accessToken) {
      const result = await authRequest('/user', { method: 'GET', accessToken });
      if (result.ok) return { user: account(result.data), accessToken };
      if (result.status >= 500 || result.status === 429)
        throw authError(result.status, result.data?.code);
    }
    const refreshToken = readCookie(request, REFRESH);
    if (!refreshToken) return null;
    const result = await authRequest('/token?grant_type=refresh_token', {
      body: { refresh_token: refreshToken },
    });
    if (result.ok) {
      const user = account(result.data?.user);
      // A tab belonging to a previous account may never issue matching-session cookies.
      if (expectedAccount && user.id !== expectedAccount) return { user };
      return writeSession(response, result.data);
    }
    if (result.status >= 500 || result.status === 429)
      throw authError(result.status, result.data?.code);
    clearSession(response);
    return null;
  }

  function startFlow(flow) {
    const verifier = randomBytes(32).toString('base64url');
    const redirect = new URL(`/api/auth/callback/${flow}`, appOrigin);
    return {
      verifier,
      redirect: new URLSearchParams({ redirect_to: redirect.toString() }),
      challenge: {
        code_challenge: createHash('sha256').update(verifier).digest('base64url'),
        code_challenge_method: 's256',
      },
    };
  }

  async function signIn(response, email, password) {
    const result = await authRequest('/token?grant_type=password', { body: { email, password } });
    if (!result.ok)
      throw authError(
        result.status,
        result.data?.code,
        new HttpError(401, 'INVALID_CREDENTIALS', 'Check your email and password.'),
      );
    cookie(response, RECOVERY, '', 0);
    return writeSession(response, result.data).user;
  }

  async function callback(request, response, url, flow) {
    const verifier = readCookie(request, FLOW_COOKIE[flow]);
    const code = url.searchParams.get('code');
    cookie(response, FLOW_COOKIE[flow], '', 0);
    let outcome = 'error';
    if (verifier && code && TOKEN.test(code)) {
      try {
        const result = await authRequest('/token?grant_type=pkce', {
          body: { auth_code: code, code_verifier: verifier },
        });
        if (result.ok && flow === 'reset' && TOKEN.test(result.data?.access_token || '')) {
          clearSession(response);
          cookie(response, RECOVERY, result.data.access_token, 600);
          outcome = 'reset';
        } else if (result.ok && flow === 'confirm') {
          cookie(response, RECOVERY, '', 0);
          writeSession(response, result.data);
          outcome = 'confirmed';
        }
      } catch (error) {
        if (!(error instanceof HttpError)) throw error;
      }
    }
    response.writeHead(303, { Location: `/?auth=${outcome}`, 'Cache-Control': 'no-store' });
    response.end();
  }

  async function route(request, response, url, requireMethod) {
    switch (url.pathname) {
      case '/api/auth/session': {
        requireMethod(request, response, ['GET']);
        const recovering = Boolean(readCookie(request, RECOVERY));
        const active = recovering ? null : await session(request, response);
        return sendJson(response, 200, { enabled: true, user: active?.user || null, recovering });
      }
      case '/api/auth/signup': {
        requireMethod(request, response, ['POST']);
        const body = await readJson(request, 8192);
        const email = emailInput(body.email);
        const password = passwordInput(body.password);
        const { verifier, redirect, challenge } = startFlow('confirm');
        const result = await authRequest(`/signup?${redirect}`, {
          body: { email, password, ...challenge },
        });
        if (!result.ok)
          throw authError(
            result.status,
            result.data?.code,
            new HttpError(
              422,
              'SIGN_UP_FAILED',
              'Could not create the account. Check your details and try again.',
            ),
          );
        const user = result.data?.access_token ? writeSession(response, result.data).user : null;
        if (!user) cookie(response, FLOW_COOKIE.confirm, verifier, 3600);
        return sendJson(response, 200, { user, confirmationRequired: !user });
      }
      case '/api/auth/login': {
        requireMethod(request, response, ['POST']);
        const body = await readJson(request, 8192);
        const user = await signIn(
          response,
          emailInput(body.email),
          passwordInput(body.password, 1),
        );
        return sendJson(response, 200, { user });
      }
      case '/api/auth/logout': {
        requireMethod(request, response, ['POST']);
        try {
          const active = await session(request, response);
          if (active) await authRequest('/logout?scope=local', { accessToken: active.accessToken });
        } catch (error) {
          if (!(error instanceof HttpError)) throw error;
        } finally {
          clearSession(response);
          cookie(response, RECOVERY, '', 0);
          for (const name of Object.values(FLOW_COOKIE)) cookie(response, name, '', 0);
        }
        return sendJson(response, 200, { user: null });
      }
      case '/api/auth/reset': {
        requireMethod(request, response, ['POST']);
        const { email: input } = await readJson(request, 8192);
        const email = emailInput(input);
        const { verifier, redirect, challenge } = startFlow('reset');
        const result = await authRequest(`/recover?${redirect}`, { body: { email, ...challenge } });
        if (
          !result.ok &&
          (result.status >= 500 ||
            result.status === 429 ||
            result.data?.code === 'email_address_not_authorized')
        )
          throw authError(result.status, result.data?.code);
        if (result.ok) cookie(response, FLOW_COOKIE.reset, verifier, 3600);
        return sendJson(response, 200, { ok: true });
      }
      case '/api/auth/password': {
        requireMethod(request, response, ['POST']);
        const recoveryToken = readCookie(request, RECOVERY);
        if (!recoveryToken)
          throw new HttpError(401, 'RESET_EXPIRED', 'Request a fresh password reset link.');
        const { password } = await readJson(request, 8192);
        const newPassword = passwordInput(password);
        const result = await authRequest('/user', {
          method: 'PUT',
          accessToken: recoveryToken,
          body: { password: newPassword },
        });
        if (!result.ok)
          throw authError(
            result.status,
            result.data?.code,
            new HttpError(401, 'RESET_EXPIRED', 'Request a fresh password reset link.'),
          );
        const user = await signIn(response, account(result.data).email, newPassword);
        return sendJson(response, 200, { user });
      }
      case '/api/auth/callback/confirm':
      case '/api/auth/callback/reset':
        requireMethod(request, response, ['GET']);
        return callback(request, response, url, url.pathname.split('/').at(-1));
      default:
        throw new HttpError(404, 'NOT_FOUND', 'The API endpoint does not exist.');
    }
  }

  return { session, route };
}
