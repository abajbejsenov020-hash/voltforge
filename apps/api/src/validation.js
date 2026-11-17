import { HttpError } from './http.js';

const SPEC_FIELDS = new Set([
  'dropout',
  'fullV',
  'bms',
  'batteryLimit',
  'motorCount',
  'motorCountOverride',
]);
const PERFORMANCE_FIELDS = new Set([
  'rider',
  'vehicle',
  'cruise',
  'power',
  'efficiency',
  'usable',
  'cda',
  'rolling',
  'wheel',
  'rpm',
  'wind',
  'grade',
  'stops',
  'accessory',
  'nominalVoltage',
  'capacityAh',
  'gpsSpeed',
  'dashboardSpeed',
  'tripKm',
  'tripUsedWh',
  'tripSpeed',
  'peakMotorW',
  'peakControllerA',
  'peakBatteryA',
  'peakVoltage',
  'peakEfficiency',
]);
const isRecord = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);
const invalid = (field, message) => {
  throw new HttpError(422, 'INVALID_BUILD', message, { field });
};

function string(value, field, max, allowEmpty = false) {
  if (
    typeof value !== 'string' ||
    value.length > max ||
    /[\u0000-\u001f\u007f]/.test(value) ||
    (!allowEmpty && !value.trim())
  )
    invalid(
      field,
      `${field} must be ${allowEmpty ? 'a' : 'a nonempty'} string of at most ${max} characters.`,
    );
  return value;
}

function numeric(value, field, { empty = true, signed = false } = {}) {
  if (value === '' && empty) return value;
  if (
    !['number', 'string'].includes(typeof value) ||
    (typeof value === 'string' && !value.trim())
  ) {
    invalid(field, `${field} must be a finite number${empty ? ' or an empty field' : ''}.`);
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || Math.abs(parsed) > 1_000_000_000 || (!signed && parsed < 0)) {
    invalid(
      field,
      `${field} must be a finite ${signed ? '' : 'nonnegative '}number within the supported range.`,
    );
  }
  return value;
}

export function createBuildValidator(catalog, categories) {
  const categoryNames = new Set(
    categories.map((category) => (typeof category === 'string' ? category : category.id)),
  );
  const parts = new Map(catalog.map((part) => [part.id, part]));

  return function validateBuild(input, routeId) {
    if (!isRecord(input)) invalid('build', 'build must be an object.');
    const id = string(input.id, 'id', 100);
    if (routeId !== undefined && id !== routeId) invalid('id', 'The build ID must match the URL.');
    const name = string(input.name, 'name', 150);
    if (!['bike', 'scooter'].includes(input.type)) invalid('type', 'type must be bike or scooter.');
    if (!['new', 'rebuild'].includes(input.mode)) invalid('mode', 'mode must be new or rebuild.');
    const vehicle = string(input.vehicle ?? '', 'vehicle', 150, true);
    if (!isRecord(input.selected))
      invalid('selected', 'selected must be an object of category and part IDs.');
    const selected = {};
    for (const [category, partId] of Object.entries(input.selected)) {
      if (!categoryNames.has(category))
        invalid(`selected.${category}`, 'The selected category does not exist.');
      const part = parts.get(partId);
      if (!part || part.category !== category)
        invalid(`selected.${category}`, 'The selected part does not belong to this category.');
      selected[category] = partId;
    }
    if (!isRecord(input.specs ?? {})) invalid('specs', 'specs must be an object.');
    const specs = {};
    for (const [key, value] of Object.entries(input.specs ?? {})) {
      if (!SPEC_FIELDS.has(key)) invalid(`specs.${key}`, 'This specification is not supported.');
      specs[key] = numeric(value, `specs.${key}`, { empty: key !== 'motorCount' });
      if (['motorCount', 'motorCountOverride'].includes(key) && ![1, 2].includes(Number(value)))
        invalid(`specs.${key}`, `${key} must be 1 or 2.`);
    }
    const sourcePerformance = input.performance ?? {};
    if (!isRecord(sourcePerformance) || ![undefined, 1, 2].includes(sourcePerformance.schema)) {
      invalid(
        'performance.schema',
        'Performance inputs must use schema 1 or 2, or omit the legacy schema.',
      );
    }
    // Keeping the legacy version lets the shared estimator apply its historical defaults.
    const performance =
      sourcePerformance.schema === undefined ? {} : { schema: sourcePerformance.schema };
    for (const [key, value] of Object.entries(sourcePerformance)) {
      if (key === 'schema') continue;
      if (key === 'configuration') {
        if (!['auto', 'custom'].includes(value))
          invalid('performance.configuration', 'configuration must be auto or custom.');
        performance[key] = value;
      } else {
        if (
          !PERFORMANCE_FIELDS.has(key) &&
          (sourcePerformance.schema === 2 || !/^[a-z][a-z0-9_]{0,63}$/i.test(key))
        ) {
          invalid(`performance.${key}`, 'This performance input is not supported.');
        }
        performance[key] = numeric(value, `performance.${key}`, {
          signed: key === 'wind' || key === 'grade',
        });
      }
    }
    const updated = input.updated ?? Date.now();
    if (!Number.isSafeInteger(updated) || updated < 0)
      invalid('updated', 'updated must be a nonnegative integer timestamp.');
    return {
      id,
      name,
      type: input.type,
      mode: input.mode,
      vehicle,
      selected,
      specs,
      performance,
      updated,
    };
  };
}

export function validateRevision(value) {
  if (value !== undefined && (!Number.isSafeInteger(value) || value < 0)) {
    throw new HttpError(422, 'INVALID_REVISION', 'expectedRevision must be a nonnegative integer.');
  }
  return value;
}
