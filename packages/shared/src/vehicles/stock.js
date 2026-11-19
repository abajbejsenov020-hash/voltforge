import { CATEGORIES } from '../catalog/index.js';
import { selectParts } from '../build.js';
import { canonicalVehicleName, normalizeVehicleName, VEHICLE_INDEX } from './index.js';
import profiles from './stock-profiles.json' with { type: 'json' };

const profileKey = (name) => normalizeVehicleName(name).replace(/[^a-z0-9]/g, '');

// Exact names and registered aliases only: nearby model variants have different hardware.
export const STOCK_PERFORMANCE = Object.fromEntries(
  profiles.map((profile) => [
    profileKey(profile.name),
    {
      ...profile,
      wh:
        profile.nominal > 0 && profile.ah > 0
          ? profile.nominal * profile.ah
          : profile.energyWh || null,
    },
  ]),
);

const indexedNames = new Set(VEHICLE_INDEX.map((entry) => profileKey(entry.name)));
export function vehicleStockProfile(name) {
  const exact = profileKey(name);
  if (STOCK_PERFORMANCE[exact]) return STOCK_PERFORMANCE[exact];
  if (indexedNames.has(exact)) return null;
  return (
    STOCK_PERFORMANCE[profileKey(name)] ||
    STOCK_PERFORMANCE[profileKey(canonicalVehicleName(name))] ||
    null
  );
}

/** The historical value 1 is also the saved untouched default on dual-motor rebuilds. */
export function effectiveMotorCount(state) {
  const override = Number(state.specs?.motorCountOverride);
  if (override === 1 || override === 2) return override;
  const value = Number(state.specs?.motorCount);
  const configured = Number.isFinite(value) && value > 0 ? Math.min(4, Math.max(1, value)) : 1;
  const profile = state.mode === 'rebuild' ? vehicleStockProfile(state.vehicle) : null;
  return configured === 1 && profile?.motors > 0 ? profile.motors : configured;
}

/** OEM family entries can use the documented factory rating as an explicit planning assumption. */
function replacementRatings(part) {
  if (
    part.category !== 'Motors' ||
    !part.detail?.startsWith('OEM replacement') ||
    part.models?.length !== 1
  )
    return part;
  const profile = vehicleStockProfile(part.models[0]);
  if (!profile || !(profile.ratedMotorW > 0 || profile.peakMotorW > 0)) return part;
  return {
    ...part,
    ratedW: part.ratedW || profile.ratedMotorW,
    peakW:
      part.peakW ||
      (profile.peakMotorW > 0 && profile.motors > 0 ? profile.peakMotorW / profile.motors : null),
    factoryRatingAssumption: true,
    variantNote: `OEM replacement uses the ${profile.name} factory motor rating as a planning assumption. Confirm the exact year, winding and supplier version.`,
    sources: [
      {
        url: profile.source,
        note: 'Factory motor specification used for the named OEM replacement family; exact replacement variant unverified.',
      },
    ],
  };
}

/** Effective hardware is transient. Saved selected IDs continue to describe upgrades only. */
export function resolveBuildParts(state) {
  const explicit = Object.fromEntries(
    Object.entries(selectParts(state)).map(([category, part]) => [
      category,
      replacementRatings(part),
    ]),
  );
  if (state.mode !== 'rebuild') return explicit;
  const profile = vehicleStockProfile(state.vehicle);
  const name = profile?.name || state.vehicle || 'Vehicle';
  const sources = profile?.source ? [{ url: profile.source, note: profile.note || '' }] : [];
  const stock = Object.fromEntries(
    CATEGORIES.map((category) => [
      category,
      {
        id: `stock:${profileKey(name)}:${category.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`,
        category,
        name: `${name} factory ${category.toLowerCase()}`,
        type: state.type,
        stock: true,
        models: [name],
        reference: profile?.source || null,
        sources,
      },
    ]),
  );
  Object.assign(stock.Batteries, {
    nominal: profile?.nominal ?? null,
    ah: profile?.ah ?? null,
    energyWh: profile?.energyWh ?? null,
    continuousDischargeA: profile?.batteryA ?? null,
    peakDischargeA: profile?.peakBatteryA ?? null,
  });
  Object.assign(stock.Motors, {
    ratedW: profile?.ratedMotorW ?? null,
    peakW:
      profile?.peakMotorW > 0 && profile?.motors > 0 ? profile.peakMotorW / profile.motors : null,
    motorCount: profile?.motors ?? null,
  });
  stock.Controllers.maxBatteryA = profile?.controllerA ?? null;
  if (profile?.electric === false) {
    delete stock.Motors;
    delete stock.Controllers;
    delete stock.Batteries;
  }
  stock['Tires & wheels'].wheelInches = profile?.wheel ?? null;
  for (const category of ['Motors', 'Controllers']) {
    const part = explicit[category];
    if (
      profile &&
      part &&
      !part.request &&
      !part.template &&
      part.detail?.startsWith('OEM replacement') &&
      part.models?.length === 1 &&
      profileKey(part.models[0]) === profileKey(profile.name)
    ) {
      explicit[category] = { ...part, stockEquivalent: true };
    }
  }
  return { ...stock, ...explicit };
}
