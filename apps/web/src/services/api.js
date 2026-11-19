export class ApiError extends Error {
  constructor(message, status, code) {
    super(message);
    this.status = status;
    this.code = code;
  }
}
export function createApiClient(fetcher = globalThis.fetch, { accountId } = {}) {
  async function request(path, options = {}) {
    const response = await fetcher('/api' + path, {
      credentials: 'same-origin',
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(accountId && path.startsWith('/builds') && { 'X-Voltmodd-Account': accountId }),
        ...options.headers,
      },
      signal: options.signal || AbortSignal.timeout(8000),
    });
    let payload;
    try {
      payload = await response.json();
    } catch {
      throw new ApiError(
        'The server returned an unreadable response.',
        response.status,
        'BAD_RESPONSE',
      );
    }
    if (!response.ok)
      throw new ApiError(
        payload.error?.message || 'The request failed.',
        response.status,
        payload.error?.code,
      );
    return payload;
  }
  const post = (path, body) => request(path, { method: 'POST', body: JSON.stringify(body) });
  const importBuildsWithResult = (builds) => post('/builds/import', { builds });
  return {
    listBuilds: async () => (await request('/builds')).builds,
    importBuilds: async (builds) => (await importBuildsWithResult(builds)).builds,
    importBuildsWithResult,
    saveBuild: async (build, expectedRevision = 0) =>
      (
        await request('/builds/' + encodeURIComponent(build.id), {
          method: 'PUT',
          body: JSON.stringify({ build, expectedRevision }),
        })
      ).build,
    deleteBuild: (id) => request('/builds/' + encodeURIComponent(id), { method: 'DELETE' }),
    estimate: async (build) =>
      (await request('/performance', { method: 'POST', body: JSON.stringify({ build }) }))
        .performance,
    accountSession: () => request('/auth/session'),
    signUp: (email, password) => post('/auth/signup', { email, password }),
    logIn: (email, password) => post('/auth/login', { email, password }),
    logOut: () => post('/auth/logout', {}),
    resetPassword: (email) => post('/auth/reset', { email }),
    setPassword: (password) => post('/auth/password', { password }),
  };
}
