import { $ } from '../ui/dom.js';
import { getVehicleVisual } from '@voltforge/shared/visuals';
import { CATEGORIES } from '@voltforge/shared/catalog';
import { effectiveMotorCount, vehicleStockProfile } from '@voltforge/shared/stock';
export function createFeature(app) {
  function render() {
    const p = app.selected();
    const profile = app.performanceProfile();
    $('#buildName').textContent = app.state.name;
    const tag = document.createElement('span');
    tag.className = 'tiny-tag';
    tag.textContent = app.state.mode === 'rebuild' ? 'REBUILD' : 'CONCEPT';
    $('#buildName').append(tag);
    $('#buildKind').textContent =
      profile?.electric === false
        ? 'BICYCLE'
        : app.state.type === 'scooter'
          ? 'E-SCOOTER'
          : 'E-BIKE';
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
        ? ' <small>chosen · ' +
          Object.values(app.effectiveParts()).filter((part) => part.stock).length +
          ' stock</small>'
        : ' <small>/ ' + CATEGORIES.length + ' categories</small>');
    app.renderTabs();
    app.renderCatalog();
    $('#referencePhoto').hidden = !visual.reference;
    const motorCount = effectiveMotorCount(app.state);
    // Let a photo-based model with unknown factory specs use its authored mounts.
    const useAuthoredMounts =
      app.state.mode === 'rebuild' &&
      motorCount === 1 &&
      !app.state.specs.motorCountOverride &&
      !vehicleStockProfile(app.state.vehicle)?.motors;
    app.scene.update(
      app.state.type,
      p,
      app.category,
      app.state.vehicle,
      app.state.paint,
      useAuthoredMounts ? undefined : motorCount,
    );
    app.renderPerformance();
  }
  return { render };
}
