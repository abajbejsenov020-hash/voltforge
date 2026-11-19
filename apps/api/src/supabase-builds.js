import { HttpError } from './http.js';
import { RevisionConflict } from './repository.js';

const unavailable = () =>
  new HttpError(503, 'BUILD_STORAGE_UNAVAILABLE', 'Build storage is temporarily unavailable.');

export function createSupabaseBuildRepository({ url, key, fetcher = fetch }) {
  async function rpc(operation, accessToken, parameters = {}) {
    if (!accessToken) throw new HttpError(401, 'AUTH_REQUIRED', 'Log in to access your garage.');

    let response;
    try {
      response = await fetcher(new URL('/rest/v1/rpc/voltmodd_' + operation, url), {
        method: 'POST',
        redirect: 'error',
        headers: {
          apikey: key,
          Authorization: 'Bearer ' + accessToken,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(parameters),
        signal: AbortSignal.timeout(7000),
      });
    } catch {
      throw unavailable();
    }

    if (response.status === 401)
      throw new HttpError(401, 'AUTH_REQUIRED', 'Log in to access your garage.');
    if (response.status === 403)
      throw new HttpError(403, 'BUILD_ACCESS_DENIED', 'Your account cannot access this garage.');
    if (!response.ok) throw unavailable();
    try {
      return await response.json();
    } catch {
      throw unavailable();
    }
  }

  return {
    listBuilds: (accessToken) => rpc('list_builds', accessToken),
    async saveBuild(accessToken, build, expectedRevision) {
      const result = await rpc('save_build', accessToken, {
        p_build: build,
        p_expected_revision: expectedRevision ?? null,
      });
      if (Number.isSafeInteger(result?.conflict)) throw new RevisionConflict(result.conflict);
      if (!result?.build || typeof result.created !== 'boolean') throw unavailable();
      return result;
    },
    importBuilds: (accessToken, builds) => rpc('import_builds', accessToken, { p_builds: builds }),
    deleteBuild: (accessToken, id) => rpc('delete_build', accessToken, { p_id: id }),
  };
}
