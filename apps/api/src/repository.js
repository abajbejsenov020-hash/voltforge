import { createHash, randomBytes } from 'node:crypto';

export class RevisionConflict extends Error {
  constructor(currentRevision) {
    super('This build changed since it was loaded. Reload it before saving again.');
    this.currentRevision = currentRevision;
  }
}

const hashToken = (token) => createHash('sha256').update(token).digest('hex');
const unpack = (row) => (row ? { ...JSON.parse(row.payload), revision: row.revision } : undefined);

export function createRepository(database) {
  const statements = {
    session: database.prepare('SELECT token_hash FROM sessions WHERE token_hash = ?'),
    addSession: database.prepare('INSERT INTO sessions(token_hash, created_at) VALUES (?, ?)'),
    list: database.prepare(
      'SELECT payload, revision FROM builds WHERE session_hash = ? ORDER BY updated_at DESC, id',
    ),
    get: database.prepare('SELECT payload, revision FROM builds WHERE session_hash = ? AND id = ?'),
    save: database.prepare(`INSERT INTO builds(session_hash, id, payload, revision, updated_at)
      VALUES (?, ?, ?, ?, ?) ON CONFLICT(session_hash, id) DO UPDATE SET
      payload = excluded.payload, revision = excluded.revision, updated_at = excluded.updated_at`),
    import: database.prepare(
      'INSERT OR IGNORE INTO builds(session_hash, id, payload, revision, updated_at) VALUES (?, ?, ?, 1, ?)',
    ),
    delete: database.prepare('DELETE FROM builds WHERE session_hash = ? AND id = ?'),
  };

  function transaction(operation) {
    database.exec('BEGIN IMMEDIATE');
    try {
      const result = operation();
      database.exec('COMMIT');
      return result;
    } catch (error) {
      database.exec('ROLLBACK');
      throw error;
    }
  }

  return {
    resolveSession(token) {
      if (/^[A-Za-z0-9_-]{43}$/.test(token || '')) {
        const hash = hashToken(token);
        if (statements.session.get(hash)) return { hash };
      }
      const newToken = randomBytes(32).toString('base64url');
      const hash = hashToken(newToken);
      statements.addSession.run(hash, Date.now());
      return { hash, token: newToken };
    },
    listBuilds(sessionHash) {
      return statements.list.all(sessionHash).map(unpack);
    },
    saveBuild(sessionHash, build, expectedRevision) {
      return transaction(() => {
        const previous = statements.get.get(sessionHash, build.id);
        const currentRevision = previous?.revision || 0;
        if (expectedRevision !== undefined && expectedRevision !== currentRevision) {
          throw new RevisionConflict(currentRevision);
        }
        const saved = { ...build, updated: Date.now() };
        const revision = currentRevision + 1;
        statements.save.run(sessionHash, build.id, JSON.stringify(saved), revision, saved.updated);
        return { build: { ...saved, revision }, created: !previous };
      });
    },
    importBuilds(sessionHash, builds) {
      return transaction(() => {
        let imported = 0;
        for (const build of builds) {
          imported += Number(
            statements.import.run(sessionHash, build.id, JSON.stringify(build), build.updated)
              .changes,
          );
        }
        return {
          builds: statements.list.all(sessionHash).map(unpack),
          imported,
          skipped: builds.length - imported,
        };
      });
    },
    deleteBuild(sessionHash, id) {
      return Number(statements.delete.run(sessionHash, id).changes) > 0;
    },
  };
}
