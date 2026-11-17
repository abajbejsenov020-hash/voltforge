import { $, esc } from '../ui/dom.js';
import {
  peakPowerText,
  peakPowerLabel,
  speedText,
  speedBasisText,
  approx,
  OWNER_SPEED_REPORT,
} from '@voltforge/shared/performance';
export function createFeature(app) {
  function renderPerformance() {
    const e = app.estimatePerformance();
    $('#estimatedPeak').textContent = peakPowerText(e.peak);
    $('#peakBasis').textContent = e.peak.basis;
    $('#peakMetricLabel').textContent = peakPowerLabel(e.peak);
    $('#stockBaselineBtn').hidden = !e.profile || e.stock;
    $('#estimatedSpeed').textContent = e.speed.value === null ? '— km/h' : speedText(e);
    $('#speedBasis').textContent = speedBasisText(e);
    $('#estimatedRange').textContent = approx(e.range, 'km');
    $('#rangeBasis').textContent = e.range
      ? 'Scenario at ' + e.cruise + ' km/h · ' + e.whPerKm.toFixed(1) + ' Wh/km'
      : 'Enter actual pack voltage and capacity';
    $('#estimatedTime').textContent = approx(e.time ? e.time * 60 : null, 'min');
    $('#speedMetricLabel').textContent =
      e.speed.kind === 'factory'
        ? 'FACTORY SPEED REFERENCE'
        : e.speed.kind === 'gps'
          ? 'REPORTED GPS SPEED'
          : 'SPEED DATA / CEILING';
    $('#rangeCruise').value = String(e.cruise);
    if (!$('#rangeCruise').value) {
      const opt = document.createElement('option');
      opt.value = e.cruise;
      opt.textContent = e.cruise;
      $('#rangeCruise').append(opt);
      $('#rangeCruise').value = String(e.cruise);
    }
    $('#performanceNote').textContent =
      (e.conflicts
        ? 'Compatibility conflicts remain; figures do not establish an operable build. '
        : '') +
      (e.stock
        ? 'Stock G4 reference: one rear 2,000W motor; 60V 20Ah = 1,200Wh. '
        : e.batteryBasis + (e.wh ? ' (' + Math.round(e.wh) + 'Wh). ' : '. ')) +
      'Range is an unvalidated energy scenario at the selected cruising speed, not a top-speed range claim. ' +
      (e.dashboard ? 'Dashboard speed is not GPS-verified ground speed. ' : '') +
      (e.legacy ? 'Old generic performance defaults were reset; confirm assumptions. ' : '') +
      (e.calibrated
        ? 'Trip-energy calibration applied.'
        : 'Add trip energy and distance to calibrate.');
    $('#rangeScenarios').innerHTML = e.scenarios
      .map(
        (s) =>
          '<div><span>' +
          s.kmh +
          ' km/h</span><strong>' +
          approx(s.range, 'km') +
          '</strong></div>',
      )
      .join('');
  }
  function performanceDialog() {
    const e = app.estimatePerformance(),
      a = e.a;
    const inputs = [
      ['rider', 'Rider + cargo mass (kg)', 1, 300, 1],
      ['vehicle', 'Vehicle mass (kg)', 1, 300, 0.1],
      ['cruise', 'Range scenario riding speed (km/h)', 5, 150, 1],
      ['nominalVoltage', 'Actual pack nominal voltage (V), if not selected', 1, 200, 0.1],
      ['capacityAh', 'Actual pack capacity (Ah), if not selected', 1, 300, 0.1],
      ['usable', 'Usable battery including reserve / condition (%)', 1, 100, 1],
      ['efficiency', 'Battery-to-wheel efficiency assumption (%)', 40, 98, 1],
      ['cda', 'Rider + vehicle drag area assumption (m²)', 0.1, 2, 0.01],
      ['rolling', 'Rolling resistance assumption', 0.001, 0.08, 0.001],
      ['wind', 'Headwind (+) / tailwind (−), km/h', -80, 120, 1],
      ['grade', 'Sustained uphill grade (%)', 0, 25, 0.1],
      ['stops', 'Full acceleration/stop cycles per km', 0, 10, 0.1],
      ['accessory', 'Lights and other accessory load (W)', 0, 500, 1],
      ['gpsSpeed', 'Your GPS-confirmed loaded top speed (optional)', 1, 200, 0.1],
      ['dashboardSpeed', 'Your scooter-display top speed (optional)', 1, 250, 0.1],
      ['tripKm', 'Measured trip distance (km, optional)', 0.1, 1000, 0.1],
      ['tripUsedWh', 'Measured battery energy used on that trip (Wh)', 1, 10000, 1],
      ['tripSpeed', 'Average moving speed on that trip (km/h)', 5, 150, 0.1],
      ['peakMotorW', 'Verified peak mechanical output per motor (W, optional)', 1, 200000, 1],
      ['peakVoltage', 'Pack voltage under peak load (V, optional)', 1, 250, 0.1],
      ['peakControllerA', 'Combined controller battery-current limit (A, optional)', 1, 3000, 1],
      ['peakBatteryA', 'Pack burst discharge-current limit (A, optional)', 1, 3000, 1],
      ['peakEfficiency', 'Electrical-to-motor-shaft peak efficiency assumption (%)', 40, 98, 1],
      ['power', 'Verified continuous mechanical W per motor (optional)', 1, 20000, 1],
      ['wheel', 'Actual outer tire diameter (inches)', 1, 40, 0.1],
      ['rpm', 'Wheel no-load RPM at this pack voltage (optional)', 1, 10000, 1],
    ];
    app.detail(
      'Performance references & range scenarios',
      `<div class="performance-result"><div><small>${e.speed.kind === 'factory' ? 'Factory speed reference' : 'Speed result / ceiling'}</small><strong>${esc(speedText(e))}</strong></div><div><small>Range energy scenario at ${e.cruise} km/h</small><strong>${approx(e.range, 'km')}</strong></div></div><p>${esc(speedBasisText(e))}. A display reading does not verify actual ground speed.</p>${e.profile ? `<h3>G4 stock reference — one rear motor</h3><p>One 2,000W rear hub motor, with 2,400W instantaneous peak listed by the factory. The linked current specification lists 41.5kg net mass; confirm your version and edit the mass below. Battery: 60V × 20Ah = 1,200Wh nominal; 11-inch tire. The factory lists 70 km/h and a 75km middle-speed mileage test at 65kg load; these are separate test figures, not a promise of 75km while riding at top speed.</p><p><a href="${e.profile.source}" target="_blank" rel="noopener noreferrer">Factory G4 specification and test context</a></p>` : ''}<div class="issue">${e.conflicts ? 'Resolve compatibility conflicts separately. ' : ''}${e.stock ? 'Using stock G4 reference hardware.' : 'Stock G4 speed and battery defaults do not apply to an unverified modified powertrain.'} ${e.wh ? Math.round(e.wh) + 'Wh nominal, ' + Math.round(e.usableWh) + 'Wh usable under the entered ' + a.usable + '% assumption.' : e.batteryBasis + '.'} Selected battery templates override stock capacity; verify them against the installed pack.</div>${e.profile && !e.stock ? '<p>To compare the original scooter, restore its stock reference. This clears planned motor, controller and battery substitutions from this build.</p><button type="button" class="btn" id="restoreStockPerformance">Use stock G4 reference</button>' : ''}<h3>Peak power after modification</h3><div class="peak-result"><strong>${esc(peakPowerText(e.peak))}</strong><p>${esc(e.peak.basis)}</p>${e.peak.electricalW !== null ? `<p>Available battery-side electrical input ceiling: ${(e.peak.electricalW / 1000).toFixed(1)} kW. Electrical input and mechanical motor output are different quantities.</p>` : ''}</div><p>Estimated combined motor shaft output = the lower of verified motor peak W × motor count, or loaded pack voltage × the lower of battery burst-current and controller battery-current limits × peak efficiency. Use ratings for the same burst duration. Controller phase amps, motor rated watts, battery Ah and advertised controller kW are not interchangeable with these inputs. Incomplete data produces an explicitly labeled ceiling or an unknown result. These burst estimates are separate from the continuous-power speed calculation; gearing trades torque against speed and does not create motor power.</p><h3>Same battery, different riding speeds</h3><table class="range-table"><thead><tr><th>Riding speed</th><th>Modeled consumption</th><th>Range scenario</th></tr></thead><tbody>${e.scenarios.map((s) => `<tr><td>${s.kmh} km/h</td><td>${s.whPerKm.toFixed(1)} Wh/km</td><td>${approx(s.range, 'km')}</td></tr>`).join('')}</tbody></table><p>Energy scenarios assume the entered mass, posture, road, wind and stop frequency. This table does not establish that the vehicle can sustain each speed. Range is not road-tested or fitted to a claimed maximum.</p><h3>Use your actual setup and observations</h3><form id="performanceForm" class="spec-fields"><label>Hardware basis<select name="configuration"><option value="auto" ${a.configuration === 'auto' ? 'selected' : ''}>Automatic — stock reference only if applicable</option><option value="custom" ${a.configuration === 'custom' ? 'selected' : ''}>Modified / custom powertrain</option></select></label>${inputs.map(([key, label, min, max, step]) => `<label>${label}<input name="${key}" type="number" min="${min}" max="${max}" step="${step}" ${['rider', 'vehicle', 'cruise', 'usable', 'efficiency', 'cda', 'rolling', 'wind', 'grade', 'stops', 'accessory', 'wheel'].includes(key) ? 'required' : ''} value="${esc(a[key])}" placeholder="Unknown"></label>`).join('')}<button class="btn primary" type="submit">Save & recalculate</button></form><h3>What changed</h3><p>There is no universal 1,000W scooter assumption and no fixed 15% RPM deduction. Published motor watts are not treated as measured mechanical output. Unknown custom-build top speed stays unknown; optional power and RPM calculations are labeled ceilings, not achievable speeds. Riding speed is never silently reduced to make range look longer.</p><p>Range uses usable pack Wh divided by energy per kilometer: aerodynamic drag, tire rolling resistance, uphill load, battery-to-wheel efficiency, accessory load and acceleration cycles. Regeneration is not assumed. Optional measured trip Wh/km anchors consumption at that trip’s speed; other speeds remain model extrapolations. Weather, battery sag, temperature, wear and motor/controller thermal limits are not fully modeled.</p>`,
    );
    if ($('#restoreStockPerformance'))
      $('#restoreStockPerformance').onclick = () => app.restoreStockPerformance(true);
    $('#performanceForm').onsubmit = (ev) => {
      ev.preventDefault();
      const next = Object.fromEntries(new FormData(ev.currentTarget)),
        tripFields = ['tripKm', 'tripUsedWh', 'tripSpeed'].filter((k) => Number(next[k]) > 0);
      if (tripFields.length && tripFields.length !== 3) {
        app.toast('Enter trip distance, energy used and average speed together to calibrate.');
        return;
      }
      app.state.performance = { ...next, schema: 2 };
      app.save();
      app.renderPerformance();
      app.performanceDialog();
      app.toast('Performance data and scenarios updated');
    };
  }
  function restoreStockPerformance(showDialog = false) {
    const profile = app.performanceProfile();
    if (!profile) return;
    for (const c of ['Motors', 'Controllers', 'Batteries']) delete app.state.selected[c];
    app.state.specs.motorCount = profile.motors;
    app.state.performance = {
      ...app.performanceInputs(),
      configuration: 'auto',
      nominalVoltage: '',
      capacityAh: '',
      vehicle: profile.vehicleMass,
      wheel: profile.wheel,
      power: '',
      rpm: '',
      gpsSpeed: '',
      dashboardSpeed: OWNER_SPEED_REPORT.kukiring4.speed,
      tripKm: '',
      tripUsedWh: '',
      tripSpeed: '',
      peakMotorW: '',
      peakControllerA: '',
      peakBatteryA: '',
      peakVoltage: '',
      schema: 2,
    };
    app.save();
    app.render();
    if (showDialog) app.performanceDialog();
    app.toast('Stock G4 reference restored; planned powertrain substitutions cleared.');
  }
  return { renderPerformance, performanceDialog, restoreStockPerformance };
}
