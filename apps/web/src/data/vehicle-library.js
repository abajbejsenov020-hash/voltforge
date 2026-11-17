import { canonicalVehicleName, normalizeVehicleName } from '@voltforge/shared/vehicles';
import references from './vehicle-references.json' with { type: 'json' };

const byName = new Map(references.map((entry) => [normalizeVehicleName(entry.name), entry]));

/** Only exact, reviewed model references belong in this library. */
export function vehicleReference(name) {
  return byName.get(normalizeVehicleName(canonicalVehicleName(name))) || null;
}

export const VEHICLE_REFERENCES = references;

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
