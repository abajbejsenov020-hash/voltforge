import { checkCompatibility } from '../compatibility.js';
import { normalizeVehicleName } from '../vehicles/index.js';
import { vehicleStockProfile, resolveBuildParts, effectiveMotorCount } from '../vehicles/stock.js';
import { automaticPerformanceInputs } from './automatic.js';
export { STOCK_PERFORMANCE } from '../vehicles/stock.js';
// Performance references and energy scenarios are deliberately separate.
// A motor's advertised watts alone do not establish loaded top speed.
// Personal observation supplied by the user; not GPS or independently verified.
export const OWNER_SPEED_REPORT = {
  kukiring4: {
    speed: 90,
    method: 'dashboard',
    note: 'User reports 90 km/h on the scooter display. Actual ground speed is not established.',
  },
};

export function numberInput(value, fallback, min = 0, max = Infinity) {
  const n = Number(value);
  return value !== '' && value !== null && value !== undefined && Number.isFinite(n)
    ? Math.min(max, Math.max(min, n))
    : fallback;
}
export function approx(value, unit) {
  return value === null || !Number.isFinite(value)
    ? '— ' + unit
    : '≈' + (value < 1 ? value.toFixed(1) : Math.round(value)) + ' ' + unit;
}
export function performanceBand(value, unit) {
  return approx(value, unit);
}
export function speedText(e) {
  if (e.speed.kind === 'planning') {
    const range = e.speed.range;
    return (
      '≈' +
      (range && Math.round(range[1]) > Math.round(range[0])
        ? Math.round(range[0]) + '–' + Math.round(range[1])
        : Math.round(e.speed.value)) +
      ' km/h'
    );
  }
  return e.speed.value === null
    ? 'Not established'
    : (e.speed.kind === 'ceiling' ? '≤' : '') + Math.floor(e.speed.value) + ' km/h';
}
export function speedBasisText(e) {
  return e.speed.basis + (e.dashboard ? ' · Your display: ' + e.dashboard + ' km/h' : '');
}
export function peakPowerText(peak) {
  if (peak.kind === 'planning') {
    const range = peak.range;
    return (
      '≈' +
      (range && range[1] - range[0] >= 100
        ? (range[0] / 1000).toFixed(1) + '–' + (range[1] / 1000).toFixed(1)
        : (peak.value / 1000).toFixed(1)) +
      ' kW'
    );
  }
  return peak.value === null
    ? '— kW'
    : (peak.kind === 'ceiling' ? '≤' : peak.kind === 'estimate' ? '≈' : '') +
        (peak.value / 1000).toFixed(1) +
        ' kW';
}
export function peakPowerLabel(peak) {
  if (peak.kind === 'planning') return 'PEAK POWER · ROUGH ESTIMATE';
  return peak.kind === 'factory'
    ? 'FACTORY PEAK REFERENCE'
    : peak.kind === 'ceiling'
      ? 'PEAK OUTPUT · CEILING'
      : 'PEAK MOTOR OUTPUT · ESTIMATE';
}
export function createPerformanceEngine(state) {
  const selected = () => resolveBuildParts(state);
  const checks = () => checkCompatibility(state);
  function performanceProfile() {
    return state.mode === 'rebuild' ? vehicleStockProfile(state.vehicle) : null;
  }
  function performanceHardware(p, profile, configuration = 'auto') {
    const measured = state.performance || {};
    if (
      profile &&
      ((Number(measured.nominalVoltage) > 0 &&
        Number(measured.nominalVoltage) !== profile.nominal) ||
        (Number(measured.capacityAh) > 0 && Number(measured.capacityAh) !== profile.ah))
    )
      return false;
    if (
      !profile ||
      configuration === 'custom' ||
      (profile.motors > 0 && effectiveMotorCount(state) !== profile.motors)
    )
      return false;
    return (
      ['Motors', 'Controllers', 'Batteries'].every(
        (c) => !p[c] || p[c].stock === true || p[c].stockEquivalent === true,
      ) && ![state.specs?.bms, state.specs?.batteryLimit].some((value) => Number(value) > 0)
    );
  }
  function performanceInputs() {
    const p = selected(),
      profile = performanceProfile(),
      stored = state.performance || {},
      legacy = stored.schema !== 2,
      bike = state.type === 'bike',
      configuration = stored.configuration || 'auto',
      stock = performanceHardware(p, profile, configuration);
    const defaults = {
      schema: 2,
      configuration,
      rider: 80,
      vehicle: profile?.vehicleMass > 0 ? profile.vehicleMass : bike ? 25 : 30,
      cruise: profile?.name === 'KuKirin G4' ? 40 : bike ? 25 : 30,
      power: '',
      efficiency: 78,
      usable: 80,
      cda: bike ? 0.55 : 0.65,
      rolling: bike ? 0.009 : 0.018,
      wheel:
        p['Tires & wheels']?.wheelInches ||
        p.Motors?.wheelInches ||
        (state.mode === 'rebuild' ? '' : bike ? 27.5 : 10),
      rpm: '',
      wind: 0,
      grade: 0,
      stops: 0.5,
      accessory: 10,
      nominalVoltage: '',
      capacityAh: '',
      gpsSpeed: '',
      dashboardSpeed: stock
        ? OWNER_SPEED_REPORT[normalizeVehicleName(profile.name).replace(/[^a-z0-9]/g, '')]?.speed ||
          ''
        : '',
      tripKm: '',
      tripUsedWh: '',
      tripSpeed: '',
      peakMotorW: '',
      peakControllerA: '',
      peakBatteryA: '',
      peakVoltage: '',
      peakEfficiency: 90,
    };
    const keep = legacy
      ? Object.fromEntries(
          ['rider', 'cda', 'rolling', 'rpm']
            .filter((k) => stored[k] !== undefined)
            .map((k) => [k, stored[k]]),
        )
      : stored;
    return { ...defaults, ...keep, schema: 2 };
  }
  function invalidatePerformanceMeasurements() {
    state.performance = {
      ...(state.performance?.schema === 2
        ? state.performance
        : Object.fromEntries(
            ['rider', 'cda', 'rolling', 'rpm']
              .filter((key) => state.performance?.[key] !== undefined)
              .map((key) => [key, state.performance[key]]),
          )),
      gpsSpeed: '',
      dashboardSpeed: '',
      tripKm: '',
      tripUsedWh: '',
      tripSpeed: '',
      peakMotorW: '',
      peakControllerA: '',
      peakBatteryA: '',
      peakVoltage: '',
      schema: 2,
    };
  }
  function estimatePeakPower(a, p, stock, profile) {
    const val = (x) => numberInput(x, 0),
      motors = effectiveMotorCount(state),
      enteredMotor = val(a.peakMotorW),
      motorPer = enteredMotor || val(p.Motors?.peakMechanicalW),
      motorW = motorPer ? motorPer * motors : 0;
    const manualController = val(a.peakControllerA),
      publishedController = val(p.Controllers?.maxBatteryA),
      configuredController = val(state.specs.batteryLimit),
      controllerLimits = [manualController, publishedController, configuredController].filter(
        (x) => x > 0,
      ),
      controllerA = controllerLimits.length ? Math.min(...controllerLimits) : 0;
    const batteryLimits = [val(a.peakBatteryA), val(p.Batteries?.peakDischargeA)].filter(
        (x) => x > 0,
      ),
      batteryA = batteryLimits.length ? Math.min(...batteryLimits) : 0,
      loadedV = val(a.peakVoltage),
      efficiency = numberInput(a.peakEfficiency, 90, 40, 98) / 100;
    const anyManual = ['peakMotorW', 'peakControllerA', 'peakBatteryA', 'peakVoltage'].some(
      (key) => val(state.performance?.[key]) > 0,
    );
    if (stock && profile?.peakMotorW && !anyManual)
      return {
        value: profile.peakMotorW,
        kind: 'factory',
        electricalW: null,
        basis:
          'Factory-listed instantaneous motor peak; output measurement basis and duration unverified.',
        missing: [],
        limiter: 'Factory reference',
      };
    const missing = [];
    if (!motorW) missing.push('motor peak output');
    if (!controllerA) missing.push('controller battery-current limit');
    if (!batteryA) missing.push('battery burst-current limit');
    if (!loadedV) missing.push('loaded pack voltage');
    const knownAmps = [controllerA, batteryA].filter((x) => x > 0),
      electricalW = loadedV && knownAmps.length ? loadedV * Math.min(...knownAmps) : null;
    const bounds = [];
    if (motorW) bounds.push({ value: motorW, label: 'Motor output limit' });
    if (loadedV && controllerA)
      bounds.push({
        value: loadedV * controllerA * efficiency,
        label: 'Controller battery-current limit',
      });
    if (loadedV && batteryA)
      bounds.push({ value: loadedV * batteryA * efficiency, label: 'Battery burst-current limit' });
    bounds.sort((x, y) => x.value - y.value);
    const value = bounds.length ? bounds[0].value : null,
      kind = value === null ? 'unknown' : missing.length ? 'ceiling' : 'estimate';
    return {
      value,
      kind,
      electricalW,
      loadedV,
      controllerA,
      batteryA,
      motorW,
      efficiency,
      missing,
      limiter: bounds[0]?.label || '',
      basis:
        kind === 'unknown'
          ? 'Add motor, controller and battery peak limits in Setup & measurements.'
          : kind === 'ceiling'
            ? 'Incomplete ceiling — missing ' + missing.join(', ') + '.'
            : bounds[0].label +
              ' · ' +
              Math.round(efficiency * 100) +
              '% electrical-to-shaft assumption. Burst duration and thermal behavior unverified.',
    };
  }
  function estimatePerformance() {
    const p = selected(),
      profile = performanceProfile(),
      a = performanceInputs(),
      stock = performanceHardware(p, profile, a.configuration),
      mass = numberInput(a.rider, 80, 1) + numberInput(a.vehicle, profile?.vehicleMass || 30, 1),
      eff = numberInput(a.efficiency, 78, 40, 98) / 100,
      cruise = numberInput(a.cruise, 30, 5, 150);
    const selectedNominal = numberInput(p.Batteries?.nominal, 0),
      selectedAh = numberInput(p.Batteries?.ah, 0),
      manualV = numberInput(a.nominalVoltage, 0),
      manualAh = numberInput(a.capacityAh, 0);
    let nominal = 0,
      ah = 0,
      batteryBasis = 'Battery data required';
    nominal = p.Batteries?.stock ? manualV || selectedNominal : selectedNominal || manualV;
    ah = p.Batteries?.stock ? manualAh || selectedAh : selectedAh || manualAh;
    if (nominal && ah) {
      batteryBasis =
        p.Batteries?.stock && !manualV && !manualAh
          ? 'Factory battery reference: ' + profile.name + ' · ' + nominal + 'V × ' + ah + 'Ah'
          : p.Batteries?.stock || (!selectedNominal && !selectedAh)
            ? 'User-entered battery data'
            : p.Batteries?.template
              ? 'Selected battery template — unverified'
              : 'Selected battery data';
    }
    const energyOnly = !manualV && !manualAh ? numberInput(p.Batteries?.energyWh, 0) : 0;
    if ((!nominal || !ah) && energyOnly)
      batteryBasis = p.Batteries?.stock
        ? 'Factory battery energy: ' + profile.name
        : 'Selected battery energy';
    const wh = nominal && ah ? nominal * ah : energyOnly || null,
      usableWh = wh ? (wh * numberInput(a.usable, 80, 1, 100)) / 100 : null;
    const equivalentAh = !ah && energyOnly && nominal ? energyOnly / nominal : 0;
    const automatic = automaticPerformanceInputs(state, p, a, {
      nominal,
      ah: ah || equivalentAh,
      stock: stock && profile?.advertisedSpeed > 0 && profile?.peakMotorW > 0,
      efficiency: eff,
    });
    if (equivalentAh && automatic.enabled) {
      automatic.equivalentAh = equivalentAh;
      automatic.assumptions.unshift(
        `Capacity equivalent assumed at ${equivalentAh.toFixed(1)} Ah from published battery energy ÷ nominal voltage. This is a planning conversion; actual pack Ah and discharge ratings remain unverified.`,
      );
    }
    const calculated = automatic.inputs;
    const roadWh = (speed) => {
      const v = speed / 3.6,
        relativeAir = Math.max(0, v + numberInput(a.wind, 0, -80, 120) / 3.6),
        drag = 0.5 * 1.225 * numberInput(a.cda, 0.65, 0.1, 2) * relativeAir * relativeAir,
        rolling = mass * 9.81 * numberInput(a.rolling, 0.018, 0.001, 0.08),
        climb = (mass * 9.81 * numberInput(a.grade, 0, 0, 25)) / 100,
        driveW = ((drag + rolling + climb) * v) / eff,
        cycles = (numberInput(a.stops, 0.5, 0, 10) * (0.5 * mass * v * v)) / (3600 * eff);
      return (driveW + numberInput(a.accessory, 10, 0, 500)) / speed + cycles;
    };
    const tripKm = numberInput(a.tripKm, 0),
      tripWh = numberInput(a.tripUsedWh, 0),
      tripSpeed = numberInput(a.tripSpeed, 0),
      calibrated = tripKm > 0 && tripWh > 0 && tripSpeed >= 5;
    const energyAtSpeed = (speed) =>
      calibrated ? Math.max(1, tripWh / tripKm + roadWh(speed) - roadWh(tripSpeed)) : roadWh(speed);
    const whPerKm = energyAtSpeed(cruise),
      range = usableWh ? usableWh / whPerKm : null;
    // Optional engineering ceilings; never use nominal/marketing watts as a speed promise.
    const enteredPower = numberInput(calculated.power, 0),
      motors = effectiveMotorCount(state);
    let mechanical = enteredPower ? enteredPower * motors : null,
      limited = false;
    const amps = [
      numberInput(state.specs.bms, 0),
      numberInput(state.specs.batteryLimit, 0),
      automatic.continuousA,
    ].filter((x) => x > 0);
    const supplyVoltage = automatic.enabled
      ? numberInput(calculated.peakVoltage, nominal)
      : nominal;
    const restrictPower = (watts) =>
      nominal && amps.length ? Math.min(watts, supplyVoltage * Math.min(...amps) * eff) : watts;
    if (mechanical && nominal && amps.length) {
      const bounded = restrictPower(mechanical);
      limited = bounded < mechanical;
      mechanical = Math.min(mechanical, bounded);
    }
    function speedFromPower(watts) {
      if (!watts) return null;
      let lo = 0,
        hi = 100;
      for (let i = 0; i < 60; i++) {
        const m = (lo + hi) / 2,
          speed = Math.max(0.01, m * 3.6),
          required =
            (roadWh(speed) -
              (numberInput(a.stops, 0.5, 0, 10) * (0.5 * mass * m * m)) / (3600 * eff)) *
              speed -
            numberInput(a.accessory, 10, 0, 500);
        if (required * eff > watts) hi = m;
        else lo = m;
      }
      return lo * 3.6;
    }
    const powerCeiling = speedFromPower(mechanical);
    const rpm = numberInput(a.rpm, 0),
      wheel = numberInput(a.wheel, 0, 0, 40),
      rpmCeiling = rpm && wheel ? (rpm * Math.PI * wheel * 0.0254 * 60) / 1000 : null,
      ceilings = [powerCeiling, rpmCeiling].filter((x) => x !== null),
      maxSpeed = ceilings.length ? Math.min(...ceilings) : null,
      gps = numberInput(a.gpsSpeed, 0),
      dashboard = numberInput(a.dashboardSpeed, 0);
    let speed = {
      value: null,
      basis: 'Add loaded-speed measurements or verified drivetrain data',
      kind: 'unknown',
    };
    if (gps)
      speed = {
        value: gps,
        basis: 'Your GPS result — reported, conditions not verified',
        kind: 'gps',
      };
    else if (stock && profile.advertisedSpeed > 0)
      speed = {
        value: profile.advertisedSpeed,
        basis: 'Factory reference, not a measured result for your vehicle',
        kind: 'factory',
      };
    else if (
      powerCeiling !== null &&
      automatic.powerRange &&
      automatic.enabled &&
      automatic.speedPlanning
    ) {
      const range = automatic.powerRange?.map((watts) => {
        const speed = speedFromPower(restrictPower(watts * motors));
        return rpmCeiling === null ? speed : Math.min(speed, rpmCeiling);
      });
      speed = {
        value: maxSpeed,
        range,
        kind: 'planning',
        basis:
          'Rough power-based scenario from effective hardware; winding, gearing and actual limits need confirmation',
      };
    } else if (maxSpeed !== null)
      speed = {
        value: maxSpeed,
        basis:
          rpmCeiling !== null
            ? 'No-load wheel RPM / power ceiling; loaded speed unverified'
            : 'Power-based ceiling; winding and gearing unverified',
        kind: 'ceiling',
      };
    let peak = estimatePeakPower(calculated, p, stock, profile);
    if (
      automatic.enabled &&
      automatic.peakPlanning &&
      peak.kind !== 'factory' &&
      peak.value !== null &&
      !peak.missing.length
    ) {
      const range = automatic.peakMotorRange?.map(
        (watts) => estimatePeakPower({ ...calculated, peakMotorW: watts }, p, stock, profile).value,
      );
      peak = {
        ...peak,
        range,
        kind: 'planning',
        basis:
          'Rough burst-output scenario · ' +
          peak.limiter +
          '. Open Assumptions & quick inputs to refine.',
      };
    }
    const conflicts = checks().filter((i) => i.kind === 'conflict').length;
    return {
      peak,
      automatic,
      a,
      p,
      profile,
      stock,
      nominal,
      ah,
      motors,
      batteryBasis,
      wh,
      usableWh,
      cruise,
      whPerKm,
      range,
      time: range ? range / cruise : null,
      power: mechanical,
      powerCeiling,
      maxSpeed,
      rpmKnown: rpm > 0,
      limited,
      speed,
      dashboard,
      calibrated,
      legacy: !!Object.keys(state.performance || {}).length && state.performance.schema !== 2,
      conflicts,
      energyAtSpeed,
      scenarios: [20, 40, 60, 80].map((kmh) => ({
        kmh,
        whPerKm: energyAtSpeed(kmh),
        range: usableWh ? usableWh / energyAtSpeed(kmh) : null,
      })),
    };
  }
  function performanceExport() {
    const e = estimatePerformance();
    return [
      'Peak motor output: ' + peakPowerText(e.peak) + ' | ' + e.peak.kind + ' | ' + e.peak.basis,
      'Peak electrical input ceiling: ' +
        (e.peak.electricalW !== null ? (e.peak.electricalW / 1000).toFixed(1) + 'kW' : 'unknown') +
        '; not continuous power',
      'Speed: ' + speedText(e) + ' | ' + speedBasisText(e),
      'Hardware: ' +
        (e.stock
          ? e.profile.name + ' factory powertrain reference'
          : 'Custom/modified or unknown powertrain'),
      'Battery: ' +
        e.batteryBasis +
        '; nominal energy ' +
        (e.wh ? Math.round(e.wh) + 'Wh' : 'unknown'),
      'Usable battery assumption: ' + (e.usableWh ? Math.round(e.usableWh) + 'Wh' : 'unknown'),
      'Range energy scenario: ' +
        approx(e.range, 'km') +
        ' AT ' +
        e.cruise +
        'km/h; consumption ' +
        e.whPerKm.toFixed(1) +
        'Wh/km',
      'Ride-time scenario: ' + approx(e.time ? e.time * 60 : null, 'min'),
      ...e.scenarios.map(
        (s) =>
          'Scenario at ' +
          s.kmh +
          'km/h: ' +
          approx(s.range, 'km') +
          ' | ' +
          s.whPerKm.toFixed(1) +
          'Wh/km',
      ),
      e.profile
        ? 'Factory reference (separate tests): ' +
          (e.profile.advertisedSpeed || 'unknown') +
          'km/h; ' +
          (e.profile.advertisedRange || 'unknown') +
          'km advertised range. ' +
          (e.profile.note || '') +
          ' ' +
          (e.profile.source || '')
        : 'No stock performance reference available.',
      'Trip-energy calibration: ' + (e.calibrated ? 'entered measurement used' : 'not provided'),
      'Inputs: ' + JSON.stringify(e.a),
      ...(e.automatic.enabled
        ? [
            'AUTOMATIC PLANNING ASSUMPTIONS',
            ...e.automatic.assumptions,
            ...e.automatic.sources.map((source) => 'Source: ' + source.url + ' | ' + source.note),
          ]
        : []),
      'Display readings are not GPS-verified ground speed. Range scenarios are not validated real-world expectations; they do not establish speed achievability or component compatibility.',
    ];
  }
  return {
    performanceProfile,
    performanceHardware,
    performanceInputs,
    invalidatePerformanceMeasurements,
    estimatePeakPower,
    estimatePerformance,
    performanceExport,
  };
}
export function estimatePerformance(build) {
  return createPerformanceEngine(build).estimatePerformance();
}
