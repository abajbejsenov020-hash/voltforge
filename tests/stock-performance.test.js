import test from 'node:test';
import assert from 'node:assert/strict';
import { createBuild, selectParts } from '@voltforge/shared/build';
import { checkCompatibility } from '@voltforge/shared/compatibility';
import { CATEGORIES, PART_BY_ID } from '@voltforge/shared/catalog';
import {
  createPerformanceEngine,
  estimatePerformance,
  STOCK_PERFORMANCE,
} from '@voltforge/shared/performance';
import {
  effectiveMotorCount,
  resolveBuildParts,
  vehicleStockProfile,
} from '@voltforge/shared/stock';

const rebuild = (vehicle = 'KuKirin G4', type = 'scooter') => ({
  ...createBuild(type),
  mode: 'rebuild',
  vehicle,
});

test('rebuilds resolve factory hardware for every unselected category without saving inferred IDs', () => {
  const build = rebuild();
  const before = structuredClone(build);
  const parts = resolveBuildParts(build);
  assert.deepEqual(Object.keys(parts), CATEGORIES);
  assert.ok(Object.values(parts).every((part) => part.stock));
  assert.equal(parts.Batteries.nominal, 60);
  assert.equal(parts.Motors.ratedW, 2000);
  assert.equal(parts['Tires & wheels'].wheelInches, 11);
  assert.deepEqual(selectParts(build), {});
  assert.deepEqual(build, before);
});

test('profile lookup uses exact canonical names and registered aliases without matching adjacent variants', () => {
  assert.equal(vehicleStockProfile('Kugoo Kirin G4'), STOCK_PERFORMANCE.kukiring4);
  assert.equal(vehicleStockProfile('surron lbx').name, 'Sur-Ron Light Bee X');
  assert.equal(vehicleStockProfile('Talaria MX4').name, 'Talaria Sting R MX4');
  assert.notEqual(vehicleStockProfile('KuKirin G4 Ultra'), vehicleStockProfile('KuKirin G4'));
  assert.equal(vehicleStockProfile('KuKirin G4 made-up variant'), null);
});

for (const [category, id] of [
  ['Controllers', 'p37'],
  ['Batteries', 'p46'],
  ['Motors', 'p4'],
]) {
  test(`G4 ${category.toLowerCase()}-only replacement uses selected part plus remaining factory hardware`, () => {
    const build = rebuild();
    build.selected[category] = id;
    const before = structuredClone(build);
    const result = estimatePerformance(build);
    assert.equal(result.p[category], PART_BY_ID.get(id));
    assert.equal(result.p[category].stock, undefined);
    for (const other of CATEGORIES.filter((item) => item !== category))
      assert.equal(result.p[other].stock, true, other);
    assert.equal(result.wh, category === 'Batteries' ? 2880 : 1200);
    assert.equal(result.a.vehicle, 41.5);
    assert.equal(result.a.wheel, 11);
    assert.equal(result.speed.kind, 'planning');
    assert.ok(result.speed.value > 0);
    assert.notEqual(result.speed.value, 70);
    assert.equal(result.peak.kind, 'planning');
    assert.ok(result.peak.value > 0);
    assert.ok(result.range > 0);
    assert.ok(result.automatic.assumptions.some((text) => /factory reference hardware/.test(text)));
    assert.deepEqual(build, before, 'estimation must not persist stock IDs or assumptions');
  });
}

test('non-powertrain upgrades retain the G4 factory baseline and separate display report', () => {
  const build = rebuild();
  build.selected = { Brakes: 'p293', Suspension: 'p302', Accessories: 'p305' };
  const result = estimatePerformance(build);
  assert.equal(result.stock, true);
  assert.equal(result.speed.kind, 'factory');
  assert.equal(result.speed.value, 70);
  assert.equal(result.peak.value, 2400);
  assert.equal(result.dashboard, 90);
  assert.equal(result.wh, 1200);
});

test('dual-motor profile overrides the historical untouched one-motor default', () => {
  const build = rebuild('KuKirin G2 Master');
  assert.equal(build.specs.motorCount, 1);
  assert.equal(effectiveMotorCount(build), 2);
  const result = estimatePerformance(build);
  assert.equal(result.motors, 2);
  assert.equal(result.p.Motors.motorCount, 2);
  assert.equal(result.wh, 52 * 20.8);
  build.selected.Controllers = 'p37';
  const changed = estimatePerformance(build);
  assert.equal(changed.motors, 2);
  assert.ok(changed.speed.value > 0);
  assert.ok(changed.peak.value > 0);
  assert.equal(changed.a.wheel, 10);
});

for (const vehicle of ['surron lbx', 'Talaria MX4']) {
  test(`${vehicle} inherits model battery, mass and outer wheel diameter after one replacement`, () => {
    const build = rebuild(vehicle, 'bike');
    build.selected.Controllers = 'p37';
    const profile = vehicleStockProfile(vehicle);
    const result = estimatePerformance(build);
    assert.equal(result.wh, profile.nominal * profile.ah);
    assert.equal(result.a.vehicle, profile.vehicleMass);
    assert.equal(result.a.wheel, profile.wheel || '');
    assert.notEqual(result.a.wheel, 27.5);
    assert.equal(result.motors, profile.motors);
    assert.equal(result.speed.kind, 'planning');
    assert.ok(result.speed.value > 0);
    assert.ok(result.peak.value > 0);
    assert.ok(result.range > 0);
    assert.equal(result.dashboard, 0, 'G4 owner observation must not leak into other profiles');
  });
}

test('an explicit motor count override supports a single-motor conversion of a dual-motor vehicle', () => {
  const build = rebuild('KuKirin G2 Master');
  build.specs.motorCountOverride = 1;
  assert.equal(effectiveMotorCount(build), 1);
  const result = estimatePerformance(build);
  assert.equal(result.stock, false);
  assert.equal(result.motors, 1);
  assert.equal(result.speed.kind, 'planning');
  assert.equal(result.wh, 52 * 20.8);
});

test('unknown factory hardware remains present with unknown specifications', () => {
  const build = rebuild('Unknown prototype', 'bike');
  const parts = resolveBuildParts(build);
  assert.equal(Object.keys(parts).length, 8);
  assert.ok(Object.values(parts).every((part) => part.stock));
  assert.equal(parts.Motors.ratedW, null);
  assert.equal(parts.Motors.motorCount, null);
  assert.equal(parts.Batteries.nominal, null);
  const result = estimatePerformance(build);
  assert.equal(result.wh, null);
  assert.equal(result.speed.value, null);
  assert.equal(result.peak.value, null);
  assert.equal(result.range, null);
  assert.equal(result.a.wheel, '');
});

test('new builds use only explicit selected components even when vehicle happens to name a known model', () => {
  const build = createBuild();
  build.vehicle = 'KuKirin G4';
  build.selected.Controllers = 'p37';
  assert.deepEqual(Object.keys(resolveBuildParts(build)), ['Controllers']);
  assert.equal(estimatePerformance(build).wh, null);
  assert.equal(estimatePerformance(build).speed.value, null);
  build.selected.Motors = 'p4';
  build.selected.Batteries = 'p46';
  assert.ok(estimatePerformance(build).speed.value > 0);
});

test('restoring a saved partial rebuild reproduces results and removing a replacement restores stock', () => {
  const build = rebuild();
  build.selected.Controllers = 'p37';
  const saved = JSON.parse(JSON.stringify(build));
  const first = estimatePerformance(build),
    restored = estimatePerformance(saved);
  assert.equal(first.speed.value, restored.speed.value);
  assert.equal(first.peak.value, restored.peak.value);
  assert.equal(first.range, restored.range);
  assert.deepEqual(saved.selected, { Controllers: 'p37' });
  delete saved.selected.Controllers;
  assert.equal(estimatePerformance(saved).speed.kind, 'factory');
  assert.equal(estimatePerformance(saved).peak.value, 2400);
});

test('battery measurements and GPS override inherited references without saving planning inputs', () => {
  const build = rebuild();
  build.performance = { schema: 2, nominalVoltage: 60, capacityAh: 30, gpsSpeed: 73 };
  const before = structuredClone(build);
  const result = estimatePerformance(build);
  assert.equal(result.wh, 1800);
  assert.equal(result.stock, false);
  assert.equal(result.speed.kind, 'gps');
  assert.equal(result.speed.value, 73);
  assert.deepEqual(build, before);
});

test('invalidation clears old observations without materializing stock defaults as saved measurements', () => {
  const build = rebuild();
  build.performance = {
    schema: 2,
    rider: 87,
    gpsSpeed: 73,
    tripKm: 20,
    tripUsedWh: 600,
    tripSpeed: 30,
  };
  build.selected.Controllers = 'p37';
  createPerformanceEngine(build).invalidatePerformanceMeasurements();
  assert.equal(build.performance.rider, 87);
  assert.equal(build.performance.gpsSpeed, '');
  assert.equal(build.performance.tripUsedWh, '');
  for (const key of ['vehicle', 'wheel', 'power', 'nominalVoltage', 'capacityAh'])
    assert.equal(Object.hasOwn(build.performance, key), false, key);
  assert.equal(estimatePerformance(build).speed.kind, 'planning');
});

test('published energy supplies range with a disclosed transient capacity conversion, not fabricated source Ah', () => {
  const build = rebuild('Stark Varg MX', 'bike');
  const before = structuredClone(build);
  const profile = vehicleStockProfile(build.vehicle);
  assert.equal(profile.ah, null);
  assert.ok(profile.energyWh > 0);
  const result = estimatePerformance(build);
  assert.equal(result.wh, profile.energyWh);
  assert.ok(result.range > 0);
  assert.ok(result.speed.value > 0);
  assert.equal(result.peak.kind, 'factory');
  assert.equal(result.peak.value, profile.peakMotorW);
  assert.ok(result.automatic.assumptions.some((text) => /Capacity equivalent/.test(text)));
  assert.deepEqual(build, before);
});

test('stock models with incomplete published metrics compute only disclosed planning replacements', () => {
  const g2 = estimatePerformance(rebuild('KuKirin G2 Max'));
  assert.equal(g2.speed.kind, 'factory');
  assert.equal(g2.speed.value, 55);
  assert.equal(g2.peak.kind, 'planning');
  assert.ok(g2.peak.value > 0);
  const mx4 = estimatePerformance(rebuild('Talaria Sting R MX4', 'bike'));
  assert.equal(mx4.peak.kind, 'factory');
  assert.equal(mx4.peak.value, 8000);
  assert.equal(mx4.speed.kind, 'planning');
});

test('unknown exact factory specifications retain stock labels and request ratings without inventing metrics', () => {
  const result = estimatePerformance(rebuild('Talaria XXX', 'bike'));
  assert.ok(Object.values(result.p).every((part) => part.stock));
  assert.equal(result.wh, null);
  assert.equal(result.speed.value, null);
  assert.equal(result.peak.value, null);
  assert.ok(result.automatic.missing.includes('nominalVoltage'));
  assert.ok(result.automatic.missing.includes('capacityAh'));
});

test('the G4 OEM replacement motor preserves the original factory references with unchanged controller and battery', () => {
  const build = rebuild();
  build.selected.Motors = 'p72';
  const result = estimatePerformance(build);
  assert.equal(result.p.Motors.ratedW, 2000);
  assert.equal(result.p.Motors.peakW, 2400);
  assert.equal(result.p.Motors.stockEquivalent, true);
  assert.equal(result.speed.kind, 'factory');
  assert.equal(result.speed.value, 70);
  assert.equal(result.peak.kind, 'factory');
  assert.equal(result.peak.value, 2400);
  assert.equal(result.wh, 1200);
  assert.equal(PART_BY_ID.get('p72').ratedW, undefined, 'inference must not mutate the catalog');
  build.selected.Controllers = 'p37';
  const modified = estimatePerformance(build);
  assert.equal(modified.stock, false);
  assert.equal(modified.speed.kind, 'planning');
  assert.ok(
    modified.automatic.assumptions.some((text) => /OEM replacement uses the KuKirin G4/.test(text)),
  );
  build.vehicle = 'KuKirin G2 Max';
  assert.equal(resolveBuildParts(build).Motors.stockEquivalent, undefined);
});

test('same-model OEM controllers retain the factory baseline while dual-controller requests remain unverified', () => {
  const g4 = rebuild();
  g4.selected.Controllers = 'p83';
  assert.equal(estimatePerformance(g4).speed.value, 70);
  assert.equal(estimatePerformance(g4).peak.value, 2400);
  assert.equal(resolveBuildParts(g4).Controllers.stockEquivalent, true);
  g4.specs.motorCountOverride = 2;
  assert.equal(estimatePerformance(g4).stock, false);
  assert.ok(
    checkCompatibility(g4).some((issue) => issue.kind === 'conflict' && /channel/.test(issue.text)),
  );
  const dual = rebuild('KuKirin G2 Master');
  dual.selected.Controllers = 'p86';
  assert.equal(resolveBuildParts(dual).Controllers.stockEquivalent, undefined);
  assert.equal(estimatePerformance(dual).stock, false);
  assert.equal(
    checkCompatibility(dual).some(
      (issue) => issue.kind === 'conflict' && /channel/.test(issue.text),
    ),
    true,
  );
});
