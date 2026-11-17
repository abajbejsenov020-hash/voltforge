import ratings from '../catalog/performance-ratings.json' with { type: 'json' };

const positive = (value) =>
  Number.isFinite(Number(value)) && Number(value) > 0 ? Number(value) : 0;
const lowest = (...values) => {
  const known = values.map(positive).filter(Boolean);
  return known.length ? Math.min(...known) : 0;
};
const band = (value, range) =>
  range?.length === 2 && range.every(positive)
    ? range.map(Number)
    : positive(value)
      ? [Number(value), Number(value)]
      : null;
const midpoint = (range) => (range[0] + range[1]) / 2;
const display = (value) => Number(value.toFixed(1));

/** Transient planning inputs: these assumptions never become saved hardware measurements. */
export function automaticPerformanceInputs(
  state,
  parts,
  inputs,
  { nominal, ah, stock, efficiency },
) {
  const result = {
    enabled:
      !stock && Boolean(parts.Motors && parts.Controllers && (parts.Batteries || (nominal && ah))),
    inputs: { ...inputs },
    assumptions: [],
    sources: [],
    missing: [],
    speedPlanning: false,
    peakPlanning: false,
    continuousA: 0,
    powerRange: null,
    peakMotorRange: null,
  };
  if (!result.enabled) return result;
  const a = result.inputs;
  const motor = { ...parts.Motors, ...ratings[parts.Motors.id] };
  const controller = { ...parts.Controllers, ...ratings[parts.Controllers.id] };
  const battery = { ...parts.Batteries, ...ratings[parts.Batteries?.id] };
  for (const part of [motor, controller, battery]) {
    for (const source of part.sources || [])
      if (!result.sources.some((item) => item.url === source.url)) result.sources.push(source);
  }
  if (!nominal || !ah) {
    if (!nominal) result.missing.push('nominalVoltage');
    if (!ah) result.missing.push('capacityAh');
    return result;
  }
  const assume = (text) => result.assumptions.push(text);
  const motorElectrical = band(motor.ratedW || motor.watts, motor.ratedWRange);
  const motorMechanical = band(motor.ratedMechanicalW);
  if (!positive(a.power)) {
    if (motorMechanical) result.powerRange = motorMechanical;
    else if (motorElectrical) {
      result.powerRange = motorElectrical.map((watts) => watts * efficiency);
      assume(
        `Motor rating ${display(motorElectrical[0])}${motorElectrical[1] !== motorElectrical[0] ? '–' + display(motorElectrical[1]) : ''} W is treated as electrical input with ${Math.round(efficiency * 100)}% shaft efficiency. Confirm the winding and rating basis.`,
      );
    }
    if (result.powerRange) {
      a.power = midpoint(result.powerRange);
      result.speedPlanning = true;
    } else result.missing.push('power');
  } else result.powerRange = [positive(a.power), positive(a.power)];

  const knownContinuous = lowest(state.specs.bms, battery.continuousDischargeA);
  result.continuousA = knownContinuous || ah * 2;
  if (!knownContinuous) {
    assume(
      `Battery continuous current assumed at 2C (${display(result.continuousA)} A). Capacity alone does not establish the pack or BMS discharge rating.`,
    );
    result.speedPlanning = true;
  }
  if (!positive(a.peakVoltage)) {
    a.peakVoltage = nominal * 0.9;
    assume(
      `Loaded pack voltage assumed at 90% of nominal (${display(a.peakVoltage)} V); replace it with a measurement.`,
    );
    result.speedPlanning = result.peakPlanning = true;
  }

  const explicitBurst = lowest(a.peakBatteryA, battery.peakDischargeA);
  a.peakBatteryA = explicitBurst || Math.min(ah * 3, result.continuousA * 1.5);
  if (!explicitBurst) {
    assume(
      `Battery burst current assumed at ${display(a.peakBatteryA)} A (up to 3C and 1.5× continuous current). Verify cells and BMS; this is a planning scenario.`,
    );
    result.peakPlanning = true;
  }
  const publishedController = positive(controller.maxBatteryA);
  const configuredController = lowest(
    a.peakControllerA,
    state.specs.batteryLimit,
    publishedController,
  );
  a.peakControllerA = configuredController || a.peakBatteryA;
  if (!configuredController) {
    assume(
      `Controller battery-current setting assumed at ${display(a.peakControllerA)} A; no exact battery-current rating is available. Phase amps are not used as battery amps.`,
    );
    result.speedPlanning = result.peakPlanning = true;
  }
  if (
    publishedController &&
    !positive(inputs.peakControllerA) &&
    !positive(state.specs.batteryLimit)
  ) {
    assume(
      `Controller uses the published ${display(publishedController)} A battery-bus maximum as a ceiling; your configured current may be lower.`,
    );
    result.speedPlanning = result.peakPlanning = true;
  }
  result.continuousA = lowest(result.continuousA, a.peakBatteryA, a.peakControllerA);

  const peakEff = Math.min(0.98, Math.max(0.4, positive(a.peakEfficiency) / 100 || 0.9));
  if (positive(a.peakMotorW)) result.peakMotorRange = [Number(a.peakMotorW), Number(a.peakMotorW)];
  else if (positive(motor.peakMechanicalW)) {
    a.peakMotorW = positive(motor.peakMechanicalW);
    result.peakMotorRange = [a.peakMotorW, a.peakMotorW];
  } else {
    const publishedPeak = band(motor.peakW, motor.peakWRange);
    if (publishedPeak) {
      result.peakMotorRange = publishedPeak.map((watts) => watts * peakEff);
      assume(
        `Published peak motor watts are treated as electrical input at ${Math.round(peakEff * 100)}% shaft efficiency; the supplier does not establish a measured shaft-output basis.`,
      );
    } else if (result.powerRange) {
      // This is explicitly a burst scenario, not a manufacturer peak rating.
      result.peakMotorRange =
        motorElectrical && !positive(inputs.power)
          ? motorElectrical.map((watts) => watts * 1.5 * peakEff)
          : result.powerRange.map((watts) => watts * 1.5);
      assume(
        'Motor burst output assumed at 1.5× its rated-power basis. Burst duration and thermal capability are unverified.',
      );
    }
    if (result.peakMotorRange) {
      a.peakMotorW = midpoint(result.peakMotorRange);
      result.peakPlanning = true;
    }
  }
  if (motor.variantNote) assume(motor.variantNote);
  return result;
}
