import { selectParts } from '../build.js';
import { checkCompatibility } from '../compatibility.js';
import { normalizeVehicleName } from '../vehicles/index.js';
// Performance references and energy scenarios are deliberately separate.
// A motor's advertised watts alone do not establish loaded top speed.
export const STOCK_PERFORMANCE = {
  kukiring4: {
    name: 'KuKirin G4',
    nominal: 60,
    ah: 20,
    wh: 1200,
    vehicleMass: 41.5,
    motors: 1,
    ratedMotorW: 2000,
    peakMotorW: 2400,
    wheel: 11,
    advertisedSpeed: 70,
    advertisedRange: 75,
    referenceLoad: 65,
    source: 'https://www.kukirinfactory.com/kukirin-g4-specification',
    note: 'Factory page lists 70 km/h and 75 km at a middle-speed test with a 65 kg load. Regional/restricted variants differ; confirm the exact vehicle.',
  },
};
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
  return e.speed.value === null
    ? 'Not established'
    : (e.speed.kind === 'ceiling' ? '≤' : '') + Math.floor(e.speed.value) + ' km/h';
}
export function speedBasisText(e) {
  return e.speed.basis + (e.dashboard ? ' · Your display: ' + e.dashboard + ' km/h' : '');
}
export function peakPowerText(peak) {
  return peak.value === null
    ? '— kW'
    : (peak.kind === 'ceiling' ? '≤' : peak.kind === 'estimate' ? '≈' : '') +
        (peak.value / 1000).toFixed(1) +
        ' kW';
}
export function peakPowerLabel(peak) {
  return peak.kind === 'factory'
    ? 'FACTORY PEAK REFERENCE'
    : peak.kind === 'ceiling'
      ? 'PEAK OUTPUT · CEILING'
      : 'PEAK MOTOR OUTPUT · ESTIMATE';
}
export function createPerformanceEngine(state) {
  const selected = () => selectParts(state);
  const checks = () => checkCompatibility(state);
  function performanceProfile() {
    if (state.mode !== 'rebuild') return null;
    const name =
      typeof normalizeVehicleName === 'function'
        ? normalizeVehicleName(state.vehicle)
        : String(state.vehicle || '').toLowerCase();
    return STOCK_PERFORMANCE[name.replace(/[^a-z0-9]/g, '')] || null;
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
      Number(state.specs.motorCount || 1) !== profile.motors
    )
      return false;
    return ['Motors', 'Controllers', 'Batteries'].every(
      (c) => !p[c] || (p[c].models?.includes(profile.name) && !p[c].template),
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
      vehicle: stock ? profile.vehicleMass : bike ? 25 : 30,
      cruise: stock ? 40 : bike ? 25 : 30,
      power: '',
      efficiency: 78,
      usable: 80,
      cda: bike ? 0.55 : 0.65,
      rolling: bike ? 0.009 : 0.018,
      wheel: stock ? profile.wheel : bike ? 27.5 : 10,
      rpm: '',
      wind: 0,
      grade: 0,
      stops: 0.5,
      accessory: 10,
      nominalVoltage: '',
      capacityAh: '',
      gpsSpeed: '',
      dashboardSpeed: stock ? OWNER_SPEED_REPORT.kukiring4?.speed || '' : '',
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
      ...performanceInputs(),
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
      motors = numberInput(state.specs.motorCount, 1, 1, 4),
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
    const anyManual = [a.peakMotorW, a.peakControllerA, a.peakBatteryA, a.peakVoltage].some(
      (x) => val(x) > 0,
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
      mass =
        numberInput(a.rider, 80, 1) + numberInput(a.vehicle, stock ? profile.vehicleMass : 30, 1),
      eff = numberInput(a.efficiency, 78, 40, 98) / 100,
      cruise = numberInput(a.cruise, stock ? 40 : 30, 5, 150);
    const selectedNominal = numberInput(p.Batteries?.nominal, 0),
      selectedAh = numberInput(p.Batteries?.ah, 0),
      manualV = numberInput(a.nominalVoltage, 0),
      manualAh = numberInput(a.capacityAh, 0);
    let nominal = 0,
      ah = 0,
      batteryBasis = 'Battery data required';
    if (p.Batteries && selectedNominal && selectedAh) {
      nominal = selectedNominal;
      ah = selectedAh;
      batteryBasis = p.Batteries.template
        ? 'Selected battery template — unverified'
        : 'Selected battery data';
    } else if (manualV && manualAh) {
      nominal = manualV;
      ah = manualAh;
      batteryBasis = 'User-entered battery data';
    } else if (stock) {
      nominal = profile.nominal;
      ah = profile.ah;
      batteryBasis = 'Stock G4 reference: 60V × 20Ah';
    }
    const wh = nominal && ah ? nominal * ah : null,
      usableWh = wh ? (wh * numberInput(a.usable, 80, 1, 100)) / 100 : null;
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
    const enteredPower = numberInput(a.power, 0),
      motors = stock ? profile.motors : numberInput(state.specs.motorCount, 1, 1, 4);
    let mechanical = enteredPower ? enteredPower * motors : null,
      limited = false;
    const amps = [numberInput(state.specs.bms, 0), numberInput(state.specs.batteryLimit, 0)].filter(
      (x) => x > 0,
    );
    if (mechanical && nominal && amps.length) {
      const bounded = nominal * Math.min(...amps) * eff;
      limited = bounded < mechanical;
      mechanical = Math.min(mechanical, bounded);
    }
    let powerCeiling = null;
    if (mechanical) {
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
        if (required * eff > mechanical) hi = m;
        else lo = m;
      }
      powerCeiling = lo * 3.6;
    }
    const rpm = numberInput(a.rpm, 0),
      rpmCeiling = rpm
        ? (rpm * Math.PI * numberInput(a.wheel, 11, 1, 40) * 0.0254 * 60) / 1000
        : null,
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
    else if (stock)
      speed = {
        value: profile.advertisedSpeed,
        basis: 'Factory reference, not a measured result for your scooter',
        kind: 'factory',
      };
    else if (maxSpeed !== null)
      speed = {
        value: maxSpeed,
        basis:
          rpmCeiling !== null
            ? 'No-load wheel RPM / power ceiling; loaded speed unverified'
            : 'Power-based ceiling; winding and gearing unverified',
        kind: 'ceiling',
      };
    const conflicts = checks().filter((i) => i.kind === 'conflict').length;
    return {
      peak: estimatePeakPower(a, p, stock, profile),
      a,
      p,
      profile,
      stock,
      nominal,
      ah,
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
          ? 'Stock G4 reference: ONE rear 2000W motor, 2400W listed instantaneous peak'
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
        ? 'Factory reference (separate tests): 70km/h; 75km middle-speed mileage at 65kg load. ' +
          e.profile.source
        : 'No stock performance reference available.',
      'Trip-energy calibration: ' + (e.calibrated ? 'entered measurement used' : 'not provided'),
      'Inputs: ' + JSON.stringify(e.a),
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
