import { PART_BY_ID } from './catalog/index.js';
export function createBuild(type = 'scooter', name = 'Untitled build') {
  return {
    id: crypto.randomUUID(),
    name,
    type,
    mode: 'new',
    vehicle: '',
    selected: {},
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
