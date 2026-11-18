import { createBuild, normalizePaint } from '@voltforge/shared/build';

const STORAGE_KEY = 'voltforge-v1';
const SYNC_KEY = 'voltforge-sync-v1';
export const BUILD_RECORD_PREFIX = 'voltforge-build-v1:';
const recordKey = (id) => BUILD_RECORD_PREFIX + encodeURIComponent(id);
const revisionOf = (value) => (Number.isSafeInteger(value) && value >= 0 ? value : 0);
const isBuild = (value) =>
  value &&
  typeof value.id === 'string' &&
  ['bike', 'scooter'].includes(value.type) &&
  value.selected &&
  typeof value.selected === 'object';
const normalize = (value) => ({
  ...value,
  specs: { ...createBuild().specs, ...value.specs },
  performance: value.performance || {},
  paint: normalizePaint(value.paint),
});
const stable = (value) =>
  Array.isArray(value)
    ? value.map(stable)
    : value && typeof value === 'object'
      ? Object.fromEntries(
          Object.keys(value)
            .sort()
            .map((key) => [key, stable(value[key])]),
        )
      : value;

// Server timestamps and revision counters are metadata, not user edits.
function content(build) {
  const normalized = normalize(build);
  const fields = ['id', 'name', 'type', 'mode', 'vehicle', 'selected', 'specs', 'performance'];
  // Keep the existing content signature for unpainted builds with a pending sync attempt.
  if (Object.keys(normalized.paint).length) fields.push('paint');
  return JSON.stringify(stable(Object.fromEntries(fields.map((key) => [key, normalized[key]]))));
}

/** Each durable record atomically stores a build and its synchronization state. */
export class BuildStore {
  constructor({ storage, api, onStatus = () => {} } = {}) {
    this.storage = storage;
    if (storage === undefined) {
      try {
        this.storage = globalThis.localStorage;
      } catch {
        this.storage = null;
      }
    }
    this.api = api;
    this.onStatus = onStatus;
    this.builds = [];
    this.revisions = Object.create(null);
    this.pending = new Set();
    this.conflicts = new Set();
    this.attempts = new Map();
    this.observed = new Map();
    this.dirty = new Map();
    this.ownEdits = new Set();
    this.editVersion = 0;
    this.ready = false;
    this.flushing = null;
    this.initializing = null;
    try {
      const { active, records } = this.readStored();
      this.applyRecords(records, active);
    } catch {
      /* Storage can be unavailable; editing and export must still work. */
    }
    this.isFirst = !this.current;
    this.current ||= createBuild();
  }

  status(label, kind = 'local') {
    this.onStatus({ label, kind });
  }

  readStored() {
    let saved;
    try {
      saved = JSON.parse(this.storage?.getItem(STORAGE_KEY) || '{}');
    } catch {
      /* Recover the independent records below. */
    }
    let sync;
    try {
      sync = JSON.parse(this.storage?.getItem(SYNC_KEY) || 'null');
    } catch {
      /* Treat missing metadata as pending. */
    }
    const records = new Map();
    for (const value of Array.isArray(saved?.builds) ? saved.builds : []) {
      if (!isBuild(value)) continue;
      records.set(value.id, {
        build: normalize(value),
        revision: revisionOf(sync?.revisions?.[value.id] ?? value.revision),
        pending: !Array.isArray(sync?.pending) || sync.pending.includes(value.id),
        conflict: Array.isArray(sync?.conflicts) && sync.conflicts.includes(value.id),
      });
    }
    const keys = new Set(
      [...records.keys(), ...this.builds.map((build) => build.id)].map(recordKey),
    );
    // Enumeration recovers records even if a tab closed before updating the legacy mirror.
    for (let index = 0; index < (this.storage?.length || 0); index++) {
      const key = this.storage.key?.(index);
      if (key?.startsWith(BUILD_RECORD_PREFIX)) keys.add(key);
    }
    const canonical = new Set();
    for (const key of keys) {
      try {
        const value = JSON.parse(this.storage?.getItem(key) || 'null');
        if (!isBuild(value?.build) || key !== recordKey(value.build.id)) continue;
        records.set(value.build.id, {
          build: normalize(value.build),
          revision: revisionOf(value.revision),
          pending: value.pending !== false,
          conflict: value.conflict === true,
          ...(value.attempt && { attempt: value.attempt }),
        });
        canonical.add(value.build.id);
      } catch {
        /* An unreadable record must not hide the other recoverable builds. */
      }
    }
    return { active: saved?.active, records, canonical };
  }

  applyRecords(records, active = this.current?.id) {
    const current = this.current;
    this.builds = [...records.values()].map((record) => record.build);
    this.revisions = Object.create(null);
    this.pending.clear();
    this.conflicts.clear();
    this.attempts.clear();
    for (const [id, record] of records) {
      this.revisions[id] = record.revision;
      if (record.pending) this.pending.add(id);
      if (record.conflict) this.conflicts.add(id);
      if (record.attempt) this.attempts.set(id, record.attempt);
      this.observed.set(id, content(record.build));
    }
    this.current = this.builds.find((build) => build.id === active) || current || this.builds[0];
  }

  record(build) {
    return {
      build: structuredClone(build),
      revision: revisionOf(this.revisions[build.id] ?? build.revision),
      pending: this.pending.has(build.id),
      conflict: this.conflicts.has(build.id),
      ...(this.attempts.has(build.id) && { attempt: this.attempts.get(build.id) }),
    };
  }

  persist(writeMirror = true) {
    try {
      if (!this.storage?.getItem || !this.storage?.setItem) throw new Error('Storage unavailable');
      const { records, canonical } = this.readStored();
      const changed = new Set();
      for (const local of this.builds) {
        const id = local.id;
        const latest = records.get(id);
        const localContent = content(local);
        const latestContent = latest && content(latest.build);
        const observed = this.observed.get(id);
        const edited =
          this.dirty.get(id) === 'edit' || (this.ownEdits.has(id) && this.pending.has(id));
        if (
          latest &&
          edited &&
          observed !== undefined &&
          latestContent !== observed &&
          localContent !== latestContent
        ) {
          // Two tabs edited the same base. Keep both versions as ordinary exportable builds.
          const copy = {
            ...structuredClone(local),
            id: crypto.randomUUID(),
            name: `${local.name || 'Untitled build'} (local copy)`.slice(0, 150),
          };
          delete copy.revision;
          records.set(copy.id, { build: copy, revision: 0, pending: true, conflict: false });
          changed.add(copy.id);
          this.ownEdits.delete(id);
          this.ownEdits.add(copy.id);
          if (this.current.id === id) this.current = copy;
          this.status(
            'Another tab edited this build — your changes were kept as a local copy',
            'conflict',
          );
        } else if (!latest || this.dirty.has(id)) {
          const record = this.record(local);
          if (latest && this.dirty.get(id) !== 'edit' && latestContent !== observed) {
            // A server acknowledgement may update the baseline of a newer tab edit.
            record.build = latest.build;
            record.pending = latest.pending;
            record.conflict = latest.conflict;
            record.revision = Math.max(record.revision, latest.revision);
          }
          records.set(id, record);
          changed.add(id);
        }
      }
      for (const [id, record] of records) {
        if (changed.has(id) || !canonical.has(id))
          this.storage?.setItem(recordKey(id), JSON.stringify(record));
      }
      this.applyRecords(records);
      this.dirty.clear();
      if (writeMirror) {
        // This remains readable by the original app. Per-build records are authoritative.
        this.storage?.setItem(
          STORAGE_KEY,
          JSON.stringify({ active: this.current.id, builds: this.builds }),
        );
        this.storage?.setItem(
          SYNC_KEY,
          JSON.stringify({
            revisions: this.revisions,
            pending: [...this.pending],
            conflicts: [...this.conflicts],
          }),
        );
      }
      return true;
    } catch {
      this.status('Browser storage unavailable — export a copy', 'error');
      return false;
    }
  }

  refreshFromStorage() {
    return this.persist(false);
  }

  save() {
    this.current.updated = Date.now();
    const id = this.current.id;
    const index = this.builds.findIndex((build) => build.id === id);
    if (index < 0) this.builds.unshift(this.current);
    else this.builds[index] = this.current;
    this.pending.add(id);
    this.dirty.set(id, 'edit');
    this.ownEdits.add(id);
    this.isFirst = false;
    this.editVersion++;
    if (this.persist()) this.status('Saved on this device');
    if (this.ready) void this.flush();
    else if (this.api) void this.initialize();
  }

  acceptServer(id, server) {
    const index = this.builds.findIndex((build) => build.id === id);
    const value = normalize(server);
    if (index < 0) this.builds.push(value);
    else this.builds[index] = value;
    if (this.current?.id === id) this.current = value;
    this.revisions[id] = revisionOf(server.revision);
    this.pending.delete(id);
    this.conflicts.delete(id);
    this.attempts.delete(id);
    this.ownEdits.delete(id);
    this.dirty.set(id, 'sync');
  }

  initialize() {
    if (!this.api) return Promise.resolve();
    if (this.initializing) return this.initializing;
    const startedAt = this.editVersion;
    this.initializing = (async () => {
      if (this.flushing) await this.flushing;
      this.refreshFromStorage();
      let remote = await this.api.listBuilds();
      if (!remote.length && this.builds.length && this.api.importBuilds) {
        const importing = this.builds.map((build) => structuredClone(build));
        for (const build of importing) {
          this.attempts.set(build.id, { content: content(build), revision: 0 });
          this.dirty.set(build.id, 'sync');
        }
        this.persist();
        remote = await this.api.importBuilds(importing);
      }
      this.refreshFromStorage();
      const map = new Map(remote.filter(isBuild).map((build) => [build.id, normalize(build)]));
      for (const local of [...this.builds]) {
        const id = local.id;
        const server = map.get(id);
        map.delete(id);
        if (!server) {
          this.pending.add(id);
          this.dirty.set(id, 'sync');
          continue;
        }
        if (!this.pending.has(id) || content(local) === content(server)) {
          this.acceptServer(id, server);
          continue;
        }
        const attempt = this.attempts.get(id);
        if (attempt && attempt.content === content(server) && server.revision > attempt.revision) {
          this.revisions[id] = server.revision;
          this.attempts.delete(id);
        }
        if (revisionOf(this.revisions[id]) !== server.revision) this.conflicts.add(id);
        else this.conflicts.delete(id);
        this.dirty.set(id, 'sync');
      }
      for (const server of map.values()) this.acceptServer(server.id, server);
      if (this.isFirst && this.builds.length) {
        this.current = this.builds[0];
        this.isFirst = false;
      }
      this.ready = true;
      this.persist();
      await this.flush();
    })()
      .catch(() => {
        this.ready = false;
        this.status('On this device — server unavailable', 'offline');
      })
      .finally(() => {
        this.initializing = null;
        if (!this.ready && this.editVersion > startedAt) void this.initialize();
      });
    return this.initializing;
  }

  async recoverConflict(id, sent) {
    const server = (await this.api.listBuilds()).find((build) => build.id === id);
    const local = this.builds.find((build) => build.id === id);
    if (server && local && content(server) === content(local)) this.acceptServer(id, server);
    else if (server && content(server) === content(sent)) {
      this.revisions[id] = server.revision;
      this.conflicts.delete(id);
      this.attempts.delete(id);
    } else this.conflicts.add(id);
    this.dirty.set(id, 'sync');
    this.persist();
  }

  flush() {
    if (!this.ready || !this.api) return Promise.resolve();
    if (this.flushing) return this.flushing;
    const startedAt = this.editVersion;
    this.flushing = (async () => {
      while (this.ready) {
        this.refreshFromStorage();
        const ids = [...this.pending].filter((id) => !this.conflicts.has(id));
        if (!ids.length) break;
        for (const id of ids) {
          const local = this.builds.find((build) => build.id === id);
          if (!local) {
            this.pending.delete(id);
            continue;
          }
          const sent = structuredClone(local);
          const revision = revisionOf(this.revisions[id]);
          this.attempts.set(id, { content: content(sent), revision });
          this.dirty.set(id, 'sync');
          this.persist();
          try {
            const saved = await this.api.saveBuild(sent, revision);
            this.refreshFromStorage();
            const current = this.builds.find((build) => build.id === id);
            if (current && content(current) === content(sent)) this.acceptServer(id, saved);
            else {
              this.revisions[id] = saved.revision;
              this.attempts.delete(id);
              this.dirty.set(id, 'sync');
            }
            this.persist();
          } catch (error) {
            if (error.status === 409) {
              await this.recoverConflict(id, sent);
              continue;
            }
            this.ready = false;
            this.status('On this device — server unavailable', 'offline');
            break;
          }
        }
      }
      if (this.ready) {
        if (this.conflicts.size)
          this.status('Another tab has newer edits — your local copy is kept', 'conflict');
        else
          this.status(
            this.builds.length ? 'Saved to your private workspace' : 'Workspace connected',
            'synced',
          );
      }
    })()
      .catch(() => {
        this.ready = false;
        this.status('On this device — server unavailable', 'offline');
      })
      .finally(() => {
        this.flushing = null;
        if (!this.ready && this.editVersion > startedAt) void this.initialize();
      });
    return this.flushing;
  }
}
