import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { CATALOG, CATEGORIES, PART_BY_ID } from '@voltforge/shared/catalog';
import { VEHICLE_INDEX, canonicalVehicleName, findVehicles } from '@voltforge/shared/vehicles';
import { getVehicleVisual } from '@voltforge/shared/visuals';
import { createBuild, selectParts } from '@voltforge/shared/build';
import { checkCompatibility } from '@voltforge/shared/compatibility';
import {
  createPerformanceEngine,
  estimatePerformance,
  OWNER_SPEED_REPORT,
  peakPowerText,
} from '@voltforge/shared/performance';

const part = (brand, name) => {
  const value = CATALOG.find((entry) => entry.brand === brand && entry.name === name);
  assert.ok(value, `Missing preserved part: ${brand} ${name}`);
  return value;
};

function g4() {
  return { ...createBuild(), mode: 'rebuild', vehicle: 'KuKirin G4' };
}

// Isolate manual-limit mathematics from the stock-hardware inheritance suite.
function unconfiguredBike() {
  return createBuild('bike');
}

function identityDigest(records, fields) {
  const identities = records
    .map((record) => fields.map((field) => record[field]))
    .sort((left, right) => left[0].localeCompare(right[0]));
  return createHash('sha256').update(JSON.stringify(identities)).digest('hex');
}

const newJoyors = [
  'S5-Z',
  'S8-S-Z',
  'S10-S-Z',
  'Y6-S',
  'Y10',
  'T6',
  'T10',
  'T12 Ultra',
  'C10',
  'F5',
].map((model) => 'Joyor ' + model);

test('saved part IDs and vehicle identities survive the module migration', () => {
  assert.equal(CATALOG.length, 315);
  assert.equal(PART_BY_ID.size, 315);
  assert.equal(VEHICLE_INDEX.length, 345 + newJoyors.length);
  assert.equal(new Set(VEHICLE_INDEX.map((vehicle) => vehicle.id)).size, VEHICLE_INDEX.length);
  const originalVehicles = VEHICLE_INDEX.filter((vehicle) => !newJoyors.includes(vehicle.name));
  // Fixed baselines from the recovered app before module extraction. These
  // protect every saved identity, rather than accepting a catalog with the same count.
  assert.equal(
    identityDigest(CATALOG, ['id', 'category', 'brand', 'name', 'type']),
    'dca40bf34dbca61bca31947f48c5097588a5737d030b7dbfa8d711670d923e95',
  );
  assert.equal(
    identityDigest(originalVehicles, ['id', 'name', 'brand', 'type']),
    '6c59c8721577ed97da147da3a60f0a639a711918d68acdd80b33939a226d051c',
  );
  const saved = createBuild();
  saved.selected = { Controllers: 'p291', Batteries: 'p308', Brakes: 'p292' };
  assert.deepEqual(
    Object.fromEntries(Object.entries(selectParts(saved)).map(([key, value]) => [key, value.name])),
    { Controllers: 'ND72260', Batteries: 'G4 Battery Assembly', Brakes: 'MT5 Pro' },
  );
  assert.equal(CATEGORIES.length, 8);
});

test('the Joyor finder keeps legacy scooters and Z revisions distinct', () => {
  for (const name of newJoyors) {
    const compact = name.toLowerCase().replace(/[^a-z0-9]/g, '');
    assert.equal(canonicalVehicleName(compact), name);
    assert.equal(findVehicles(compact)[0]?.name, name, compact);
  }
  assert.equal(findVehicles('joyor s10s')[0]?.name, 'Joyor S10-S');
  assert.equal(findVehicles('joyor s10sz')[0]?.name, 'Joyor S10-S-Z');
});

test('finder preserves compact, typo, Cyrillic, and e-moto aliases across vehicle types', () => {
  const cases = [
    ['kugookiring2max', 'KuKirin G2 Max'],
    ['Kugoo Kirin G2 Master', 'KuKirin G2 Master'],
    ['ku kirin g4', 'KuKirin G4'],
    ['kukrin g2 pro', 'KuKirin G2 Pro'],
    ['кукирин г2 мастер', 'KuKirin G2 Master'],
    ['аусом галоп', 'Ausom Gallop'],
    ['KuKirin scooter G2 Max 2025', 'KuKirin G2 Max'],
    ['surron lbx', 'Sur-Ron Light Bee X'],
    ['talaria mx5', 'Talaria Sting Pro MX5'],
    ['arctic leopard exe880', 'Arctic Leopard E-XE 880 Enduro'],
    ['eride pro ss3.0', 'E Ride Pro SS 3.0'],
  ];
  for (const [query, expected] of cases) {
    assert.ok(
      findVehicles(query, { type: 'scooter' })
        .slice(0, 8)
        .some((vehicle) => vehicle.name === expected),
      `${query} must suggest ${expected}`,
    );
  }
  assert.equal(canonicalVehicleName('Sur Ron LBX'), 'Sur-Ron Light Bee X');
  assert.equal(canonicalVehicleName('KugooKirin G4'), 'KuKirin G4');
  assert.equal(canonicalVehicleName('  My custom vehicle  '), 'My custom vehicle');
  assert.deepEqual(findVehicles('spaceship xyz123'), []);
  assert.ok(
    findVehicles('G4', { brand: 'KuKirin' }).every((vehicle) => vehicle.brand === 'KuKirin'),
  );
  const custom = findVehicles('My unique ride', {
    saved: [{ id: 'saved-build', vehicle: 'My unique ride', type: 'bike' }],
  });
  assert.equal(custom[0].name, 'My unique ride');
  assert.equal(custom[0].custom, true);
});

test('canonical G4 and LBX aliases select their dedicated appearance without conflating G4 Ultra', () => {
  assert.equal(getVehicleVisual('Kugoo Kirin G4', 'scooter').profile, 'kukirin-g4');
  assert.equal(getVehicleVisual('surron lbx', 'bike').profile, 'surron-lbx');
  assert.ok(getVehicleVisual('Sur-Ron Light Bee', 'bike').reference);
  assert.notEqual(getVehicleVisual('KuKirin G4 Ultra', 'scooter').profile, 'kukirin-g4');
});

test('stock G4 uses one 2000 W motor and 60 V 20 Ah while the 90 km/h display stays separate from GPS', () => {
  const build = g4();
  const engine = createPerformanceEngine(build);
  const stock = engine.estimatePerformance();
  assert.equal(stock.stock, true);
  assert.equal(stock.profile.motors, 1);
  assert.equal(stock.profile.ratedMotorW, 2000);
  assert.equal(stock.nominal, 60);
  assert.equal(stock.ah, 20);
  assert.equal(stock.wh, 1200);
  assert.equal(stock.speed.kind, 'factory');
  assert.equal(stock.speed.value, 70);
  assert.equal(stock.dashboard, 90);
  assert.equal(OWNER_SPEED_REPORT.kukiring4.method, 'dashboard');
  assert.equal(stock.a.gpsSpeed, '');
  assert.equal(stock.maxSpeed, null);
  assert.equal(stock.power, null);
  assert.equal(stock.peak.kind, 'factory');
  assert.equal(stock.peak.value, 2400);
  build.performance = { schema: 2, gpsSpeed: 80, dashboardSpeed: 90 };
  const measured = engine.estimatePerformance();
  assert.equal(measured.speed.kind, 'gps');
  assert.equal(measured.speed.value, 80);
  assert.equal(measured.dashboard, 90);
  assert.ok(
    engine.performanceExport().some((line) => line.includes('Display readings are not GPS')),
  );
});

test('range follows riding speed and a measured 800 Wh over 20 km calibrates to 24 km usable range', () => {
  const build = g4();
  const forty = estimatePerformance(build);
  assert.equal(forty.cruise, 40);
  assert.ok(forty.range > 20 && forty.range < 50);
  for (let index = 1; index < forty.scenarios.length; index++) {
    assert.ok(forty.scenarios[index].range < forty.scenarios[index - 1].range);
    assert.ok(forty.scenarios[index].whPerKm > forty.scenarios[index - 1].whPerKm);
  }
  build.performance = { schema: 2, cruise: 80 };
  const eighty = estimatePerformance(build);
  assert.equal(
    eighty.cruise,
    80,
    'a range scenario must not be silently clamped to factory top speed',
  );
  assert.equal(eighty.wh, 1200);
  assert.ok(eighty.range > 0 && eighty.range < forty.range / 2);
  build.performance = { schema: 2, cruise: 40, tripKm: 20, tripUsedWh: 800, tripSpeed: 40 };
  const calibrated = estimatePerformance(build);
  assert.equal(calibrated.calibrated, true);
  assert.equal(calibrated.whPerKm, 40);
  assert.equal(calibrated.usableWh, 960);
  assert.equal(calibrated.range, 24);
  delete build.performance.tripSpeed;
  assert.equal(estimatePerformance(build).calibrated, false);
});

test('modified parts override their category while other factory hardware and exact variants remain distinct', () => {
  const build = g4();
  build.selected.Batteries = CATALOG.find((entry) => entry.name === '72V 40Ah Pack').id;
  const modified = estimatePerformance(build);
  assert.equal(modified.stock, false);
  assert.equal(modified.wh, 2880);
  assert.equal(modified.speed.kind, 'planning');
  assert.equal(modified.p.Motors.stock, true);
  assert.equal(modified.dashboard, 0);
  const twinMotor = g4();
  twinMotor.specs.motorCount = 2;
  assert.equal(estimatePerformance(twinMotor).stock, false);
  assert.equal(estimatePerformance(twinMotor).wh, 1200);
  const differentModel = { ...g4(), vehicle: 'KuKirin G4 Ultra' };
  assert.equal(estimatePerformance(differentModel).profile.name, 'KuKirin G4 Ultra');
  assert.equal(estimatePerformance(differentModel).motors, 2);
  assert.equal(estimatePerformance(differentModel).peak.value, 3000);
  const alias = { ...g4(), vehicle: 'Kugoo Kirin G4' };
  assert.equal(estimatePerformance(alias).stock, true);
});

test('legacy defaults reset and custom battery measurements disable the stock baseline', () => {
  const build = g4();
  build.performance = { power: '1000', cruise: '30', wheel: '10', vehicle: '30' };
  const legacy = estimatePerformance(build);
  assert.equal(legacy.legacy, true);
  assert.equal(legacy.a.power, '');
  assert.equal(legacy.a.cruise, 40);
  assert.equal(legacy.a.vehicle, 41.5);
  assert.equal(legacy.a.wheel, 11);
  build.performance = { schema: 2, nominalVoltage: 60, capacityAh: 30 };
  const measured = estimatePerformance(build);
  assert.equal(measured.stock, false);
  assert.equal(measured.wh, 1800);
  assert.equal(measured.speed.kind, 'planning');
});

test('peak shaft output uses the bottleneck without becoming continuous power or top speed', () => {
  const build = unconfiguredBike();
  build.performance = {
    schema: 2,
    peakMotorW: 15000,
    peakControllerA: 300,
    peakBatteryA: 200,
    peakVoltage: 70,
    peakEfficiency: 90,
  };
  const batteryLimited = estimatePerformance(build);
  assert.equal(batteryLimited.peak.kind, 'estimate');
  assert.equal(batteryLimited.peak.value, 12600);
  assert.equal(batteryLimited.peak.electricalW, 14000);
  assert.equal(batteryLimited.peak.limiter, 'Battery burst-current limit');
  assert.equal(peakPowerText(batteryLimited.peak), '≈12.6 kW');
  assert.equal(batteryLimited.speed.kind, 'unknown');
  assert.equal(batteryLimited.power, null);
  build.performance.peakMotorW = 5000;
  assert.equal(estimatePerformance(build).peak.value, 5000);
  build.specs.motorCount = 2;
  assert.equal(estimatePerformance(build).peak.value, 10000);
  build.specs.motorCount = 1;
  build.performance.peakMotorW = 15000;
  build.performance.peakControllerA = 100;
  assert.equal(estimatePerformance(build).peak.value, 6300);
});

test('manual peak-current inputs cannot override a published controller or configured battery limit', () => {
  const build = unconfiguredBike();
  build.selected.Controllers = part('TORP', 'TC500 2.0').id;
  build.performance = {
    schema: 2,
    peakMotorW: 50000,
    peakControllerA: 1000,
    peakBatteryA: 500,
    peakVoltage: 70,
    peakEfficiency: 90,
  };
  assert.equal(estimatePerformance(build).peak.value, 22050);
  build.specs.batteryLimit = 100;
  assert.equal(estimatePerformance(build).peak.value, 6300);
  delete build.performance.peakBatteryA;
  const incomplete = estimatePerformance(build).peak;
  assert.equal(incomplete.kind, 'ceiling');
  assert.ok(incomplete.missing.includes('battery burst-current limit'));
  delete build.performance.peakMotorW;
  delete build.performance.peakVoltage;
  assert.equal(estimatePerformance(build).peak.kind, 'unknown');
});

test('continuous motor ratings and advertised controller output do not invent peak data', () => {
  const build = unconfiguredBike();
  build.performance = { schema: 2, power: 15000 };
  assert.equal(estimatePerformance(build).peak.kind, 'unknown');
  build.selected.Controllers = part('EBMX', 'X-9000 V3 Controller Kit').id;
  assert.equal(estimatePerformance(build).peak.kind, 'unknown');
});

test('hardware invalidation clears measured speed, trip energy, and burst limits while retaining rider inputs', () => {
  const build = unconfiguredBike();
  build.performance = {
    schema: 2,
    rider: 87,
    cruise: 40,
    gpsSpeed: 80,
    dashboardSpeed: 90,
    tripKm: 20,
    tripUsedWh: 800,
    tripSpeed: 40,
    peakMotorW: 10000,
    peakControllerA: 200,
    peakBatteryA: 150,
    peakVoltage: 70,
  };
  const engine = createPerformanceEngine(build);
  build.selected.Controllers = part('Fardriver', 'ND72260').id;
  engine.invalidatePerformanceMeasurements();
  for (const field of [
    'gpsSpeed',
    'dashboardSpeed',
    'tripKm',
    'tripUsedWh',
    'tripSpeed',
    'peakMotorW',
    'peakControllerA',
    'peakBatteryA',
    'peakVoltage',
  ])
    assert.equal(build.performance[field], '', field);
  assert.equal(build.performance.rider, 87);
  assert.equal(build.performance.cruise, 40);
  assert.equal(engine.estimatePerformance().peak.kind, 'unknown');
  assert.equal(engine.estimatePerformance().speed.kind, 'unknown');
});

test('compatibility still rejects an overvoltage pack and an undersized controller channel count', () => {
  const build = createBuild();
  const motor = CATALOG.find((entry) => entry.name === '10″ 4000W Hub Motor');
  const controller = CATALOG.find((entry) => entry.name === '75100 Pro V2.0');
  const battery = CATALOG.find((entry) => entry.name === '80V 40Ah Pack');
  assert.ok(motor && controller && battery);
  build.selected = { Motors: motor.id, Controllers: controller.id, Batteries: battery.id };
  assert.ok(
    checkCompatibility(build).some(
      (issue) => issue.kind === 'conflict' && issue.text.includes('92.4V'),
    ),
  );
  build.specs.motorCount = 2;
  assert.ok(
    checkCompatibility(build).some(
      (issue) => issue.kind === 'conflict' && issue.text.includes('channel'),
    ),
  );
});
