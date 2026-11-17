import {
  canonicalVehicleName,
  normalizeVehicleName,
  VEHICLE_INDEX,
} from '@voltforge/shared/vehicles';
import { VEHICLE_REFERENCES as references, VEHICLE_ARTWORK_AUDIT } from './vehicle-artwork.js';

const byName = new Map(references.map((entry) => [normalizeVehicleName(entry.name), entry]));
const indexedNames = new Set(VEHICLE_INDEX.map((entry) => normalizeVehicleName(entry.name)));

/** Only exact, reviewed model references belong in this library. */
export function vehicleReference(name) {
  const exact = normalizeVehicleName(name);
  if (byName.has(exact)) return byName.get(exact);
  if (indexedNames.has(exact)) return null;
  return byName.get(normalizeVehicleName(canonicalVehicleName(name))) || null;
}

export const VEHICLE_REFERENCES = references;
const audited = new Map(
  VEHICLE_ARTWORK_AUDIT.map((entry) => [normalizeVehicleName(entry.name), entry]),
);
export function vehicleArtworkAudit(name) {
  return audited.get(normalizeVehicleName(name)) || null;
}

export function featuredVehicles(type) {
  const names =
    type === 'scooter'
      ? ['KuKirin G4', 'KuKirin G2 Master', 'Ausom DT2 Pro', 'Ausom L2 Max Dual Motor']
      : [
          'Sur-Ron Light Bee X',
          'Talaria Sting Pro MX5',
          'Stark Varg EX',
          'Arctic Leopard XE Pro S',
        ];
  return names.map(vehicleReference).filter(Boolean);
}
