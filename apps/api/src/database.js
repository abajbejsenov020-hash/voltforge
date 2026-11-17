import { DatabaseSync } from 'node:sqlite';
import { mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

export function openDatabase(databasePath) {
  if (databasePath !== ':memory:')
    mkdirSync(dirname(resolve(databasePath)), { recursive: true, mode: 0o700 });
  const database = new DatabaseSync(databasePath);
  let migrating = false;
  try {
    database.exec(
      'PRAGMA foreign_keys = ON; PRAGMA busy_timeout = 5000; PRAGMA journal_mode = WAL;',
    );
    database.exec('BEGIN IMMEDIATE');
    migrating = true;
    const { user_version: version } = database.prepare('PRAGMA user_version').get();
    if (version > 1) throw new Error('This database requires a newer Voltforge API.');
    if (version === 0) {
      database.exec(`
        CREATE TABLE sessions (
          token_hash TEXT PRIMARY KEY CHECK(length(token_hash) = 64),
          created_at INTEGER NOT NULL
        ) STRICT;
        CREATE TABLE builds (
          session_hash TEXT NOT NULL REFERENCES sessions(token_hash) ON DELETE CASCADE,
          id TEXT NOT NULL,
          payload TEXT NOT NULL CHECK(json_valid(payload)),
          revision INTEGER NOT NULL CHECK(revision > 0),
          updated_at INTEGER NOT NULL,
          PRIMARY KEY(session_hash, id)
        ) STRICT;
        CREATE INDEX builds_session_updated ON builds(session_hash, updated_at DESC, id);
        PRAGMA user_version = 1;
      `);
    }
    database.exec('COMMIT');
    migrating = false;
    return database;
  } catch (error) {
    if (migrating) database.exec('ROLLBACK');
    database.close();
    throw error;
  }
}
