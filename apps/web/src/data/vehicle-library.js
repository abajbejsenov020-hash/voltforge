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

const brandPhotoModels = {
  scooter: [
    'KuKirin G4',
    'Ausom DT2 Pro',
    'Dualtron Thunder 3',
    'Segway Ninebot Max G3',
    'Teverun Fighter Supreme',
    'Joyor T12 Ultra',
    'Kaabo Wolf King GTR',
    'Xiaomi M365',
    'Apollo Pro',
    'Bogist M5 Pro',
    'EMOVE Cruiser S',
    'Hiley Tiger 10 Pro',
    'InMotion RS',
    'Inokim OXO',
    'iENYRID M4 Pro S+ Max',
    'iScooter iX6',
    'Kugoo G-Booster',
    'NAMI Burn-E 2 Max',
    'NIU KQi3 Max',
    'RoadRunner RX7',
    'Varla Eagle One Pro',
    'Vsett 10+',
    'Yume Osprey',
    'Zero 10X',
  ],
  bike: [
    'Sur-Ron Light Bee X',
    'Talaria Sting Pro MX5',
    'Stark Varg EX',
    'Arctic Leopard XE Pro S',
    'E Ride Pro SS 3.0',
    'Altis Sigma',
    'Engwe EP-2 Pro',
    'Aventon Aventure.2',
    'Cannondale Moterra Neo',
    'Cube Stereo Hybrid',
    'Fiido Titan',
    'Giant Trance X E+',
    'Haibike AllMtn',
    'Himiway Cobra',
    'KuKirin X1',
    'Lectric XP 3.0',
    'Rad Power RadRunner Plus',
    'Specialized Turbo Levo',
    'Super73 RX',
    'Trek Rail',
  ],
};

export function featuredBrands(type) {
  const models = VEHICLE_INDEX.filter((vehicle) => vehicle.type === type);
  const byModel = new Map(models.map((vehicle) => [vehicle.name, vehicle]));
  const brands = new Map();
  for (const name of brandPhotoModels[type]) {
    const vehicle = byModel.get(name);
    const reference = vehicleReference(name);
    if (vehicle && reference) brands.set(vehicle.brand, reference);
  }
  for (const model of models) {
    if (!brands.get(model.brand)) brands.set(model.brand, vehicleReference(model.name));
  }
  return [...brands].map(([brand, reference]) => ({ brand, reference }));
}
