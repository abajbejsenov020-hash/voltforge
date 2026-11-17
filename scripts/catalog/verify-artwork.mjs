import { readFileSync, statSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { VEHICLE_INDEX } from '@voltforge/shared/vehicles';
import original from '../../apps/web/src/data/vehicle-references.json' with { type: 'json' };
const root = resolve(import.meta.dirname, '../..');
const old = new Set(original.map((entry) => entry.name));
const expected = new Map(
  VEHICLE_INDEX.filter((entry) => !old.has(entry.name)).map((entry) => [entry.name, entry]),
);
const ready = [];
const unresolved = [];
const seen = new Set();
function check(condition, message) {
  if (!condition) throw new Error(message);
}
for (const batch of ['commuter', 'premium', 'bikes']) {
  const data = JSON.parse(
    readFileSync(resolve(root, `apps/web/src/data/vehicle-expansion-${batch}.json`), 'utf8'),
  );
  for (const row of [...data.entries, ...data.unresolved]) {
    check(expected.has(row.name), `${batch}: unexpected name ${row.name}`);
    check(!seen.has(row.name), `Duplicate audit record: ${row.name}`);
    check(expected.get(row.name).type === row.type, `${row.name}: catalog type changed`);
    seen.add(row.name);
  }
  for (const row of data.entries) {
    check(
      /^https:\/\//.test(row.source) && /^https:\/\//.test(row.imageSource),
      `${row.name}: source URLs required`,
    );
    check(
      row.image?.startsWith('/assets/vehicles/expansion/'),
      `${row.name}: local source image required`,
    );
    const image = resolve(root, 'apps/web/public' + row.image);
    check(statSync(image).size === row.bytes, `${row.name}: image bytes differ`);
    check(
      row.dimensions?.length === 2 && row.dimensions.every((n) => Number.isInteger(n) && n > 0),
      `${row.name}: actual image dimensions required`,
    );
    check(row.model?.bytes > 0, `${row.name}: model not ready`);
    check(
      statSync(resolve(root, 'apps/web/public' + row.model.url)).size === row.model.bytes,
      `${row.name}: GLB size differs`,
    );
    check(
      statSync(resolve(root, row.model.nativeSource)).size > 10000,
      `${row.name}: editable source missing`,
    );
    ready.push(row);
  }
  for (const row of data.unresolved) {
    check(
      row.reason?.length > 20 && row.sources?.length > 0,
      `${row.name}: unresolved requires an actual source audit`,
    );
    check(
      row.sources.every((source) => /^https:\/\//.test(source)),
      `${row.name}: audit URLs required`,
    );
    unresolved.push(row);
  }
}
const pending = [...expected.values()].filter((entry) => !seen.has(entry.name));
if (process.argv.includes('--complete'))
  check(
    pending.length === 0,
    `Unaudited (${pending.length}): ${pending.map((entry) => entry.name).join(', ')}`,
  );
const result = {
  catalogCount: VEHICLE_INDEX.length,
  referenceCount: original.length + ready.length,
  addedCount: ready.length,
  auditedUnresolvedCount: unresolved.length,
  pendingCount: pending.length,
};
if (process.argv.includes('--write-status')) {
  writeFileSync(
    resolve(root, 'apps/web/public/assets/vehicles/unresolved.json'),
    JSON.stringify(
      {
        ...result,
        unresolvedCount: unresolved.length + pending.length,
        scope:
          'Source audit separates verified photo/Blender appearances from unresolved model identity and entries still awaiting audit. No unrelated look-alike is substituted.',
        unresolved,
        pending: pending.map(({ name, type }) => ({
          name,
          type,
          reason: 'Source/model audit is still pending.',
        })),
      },
      null,
      2,
    ) + '\n',
  );
}
console.log(JSON.stringify(result));
