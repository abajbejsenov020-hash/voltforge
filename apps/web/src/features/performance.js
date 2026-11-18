import { $, esc } from '../ui/dom.js';
import { factorySummary } from '../ui/stock.js';
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
    const energy = $('#energy');
    energy.firstChild.textContent = (e.wh ? Math.round(e.wh) : '—') + ' ';
    const check = $('#checkSummary');
    check.textContent = e.conflicts
      ? e.conflicts + (e.conflicts === 1 ? ' conflict' : ' conflicts')
      : 'Needs verification';
    check.classList.toggle('has-conflicts', Boolean(e.conflicts));
    $('#performanceConflict').hidden = !e.conflicts;
    if (e.conflicts) {
      const firstConflict = app.checks().find((issue) => issue.kind === 'conflict');
      $('#performanceConflictText').textContent = 'Conditional estimates · ' + firstConflict.text;
    }
    $('#reviewPerformanceConflicts').onclick = () => app.review({ focusIssues: true });
    $('#estimatedPeak').textContent = peakPowerText(e.peak);
    $('#peakBasis').textContent = e.peak.basis;
    $('#peakMetricLabel').textContent = peakPowerLabel(e.peak);
    $('#stockBaselineBtn').hidden = !e.profile || e.stock;
    const hardwareNote = $('#stockHardwareNote');
    hardwareNote.hidden = app.state.mode !== 'rebuild';
    if (!hardwareNote.hidden) {
      const labels = { Motors: 'motor', Controllers: 'controller', Batteries: 'battery' };
      const stock = Object.keys(labels)
        .filter((c) => e.p[c]?.stock)
        .map((c) => labels[c]);
      const equivalent = Object.keys(labels)
        .filter((c) => e.p[c]?.stockEquivalent)
        .map((c) => labels[c]);
      const changed = Object.keys(labels)
        .filter((c) => e.p[c] && !e.p[c].stock && !e.p[c].stockEquivalent)
        .map((c) => labels[c]);
      hardwareNote.textContent =
        (stock.length ? 'Stock: ' + stock.join(', ') + '. ' : '') +
        (equivalent.length
          ? 'Factory-equivalent replacement: ' + equivalent.join(', ') + '. '
          : '') +
        (changed.length ? 'Upgraded: ' + changed.join(', ') + '. ' : '') +
        'Unchanged categories retain their factory parts.';
    }
    const missingPower = e.automatic.missing.includes('power');
    const speedUnknown = e.speed.value === null;
    $('#estimatedSpeed').textContent = speedText(e);
    $('#estimatedSpeed').classList.toggle('metric-unavailable', speedUnknown);
    $('#speedBasis').textContent =
      speedUnknown && missingPower
        ? 'Add the motor’s continuous shaft output to estimate top speed.'
        : speedBasisText(e);
    const speedAction = $('#addSpeedData');
    speedAction.hidden = !speedUnknown;
    speedAction.textContent = missingPower ? 'Add motor rating →' : 'Add speed data →';
    speedAction.onclick = () => {
      const missing = e.automatic.missing[0];
      if (missing) focusRating(missing);
      else app.performanceDialog();
    };
    const peakAction = $('#addPeakData');
    peakAction.hidden = !e.automatic.enabled || !e.peak.missing.includes('motor peak output');
    peakAction.onclick = () => focusRating('peakMotorW');
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
          : e.speed.kind === 'planning'
            ? 'TOP SPEED · ROUGH ESTIMATE'
            : speedUnknown
              ? 'TOP SPEED'
              : 'TOP SPEED · CEILING';
    $('#rangeCruise').value = String(e.cruise);
    if (!$('#rangeCruise').value) {
      const opt = document.createElement('option');
      opt.value = e.cruise;
      opt.textContent = e.cruise;
      $('#rangeCruise').append(opt);
      $('#rangeCruise').value = String(e.cruise);
    }
    $('#performanceNote').textContent =
      (e.stock
        ? factorySummary(e.profile) + '. '
        : e.batteryBasis + (e.wh ? ' (' + Math.round(e.wh) + 'Wh). ' : '. ')) +
      (!e.profile?.vehicleMass && !Number(app.state.performance?.vehicle)
        ? 'Vehicle mass assumed at ' + e.a.vehicle + ' kg until confirmed. '
        : '') +
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
    renderAutomaticInputs(e);
  }
  function focusRating(key) {
    const field = $('#quickPerformanceForm')?.elements.namedItem(key);
    if (!field) return app.performanceDialog();
    field.closest('details').open = true;
    field.focus();
    field.scrollIntoView({ block: 'center' });
  }
  function renderAutomaticInputs(e) {
    const container = $('#automaticPerformance');
    container.hidden = !e.automatic.enabled;
    if (!e.automatic.enabled) {
      container.innerHTML = '';
      return;
    }
    const wasOpen = container.querySelector('details')?.open;
    const fields = [
      ['power', 'Motor output per motor (W)', e.automatic.inputs.power],
      ['bms', 'Battery continuous current (A)', e.automatic.continuousA],
      ['peakBatteryA', 'Battery burst current (A)', e.automatic.inputs.peakBatteryA],
      ['peakControllerA', 'Controller battery current (A)', e.automatic.inputs.peakControllerA],
      ['peakMotorW', 'Peak shaft output per motor (W)', e.automatic.inputs.peakMotorW],
      ['peakVoltage', 'Pack voltage under load (V)', e.automatic.inputs.peakVoltage],
    ];
    if (e.automatic.missing.includes('nominalVoltage'))
      fields.unshift(['nominalVoltage', 'Pack nominal voltage (V)', '']);
    if (e.automatic.equivalentAh || e.automatic.missing.includes('capacityAh'))
      fields.unshift(['capacityAh', 'Pack capacity (Ah)', e.automatic.equivalentAh || '']);
    const value = (key) =>
      key === 'bms' ? app.state.specs.bms : (app.state.performance?.[key] ?? '');
    container.innerHTML = `<p class="automatic-note">${
      e.automatic.missing.length
        ? 'Enter the required ratings to calculate the missing estimates.'
        : e.speed.kind === 'planning' || e.peak.kind === 'planning'
          ? 'Calculated automatically from your parts. These are planning scenarios; battery limits and winding may change the result.'
          : 'Your entered limits refine the selected-part calculation.'
    }</p>
      <details class="estimate-inputs" ${wasOpen || e.automatic.missing.length ? 'open' : ''}>
        <summary>Assumptions & quick inputs${e.automatic.missing.length ? ' · ratings needed' : ''}</summary>
        <p>Leave optional fields blank to use catalog values and planning assumptions.</p>
        <form id="quickPerformanceForm" class="spec-fields">${fields.map(([key, label, automatic]) => `<label>${esc(label)}${e.automatic.missing.includes(key) ? ' · required' : ''}<input name="${key}" type="number" min="0.1" max="${/power|peakMotorW/.test(key) ? 200000 : key === 'capacityAh' ? 300 : key === 'peakVoltage' || key === 'nominalVoltage' ? 500 : 3000}" step="any" value="${esc(value(key))}" placeholder="${Number(automatic) > 0 ? 'Automatic: ' + Number(Number(automatic).toFixed(1)) : 'Enter rating'}" ${e.automatic.missing.includes(key) ? 'required' : ''}></label>`).join('')}
          <button class="btn primary" type="submit">Update estimates</button>
        </form>
        ${e.automatic.assumptions.length ? `<ul class="estimate-assumptions">${e.automatic.assumptions.map((text) => `<li>${esc(text)}</li>`).join('')}</ul>` : ''}
        ${e.automatic.sources.length ? `<div class="estimate-sources"><span>Rating sources</span>${e.automatic.sources.map((source, index) => `<a href="${esc(source.url)}" target="_blank" rel="noopener noreferrer" title="${esc(source.note)}">Manufacturer reference ${index + 1} ↗</a>`).join('')}</div>` : ''}
      </details>`;
    $('#quickPerformanceForm').onsubmit = (event) => {
      event.preventDefault();
      const { bms, ...values } = Object.fromEntries(new FormData(event.currentTarget));
      app.state.specs.bms = bms;
      app.state.performance = { ...app.state.performance, ...values, schema: 2 };
      app.save();
      app.renderPerformance();
      $('#quickPerformanceForm button').focus();
      app.toast('Performance inputs saved');
    };
  }
  function performanceDialog() {
    const e = app.estimatePerformance(),
      a = e.a;
    const inputs = [
      ['rider', 'Rider + cargo mass (kg)', 1, 300, 1],
      ['vehicle', 'Vehicle mass (kg)', 1, 300, 0.1],
      ['cruise', 'Range scenario riding speed (km/h)', 5, 150, 1],
      ['nominalVoltage', 'Actual pack nominal voltage (V), if not selected', 1, 500, 0.1],
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
      ['peakVoltage', 'Pack voltage under peak load (V, optional)', 1, 500, 0.1],
      ['peakControllerA', 'Combined controller battery-current limit (A, optional)', 1, 3000, 1],
      ['peakBatteryA', 'Pack burst discharge-current limit (A, optional)', 1, 3000, 1],
      ['peakEfficiency', 'Electrical-to-motor-shaft peak efficiency assumption (%)', 40, 98, 1],
      ['power', 'Verified continuous mechanical W per motor (optional)', 1, 200000, 1],
      ['wheel', 'Actual outer tire diameter (inches)', 1, 40, 0.1],
      ['rpm', 'Wheel no-load RPM at this pack voltage (optional)', 1, 10000, 1],
    ];
    app.detail(
      'Performance references & range scenarios',
      `<div class="performance-result"><div><small>${e.speed.kind === 'factory' ? 'Factory speed reference' : e.speed.kind === 'planning' ? 'Rough top-speed estimate' : 'Speed result / ceiling'}</small><strong>${esc(speedText(e))}</strong></div><div><small>Range energy scenario at ${e.cruise} km/h</small><strong>${approx(e.range, 'km')}</strong></div></div><p>${esc(speedBasisText(e))}. A display reading does not verify actual ground speed.</p>${e.profile ? `<h3>${esc(e.profile.name)} factory reference</h3><p>${esc(factorySummary(e.profile))}</p><p>${esc(e.profile.note || '')}</p>${e.profile.source ? `<p><a href="${esc(e.profile.source)}" target="_blank" rel="noopener noreferrer">Factory specifications and version details</a></p>` : ''}` : ''}<div class="issue">${e.conflicts ? 'Resolve compatibility conflicts separately. ' : ''}${app.state.mode === 'rebuild' ? 'Unchanged components retain the factory hardware. Selected upgrades override only their own category. ' : ''}${e.wh ? Math.round(e.wh) + 'Wh nominal, ' + Math.round(e.usableWh) + 'Wh usable under the entered ' + a.usable + '% assumption.' : e.batteryBasis + '.'}</div>${e.profile && !e.stock ? '<p>Restore the factory motor, controller and battery to compare the original vehicle. Other modifications remain selected.</p><button type="button" class="btn" id="restoreStockPerformance">Restore stock powertrain</button>' : ''}<h3>Peak power after modification</h3><div class="peak-result"><strong>${esc(peakPowerText(e.peak))}</strong><p>${esc(e.peak.basis)}</p>${e.peak.electricalW !== null ? `<p>Available battery-side electrical input ceiling: ${(e.peak.electricalW / 1000).toFixed(1)} kW. Electrical input and mechanical motor output are different quantities.</p>` : ''}</div><p>Estimated combined motor shaft output = the lower of verified motor peak W × motor count, or loaded pack voltage × the lower of battery burst-current and controller battery-current limits × peak efficiency. Use ratings for the same burst duration. Controller phase amps, motor rated watts, battery Ah and advertised controller kW are not interchangeable with these inputs. Manufacturer ratings populate the automatic scenario. Unknown discharge limits, loaded voltage and motor burst output use visible planning assumptions that can be overridden. Without a motor rating, only a partial ceiling can be shown. These burst estimates are separate from the continuous-power speed calculation; gearing trades torque against speed and does not create motor power.</p><h3>Same battery, different riding speeds</h3><table class="range-table"><thead><tr><th>Riding speed</th><th>Modeled consumption</th><th>Range scenario</th></tr></thead><tbody>${e.scenarios.map((s) => `<tr><td>${s.kmh} km/h</td><td>${s.whPerKm.toFixed(1)} Wh/km</td><td>${approx(s.range, 'km')}</td></tr>`).join('')}</tbody></table><p>Energy scenarios assume the entered mass, posture, road, wind and stop frequency. This table does not establish that the vehicle can sustain each speed. Range is not road-tested or fitted to a claimed maximum.</p><h3>Use your actual setup and observations</h3><form id="performanceForm" class="spec-fields"><label>Hardware basis<select name="configuration"><option value="auto" ${a.configuration === 'auto' ? 'selected' : ''}>Automatic — selected parts and stock references</option><option value="custom" ${a.configuration === 'custom' ? 'selected' : ''}>Modified / custom powertrain</option></select></label>${inputs.map(([key, label, min, max, step]) => `<label>${label}<input name="${key}" type="number" min="${min}" max="${max}" step="${['vehicle', 'wheel'].includes(key) ? 'any' : step}" ${['rider', 'vehicle', 'cruise', 'usable', 'efficiency', 'cda', 'rolling', 'wind', 'grade', 'stops', 'accessory'].includes(key) ? 'required' : ''} value="${esc(a[key])}" placeholder="Unknown"></label>`).join('')}<button class="btn primary" type="submit">Save & recalculate</button></form><h3>What changed</h3><p>There is no universal 1,000W scooter assumption and no fixed 15% RPM deduction. Published motor watts are not treated as measured mechanical output. Rebuild estimates combine each chosen upgrade with the remaining factory components. New builds require a motor, controller and battery. Planning estimates use available ratings; unknown specifications remain visible. Missing motor or pack ratings are requested inline. Catalog watts, assumed battery discharge, voltage sag and motor burst output are displayed separately from user measurements; winding and gearing can reduce actual speed. Riding speed is never silently reduced to make range look longer.</p><p>Range uses usable pack Wh divided by energy per kilometer: aerodynamic drag, tire rolling resistance, uphill load, battery-to-wheel efficiency, accessory load and acceleration cycles. Regeneration is not assumed. Optional measured trip Wh/km anchors consumption at that trip’s speed; other speeds remain model extrapolations. Weather, battery sag, temperature, wear and motor/controller thermal limits are not fully modeled.</p>`,
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
    app.state.specs.motorCount = profile.motors || 1;
    delete app.state.specs.motorCountOverride;
    app.state.specs.fullV = '';
    app.state.specs.bms = '';
    app.state.specs.batteryLimit = '';
    app.state.performance = {
      ...(app.state.performance || {}),
      configuration: 'auto',
      nominalVoltage: '',
      capacityAh: '',
      vehicle: profile.vehicleMass || '',
      wheel: profile.wheel || '',
      power: '',
      rpm: '',
      gpsSpeed: '',
      dashboardSpeed: profile.name === 'KuKirin G4' ? OWNER_SPEED_REPORT.kukiring4.speed : '',
      tripKm: '',
      tripUsedWh: '',
      tripSpeed: '',
      peakMotorW: '',
      peakControllerA: '',
      peakBatteryA: '',
      peakVoltage: '',
      schema: 2,
    };
    delete app.state.performance.vehicle;
    delete app.state.performance.wheel;
    app.save();
    app.render();
    if (showDialog) app.performanceDialog();
    app.toast('Factory motor, controller and battery restored.');
  }
  return { renderPerformance, performanceDialog, restoreStockPerformance };
}
