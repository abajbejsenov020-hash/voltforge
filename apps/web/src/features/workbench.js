import { $ } from '../ui/dom.js';
import { getVehicleVisual } from '@voltforge/shared/visuals';
import { CATEGORIES } from '@voltforge/shared/catalog';
export function createFeature(app) {
  function render() {
    const p = app.selected();
    $('#buildName').textContent = app.state.name;
    const tag = document.createElement('span');
    tag.className = 'tiny-tag';
    tag.textContent = app.state.mode === 'rebuild' ? 'REBUILD' : 'CONCEPT';
    $('#buildName').append(tag);
    $('#buildKind').textContent = app.state.type === 'scooter' ? 'E-SCOOTER' : 'E-BIKE';
    $('#buildSubtitle').textContent =
      app.state.mode === 'rebuild'
        ? 'Starting from ' + app.state.vehicle + ' · Confirm your exact model and measurements.'
        : 'Your ideas. Real parts. One place to bring them together.';
    const visual = getVehicleVisual(app.state.vehicle, app.state.type);
    $('#modelLabel').textContent =
      app.state.mode === 'rebuild' ? visual.name + ' · ' + visual.fidelity : 'Custom concept model';
    const upgrades = Object.keys(p).length;
    $('#partCount').previousElementSibling.textContent =
      app.state.mode === 'rebuild' ? 'CHOSEN REPLACEMENTS' : 'SELECTED PARTS';
    $('#partCount').innerHTML =
      upgrades +
      (app.state.mode === 'rebuild'
        ? ' <small>chosen · ' + (CATEGORIES.length - upgrades) + ' stock</small>'
        : ' <small>/ ' + CATEGORIES.length + ' categories</small>');
    const perf = app.estimatePerformance();
    $('#energy').innerHTML = (perf.wh ? Math.round(perf.wh) : '—') + ' <small>Wh nominal</small>';
    const count = app.checks().filter((i) => i.kind === 'conflict').length;
    $('#checkSummary').textContent = count
      ? count + ' conflict' + (count > 1 ? 's' : '')
      : 'Needs verification';
    $('#checkSummary').style.color = count ? '#b06c45' : '';
    app.renderTabs();
    app.renderCatalog();
    $('#referencePhoto').hidden = !visual.reference;
    app.scene.update(app.state.type, p, app.category, app.state.vehicle);
    app.renderPerformance();
  }
  return { render };
}
