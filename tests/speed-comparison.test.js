import test from 'node:test';
import assert from 'node:assert/strict';
import { createBuild } from '@voltforge/shared/build';
import { estimatePerformance } from '@voltforge/shared/performance';
const g4 = (selected = {}) => ({
  ...createBuild(),
  mode: 'rebuild',
  vehicle: 'KuKirin G4',
  selected,
});
test('a stronger motor is compared with the factory vehicle on the same speed basis', () => {
  const stock = estimatePerformance(g4());
  const motor = estimatePerformance(g4({ Motors: 'p6' }));
  assert.equal(stock.speed.value, 70);
  assert.ok(
    motor.speed.value >= stock.speed.value,
    `factory ${stock.speed.value} versus stronger motor ${motor.speed.value}: an assumed supply cap must not create an unexplained method-switch penalty`,
  );
});

test('the reference is not a minimum-speed clamp: a weaker motor and entered low current can be slower', () => {
  const weak = g4({ Motors: 'p9' });
  const weakResult = estimatePerformance(weak);
  assert.ok(weakResult.speed.value < 70);
  const restricted = g4({ Motors: 'p6' });
  restricted.specs.bms = 20;
  restricted.specs.batteryLimit = 20;
  const result = estimatePerformance(restricted);
  assert.ok(result.speed.value < 70);
  assert.ok(result.speedLimits.some((limit) => limit.kind === 'configured-current'));
  assert.match(result.speed.basis, /Entered supply limits/);
});

test('a known wheel RPM ceiling still wins over a stronger motor or the stock reference', () => {
  const build = g4({ Motors: 'p6' });
  build.performance = { schema: 2, rpm: 800, wheel: 11 };
  const result = estimatePerformance(build);
  assert.ok(result.speed.value < 70);
  assert.ok(result.speedLimits.some((limit) => limit.kind === 'wheel-rpm'));
  assert.match(result.speed.basis, /wheel RPM/);
});

test('manually entered controller and battery current are identified as configured limits', () => {
  for (const field of ['peakControllerA', 'peakBatteryA']) {
    for (const selected of [{}, { Motors: 'p6' }]) {
      const build = g4(selected);
      build.performance = { schema: 2, [field]: 10 };
      const result = estimatePerformance(build);
      assert.ok(result.speed.value < 70, `${field} ${JSON.stringify(selected)}`);
      assert.ok(
        result.speedLimits.some((limit) => limit.kind === 'configured-current'),
        field,
      );
      assert.match(result.speed.basis, /Entered supply limits/);
    }
  }
  const nonbinding = g4({ Motors: 'p6' });
  nonbinding.performance = { schema: 2, peakControllerA: 100 };
  assert.ok(
    estimatePerformance(nonbinding).speedLimits.some((limit) => limit.kind === 'supply-scenario'),
  );
});

test('bigger motor and matched supply can exceed stock while stock supply explains a plateau', () => {
  const motorOnly = estimatePerformance(g4({ Motors: 'p6' }));
  const matched = estimatePerformance(g4({ Motors: 'p6', Controllers: 'p37', Batteries: 'p46' }));
  assert.ok(matched.speed.value > motorOnly.speed.value);
  assert.ok(motorOnly.speedLimits.some((limit) => limit.kind === 'supply-scenario'));
  assert.match(motorOnly.speed.basis, /cannot use its full rating/);
});

test('reference comparison does not erase wind/load or persist inferred measurements', () => {
  const normal = g4({ Motors: 'p6' });
  const before = structuredClone(normal);
  const speed = estimatePerformance(normal).speed.value;
  assert.deepEqual(normal, before);
  const headwind = structuredClone(normal);
  headwind.performance.wind = 40;
  headwind.performance.rider = 150;
  assert.ok(estimatePerformance(headwind).speed.value < speed);
  normal.performance.gpsSpeed = 81;
  assert.equal(estimatePerformance(normal).speed.kind, 'gps');
  assert.equal(estimatePerformance(normal).speed.value, 81);
});

test('entered RPM and output are not hidden by the unmodified factory reference', () => {
  const rpm = g4();
  rpm.performance = { schema: 2, rpm: 800, wheel: 11 };
  const result = estimatePerformance(rpm);
  assert.equal(result.speed.kind, 'ceiling');
  assert.ok(result.speed.value < 70);
  assert.ok(result.speedLimits.some((limit) => limit.kind === 'wheel-rpm'));
  const measured = g4();
  measured.performance = { schema: 2, power: 1000 };
  assert.equal(estimatePerformance(measured).speed.kind, 'planning');
  assert.ok(estimatePerformance(measured).speed.value < 70);
});
