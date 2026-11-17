import { normalizeVehicleName, canonicalVehicleName } from './index.js';
import { FEATURED_VEHICLES } from './featured.js';
// Visual families describe appearance only. They do not supply engineering specs.
function getVehicleVisual(name, type = 'scooter') {
  const n = normalizeVehicleName(canonicalVehicleName(name)),
    photo = FEATURED_VEHICLES.find(
      (v) => normalizeVehicleName(v.name) === (n === 'surron light bee' ? 'surron light bee x' : n),
    );
  const base = {
    name: name || 'Custom ' + (type === 'bike' ? 'e-bike' : 'e-scooter'),
    type,
    profile: type === 'bike' ? 'mountain-bike' : 'performance-scooter',
    frame: 0x3a3d40,
    accent: 0xb77a54,
    reference: photo?.image || null,
    source: photo?.source || null,
    fidelity: 'family approximation',
  };
  if (type === 'scooter') {
    if (n === 'kukirin g4')
      return {
        ...base,
        profile: 'kukirin-g4',
        frame: 0x646b6e,
        accent: 0xf29116,
        fidelity: 'photo-guided approximation',
      };
    if (/kukirin|kugoo/.test(n))
      return { ...base, profile: 'kukirin-sport', frame: 0x43484c, accent: 0xe78516 };
    if (/ninebot|xiaomi|niu|inokim light|apollo air|apollo go/.test(n))
      return {
        ...base,
        profile: 'commuter-scooter',
        frame: 0x4f555b,
        accent: /xiaomi/.test(n) ? 0xb6573f : 0xb4973f,
      };
    if (/ausom/.test(n))
      return {
        ...base,
        profile: 'ausom-sport',
        frame: 0x41474c,
        accent: /leopard|gallop/.test(n) ? 0xe17b28 : 0xa4a8aa,
      };
    if (/dualtron/.test(n))
      return { ...base, profile: 'dualtron-sport', frame: 0x282c31, accent: 0xb8bec2 };
    if (/nami/.test(n))
      return { ...base, profile: 'nami-sport', frame: 0x292d30, accent: 0x839e80 };
  } else {
    if (/^surron light bee(?: x)?$/.test(n))
      return {
        ...base,
        profile: 'surron-lbx',
        frame: 0x303336,
        accent: 0xd0dc38,
        fidelity: 'photo-guided approximation',
      };
    if (/surron|talaria|arctic leopard|stark|e ride pro|altis/.test(n))
      return { ...base, profile: 'electric-moto', frame: 0x33383d, accent: 0x969da3 };
    if (/fiido c11/.test(n))
      return { ...base, profile: 'step-through-bike', frame: 0xe0ded6, accent: 0x404749 };
    if (/fiido m1 pro/.test(n))
      return { ...base, profile: 'folding-fat-bike', frame: 0x175e56, accent: 0xbf9a4d };
    if (
      /fiido c21|fiido c22|aventon pace|aventon abound|rad.*runner|rad.*wagon|rad.*city|engwe l20|specialized.*como|trek.*verve/.test(
        n,
      )
    )
      return { ...base, profile: 'step-through-bike', frame: 0x596c71, accent: 0xbba084 };
    if (/engwe|fiido m1|fiido m21|fiido d|lectric xp/.test(n))
      return { ...base, profile: 'folding-fat-bike', frame: 0x505b58, accent: 0xb49057 };
  }
  return base;
}

export { getVehicleVisual };
