import { PART_BY_ID } from './catalog/index.js';

export const PAINT_ZONES = Object.freeze({
  frame: 'Frame',
  deck: 'Deck shell',
  body: 'Body panels',
  fork: 'Fork',
  swingarm: 'Swingarm',
  rims: 'Rims',
});

export const isPaintColor = (value) => typeof value === 'string' && /^#[0-9a-f]{6}$/i.test(value);

export function normalizePaint(value) {
  return Object.fromEntries(
    Object.keys(PAINT_ZONES)
      .filter((zone) => Object.hasOwn(value ?? {}, zone) && isPaintColor(value[zone]))
      .map((zone) => [zone, value[zone].toLowerCase()]),
  );
}

export function createBuild(type = 'scooter', name = 'Untitled build') {
  return {
    id: crypto.randomUUID(),
    name,
    type,
    mode: 'new',
    vehicle: '',
    selected: {},
    paint: {},
    specs: { dropout: '', fullV: '', bms: '', batteryLimit: '', motorCount: 1 },
    performance: { schema: 2 },
    updated: Date.now(),
  };
}
export function selectParts(build) {
  return Object.fromEntries(
    Object.entries(build.selected || {})
      .map(([category, id]) => [category, PART_BY_ID.get(id)])
      .filter(([, part]) => part),
  );
}
