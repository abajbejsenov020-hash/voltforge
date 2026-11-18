import { esc, $ } from '../ui/dom.js';
import { CATEGORIES, CATALOG } from '@voltforge/shared/catalog';
import { peakPowerLabel, peakPowerText } from '@voltforge/shared/performance';
import { effectiveMotorCount } from '@voltforge/shared/stock';
import { PAINT_ZONES } from '@voltforge/shared/build';
import { factorySummary, componentName } from '../ui/stock.js';
export function createFeature(app) {
  function review({ focusIssues = false } = {}) {
    const p = app.effectiveParts(),
      issues = app.checks(),
      performance = app.estimatePerformance();
    const conflicts = issues.filter((issue) => issue.kind === 'conflict');
    const checks = issues.filter((issue) => issue.kind !== 'conflict');
    const conflictSection = conflicts.length
      ? `<h3 id="reviewConflicts" tabindex="-1">Compatibility conflicts</h3>${conflicts.map((issue) => `<div class="issue conflict">${esc(issue.text)}</div>`).join('')}`
      : '';
    const checkRows = checks
      .map(
        (issue) =>
          `<div class="issue ${issue.kind === 'pass' ? 'pass' : ''}">${issue.kind === 'pass' ? '✓ ' : '○ '}${esc(issue.text)}</div>`,
      )
      .join('');
    app.detail(
      'Your build, at a glance',
      `<p>${esc(app.state.name)} · ${app.state.type === 'scooter' ? 'E-scooter' : 'E-bike'}${app.state.mode === 'rebuild' ? ' · Rebuild of ' + esc(app.state.vehicle) : ''}</p>${conflictSection}${CATEGORIES.map((c) => `<div class="review-row"><div><small>${c}</small><br><strong>${esc(componentName(p[c]))}</strong></div>${p[c] && !p[c].stock ? `<button data-remove="${p[c].id}">${app.state.mode === 'rebuild' ? 'Return to stock' : 'Remove'}</button>` : ''}</div>`).join('')}<h3>${esc(peakPowerLabel(performance.peak))}</h3><div class="peak-result"><strong>${esc(peakPowerText(performance.peak))}</strong><p>${esc(performance.peak.basis)}</p></div><button class="text-btn" id="reviewPeakSetup">Set peak-power inputs →</button>${app.performanceProfile() ? '<p>Factory reference: ' + esc(factorySummary(app.performanceProfile())) + '. Unchanged components remain stock.</p>' : app.state.mode === 'rebuild' ? '<p>Unchanged categories retain factory parts. Add missing ratings in performance setup for this vehicle.</p>' : ''}<h3>Measurements & planned limits</h3><p>Enter values from your actual hardware labels and measurements. These are user-provided, unverified inputs.</p><form id="specForm" class="spec-fields"><label>Measured dropout (mm)<input name="dropout" type="number" min="1" max="500" step="any" value="${esc(app.state.specs.dropout)}" placeholder="Unknown"></label><label>Actual pack full-charge voltage (V)<input name="fullV" type="number" min="1" max="500" step="any" value="${esc(app.state.specs.fullV)}" placeholder="${p.Batteries?.fullV || 'Unknown'}"></label><label>BMS continuous current (A)<input name="bms" type="number" min="1" max="1000" step="any" value="${esc(app.state.specs.bms)}" placeholder="Unknown"></label><label>Planned battery current total (A)<input name="batteryLimit" type="number" min="1" max="1000" step="any" value="${esc(app.state.specs.batteryLimit)}" placeholder="Unknown"></label><label>Driven motors<select name="motorCount"><option value="1" ${effectiveMotorCount(app.state) === 1 ? 'selected' : ''}>1 motor</option><option value="2" ${effectiveMotorCount(app.state) === 2 ? 'selected' : ''}>2 motors</option></select></label><button class="btn primary" type="submit">Save & check</button></form><h3>Compatibility review</h3><p>Rules-based checks on entered data. Passing one check does not establish overall compatibility.</p>${checkRows}<button class="btn" id="reviewExport">Export complete build ↗</button>`,
    );
    if (focusIssues) $('#reviewConflicts')?.focus();
    $('#reviewPeakSetup').onclick = app.performanceDialog;
    $('#specForm').onsubmit = (e) => {
      e.preventDefault();
      const form = new FormData(e.currentTarget);
      const updated = Object.fromEntries(form);
      if (Number(updated.motorCount) !== effectiveMotorCount(app.state))
        app.invalidatePerformanceMeasurements();
      app.state.specs = { ...updated, motorCountOverride: Number(updated.motorCount) };
      app.save();
      app.render();
      $('#assistantText').textContent =
        app.checks().find((i) => i.kind === 'conflict')?.text ||
        app.checks().find((i) => i.kind === 'unknown')?.text ||
        'Review your selected components before building.';
      app.review();
      $('#specForm button').focus();
      app.toast('Measurements saved and checks updated');
    };
    $('#detailBody')
      .querySelectorAll('[data-remove]')
      .forEach(
        (b) =>
          (b.onclick = () => {
            app.togglePart(b.dataset.remove);
            app.review();
          }),
      );
    $('#reviewExport').onclick = app.exportBuild;
  }
  function exportBuild() {
    const p = app.effectiveParts(),
      text = [
        'VOLTMODD — BUILD PLAN',
        app.state.name,
        'Vehicle type: ' + app.state.type,
        'Mode: ' + app.state.mode,
        ...(app.state.vehicle ? ['Vehicle: ' + app.state.vehicle] : []),
        'Saved: ' + new Date().toISOString(),
        '',
        app.state.mode === 'rebuild'
          ? 'EFFECTIVE PARTS — FACTORY PARTS + UPGRADES'
          : 'SELECTED PARTS',
        ...CATEGORIES.map(
          (c) =>
            c +
            ': ' +
            (p[c]
              ? componentName(p[c]) +
                (p[c].detail ? ' | ' + p[c].detail : '') +
                (p[c].reference
                  ? ' | Reference: ' + p[c].reference
                  : p[c].stock
                    ? ' | Factory rating unverified'
                    : ' | Planning template')
              : 'Not selected'),
        ),
        ...(Object.keys(app.state.paint || {}).length
          ? [
              '',
              'PAINT',
              ...Object.entries(app.state.paint).map(
                ([zone, color]) => PAINT_ZONES[zone] + ': ' + color,
              ),
            ]
          : []),
        '',
        'USER-ENTERED MEASUREMENTS',
        ...Object.entries(app.state.specs).map(([k, v]) => k + ': ' + (v || 'Unknown')),
        '',
        'COMPATIBILITY REVIEW',
        ...app.checks().map((i) => i.kind.toUpperCase() + ': ' + i.text),
        '',
        'APPROXIMATE PERFORMANCE',
        ...app.performanceExport(),
        '',
        'This is a planning prototype with illustrative 3D geometry and rules-based checks. It does not provide measured CAD, live product availability or build certification. All supplier revisions, dimensions and component ratings need verification.',
      ].join('\n');
    const url = URL.createObjectURL(new Blob([text], { type: 'text/plain;charset=utf-8' })),
      a = document.createElement('a');
    a.href = url;
    a.download =
      (app.state.name.replace(/[^a-z0-9]+/gi, '-').toLowerCase() || 'voltmodd-build') + '.txt';
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    app.toast('Build plan exported');
  }
  function savedBuilds() {
    app.detail(
      'Your garage',
      app.builds.length
        ? '<p>Builds save on this device and sync to this browser’s private server workspace when connected. Export a portable copy before clearing browser data.</p>' +
            app.builds
              .map(
                (b) =>
                  `<div class="review-row"><div><strong>${esc(b.name)}</strong><br><small>${b.type === 'scooter' ? 'E-scooter' : 'E-bike'} · ${Object.keys(b.selected).length} categories selected</small></div><button class="btn" data-load="${esc(b.id)}">${b.id === app.state.id ? 'Active' : 'Open →'}</button></div>`,
              )
              .join('')
        : '<p>Your saved builds will appear here after you create one.</p>',
    );
    $('#detailBody')
      .querySelectorAll('[data-load]')
      .forEach(
        (b) =>
          (b.onclick = () => {
            app.state = app.builds.find((x) => x.id === b.dataset.load);
            app.state.specs = { ...app.blank().specs, ...app.state.specs };
            app.category = 'Motors';
            $('#search').value = '';
            $('#brand').value = '';
            app.save();
            app.render();
            $('#assistantText').textContent =
              app.checks().find((i) => i.kind === 'conflict')?.text ||
              app.checks().find((i) => i.kind === 'unknown')?.text ||
              'Review your selected components before building.';
            $('#detailDialog').close();
            app.toast('Build opened');
          }),
      );
  }
  function guide() {
    app.detail(
      'From idea to real-world build',
      `<h3>01 · Choose your starting point</h3><p>Select an e-scooter or e-bike. For a rebuild, enter your existing model and verify its year, installed parts and actual specifications.</p><h3>02 · Explore & select parts</h3><p>Use categories, brand filters and search. Rebuilds start with factory parts in every category. Add replaces only that component; Return to stock restores it. Manufacturer entries link to references; custom items are planning templates.</p><h3>03 · Measure & check</h3><p>Open Review build. Record full-charge pack voltage, dropout width, BMS current and planned battery current. Review conflicts and unresolved items. Confirm the exact supplier SKU, axle, mounting and connectors.</p><h3>04 · Keep your plan</h3><p>Builds save locally and sync to this browser’s private workspace while connected. Use My garage to switch projects and Export build to keep a portable copy.</p><div class="issue">The 3D vehicle is an interactive concept, not measured CAD. The assistant uses local rules and catalog search; it is not connected to an AI service.</div>`,
    );
  }
  function ask(question) {
    const q = question.trim().toLowerCase();
    if (!q) return;
    if (/speed|range|ride time|performance/.test(q)) {
      app.performanceDialog();
      $('#assistantText').textContent =
        'The performance panel separates stock references, dashboard readings and GPS results. Range is modeled at your chosen riding speed; enter measured trip energy to calibrate it.';
    } else if (/check|compat|fit|wrong|problem|voltage|battery/.test(q)) {
      $('#assistantText').textContent = app
        .checks()
        .filter((i) => i.kind !== 'pass')
        .map((i) => i.text)
        .slice(0, 2)
        .join(' ');
      if (/battery/.test(q) && !app.effectiveParts().Batteries) {
        app.category = 'Batteries';
        $('#search').value = '';
        $('#brand').value = '';
        app.renderTabs();
        app.renderCatalog();
      }
    } else if (/start|how|help/.test(q))
      $('#assistantText').textContent =
        'Choose a motor, controller and battery from the catalog. Open Review build to enter measurements. The model shows a generic layout; use manufacturer drawings to verify real mounting and clearances.';
    else {
      const query = q
        .replace(/find|show|me|controllers|controller|motors|motor|please/gi, ' ')
        .trim();
      const match = CATALOG.filter((p) =>
        [p.brand, p.name, p.platform]
          .join(' ')
          .toLowerCase()
          .includes(query || q),
      );
      if (match.length) {
        app.category = match[0].category;
        $('#search').value = query || q;
        $('#brand').value = '';
        $('#vehicleFilter').value = 'all';
        app.renderTabs();
        app.renderCatalog();
        $('#assistantText').textContent =
          'I found ' +
          match.length +
          ' catalog matches. The parts panel shows ' +
          app.category.toLowerCase() +
          '. Open Details for the source and unresolved specifications.';
      } else
        $('#assistantText').textContent =
          'I can check your selected parts, explain the workflow, or search the catalog by brand and model. Try “Find VESC controllers” or “What needs checking?” This prototype uses a local spec checker.';
    }
    $('#question').value = '';
  }
  return { review, exportBuild, savedBuilds, guide, ask };
}
