import test from 'node:test';
import assert from 'node:assert/strict';
import { createBuild } from '@voltforge/shared/build';
import { estimatePerformance, createPerformanceEngine } from '@voltforge/shared/performance';
import { CATALOG } from '@voltforge/shared/catalog';

test('the reported XF Pro powertrain uses sourced data and keeps unknown peak output qualified', () => {
  const build = {
    ...createBuild('bike'),
    mode: 'rebuild',
    vehicle: 'Arctic Leopard XF Pro',
    selected: { Motors: 'p165', Controllers: 'p151', Batteries: 'p181' },
  };
  const result = estimatePerformance(build);
  assert.equal(result.speed.kind, 'planning');
  assert.ok(result.speed.value > 0);
  assert.equal(result.wh, 3168);
  assert.equal(result.automatic.continuousA, 200);
  assert.ok(result.automatic.assumptions.some((item) => /duration/i.test(item)));
  assert.equal(result.peak.kind, 'ceiling');
  assert.ok(result.peak.missing.includes('motor peak output'));
  assert.deepEqual(build.performance, { schema: 2 });
});

function completedG4() {
  return {
    ...createBuild('scooter', 'G4 Lonnyo rebuild'),
    mode: 'rebuild',
    vehicle: 'KuKirin G4',
    selected: {
      Motors: 'p4',
      Controllers: 'p37',
      Batteries: 'p46',
      Brakes: 'p293',
      Displays: 'p57',
      Accessories: 'p305',
      'Tires & wheels': 'p299',
      Suspension: 'p302',
    },
  };
}

test('the completed Lonnyo G4 build immediately shows automatic speed and peak output', () => {
  const build = completedG4();
  const result = estimatePerformance(build);
  assert.ok(result.speed.value > 0, 'a completed build must show an approximate speed');
  assert.ok(result.peak.value > 0, 'a completed build must show approximate peak power');
  assert.equal(result.speed.kind, 'planning');
  assert.equal(result.peak.kind, 'planning');
  assert.equal(result.wh, 2880);
  assert.ok(result.automatic.assumptions.some((item) => /battery.*current/i.test(item)));
  assert.ok(result.automatic.sources.some((item) => item.url.includes('lonnyo.com')));
  assert.ok(result.automatic.sources.some((item) => item.url.includes('far-driver.com')));
  assert.deepEqual(
    build.performance,
    { schema: 2 },
    'automatic assumptions must not become saved measurements',
  );
});

test('a selected motor, controller and battery are enough; accessories do not gate estimates', () => {
  const build = completedG4();
  build.selected = { Motors: 'p4', Controllers: 'p37', Batteries: 'p46' };
  const three = estimatePerformance(build);
  const eight = estimatePerformance(completedG4());
  assert.equal(three.speed.value, eight.speed.value);
  assert.equal(three.peak.value, eight.peak.value);
  assert.ok(three.speed.value > 0);
});

test('automatic results recalculate from changed parts and lower configured battery limits', () => {
  const build = completedG4(),
    original = estimatePerformance(build);
  build.selected.Batteries = 'p45';
  const changed = estimatePerformance(build);
  assert.notEqual(changed.wh, original.wh);
  build.selected.Batteries = 'p46';
  build.specs.bms = 20;
  build.specs.batteryLimit = 20;
  const limited = estimatePerformance(build);
  assert.ok(limited.speed.value < original.speed.value);
  assert.ok(limited.peak.value < original.peak.value);
});

test('GPS and manually entered peak limits take priority over planning defaults', () => {
  const build = completedG4();
  build.performance = {
    schema: 2,
    gpsSpeed: 73,
    peakMotorW: 15000,
    peakControllerA: 100,
    peakBatteryA: 80,
    peakVoltage: 70,
    peakEfficiency: 90,
  };
  const result = estimatePerformance(build);
  assert.equal(result.speed.kind, 'gps');
  assert.equal(result.speed.value, 73);
  assert.equal(result.peak.kind, 'estimate');
  assert.equal(result.peak.value, 5040);
  assert.equal(result.peak.controllerA, 100);
});

test('missing motor ratings produce a specific inline requirement instead of invented watts', () => {
  const build = completedG4();
  build.selected.Motors = 'p92';
  const result = estimatePerformance(build);
  assert.ok(result.automatic.missing.includes('power'));
  assert.equal(result.speed.value, null);
  build.performance.power = 1500;
  const entered = estimatePerformance(build);
  assert.ok(entered.speed.value > 0);
  assert.ok(entered.peak.value > 0);
});

test('partial builds retain unknown speed and stock G4 retains its factory reference', () => {
  const empty = estimatePerformance(createBuild());
  assert.equal(empty.speed.value, null);
  const stock = { ...createBuild(), mode: 'rebuild', vehicle: 'KuKirin G4' };
  assert.equal(estimatePerformance(stock).speed.kind, 'factory');
  assert.equal(estimatePerformance(stock).peak.value, 2400);
  const manual = completedG4();
  const before = structuredClone(manual);
  createPerformanceEngine(manual).performanceExport();
  assert.deepEqual(manual, before);
});

test('no-load wheel RPM alone remains a ceiling when motor output is unknown', () => {
  const build = completedG4();
  build.selected.Motors = 'p92';
  build.performance = { schema: 2, rpm: 1000, wheel: 11 };
  const result = estimatePerformance(build);
  assert.equal(result.power, null);
  assert.equal(result.speed.kind, 'ceiling');
  assert.ok(result.speed.basis.includes('No-load'));
  assert.ok(result.automatic.missing.includes('power'));
});

test('all catalog motors yield a bounded scenario or a concrete missing-rating prompt', () => {
  for (const motor of CATALOG.filter((part) => part.category === 'Motors')) {
    const build = completedG4();
    build.selected.Motors = motor.id;
    const result = estimatePerformance(build);
    if (result.speed.value === null)
      assert.ok(result.automatic.missing.includes('power'), motor.id);
    else assert.ok(Number.isFinite(result.speed.value) && result.speed.value > 0, motor.id);
    if (result.peak.value !== null) {
      assert.ok(Number.isFinite(result.peak.value) && result.peak.value > 0, motor.id);
      assert.ok(
        result.peak.value <=
          result.peak.loadedV *
            Math.min(result.peak.controllerA, result.peak.batteryA) *
            result.peak.efficiency +
            1e-6,
        motor.id,
      );
    }
    assert.deepEqual(build.performance, { schema: 2 }, motor.id);
  }
});
