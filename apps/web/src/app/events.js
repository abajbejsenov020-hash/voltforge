import { $, esc } from '../ui/dom.js';
import { reducedMotionEnabled } from '../ui/render-preferences.js';
import { vehicleStockProfile } from '@voltforge/shared/stock';
import {
  canonicalVehicleName,
  VEHICLE_INDEX,
  normalizeVehicleName,
} from '@voltforge/shared/vehicles';

export function bindEvents(app) {
  app.state.specs = { ...app.blank().specs, ...app.state.specs };
  $('#finderBrand').onchange = $('#photoModelsOnly').onchange = () => {
    app.showAllVehicles = false;
    app.vehicleSuggestions();
  };
  $('#browseVehicles').onclick = () => {
    app.showAllVehicles = true;
    app.vehicleSuggestions();
  };
  $('#customVehicle').onclick = () => {
    $('#finderBrand').value = '';
    $('#startBuild').click();
  };
  document.querySelectorAll('[data-type]').forEach((button) => {
    button.onclick = () => {
      const changed = app.setupType !== button.dataset.type;
      if (changed) {
        $('#vehicleName').value = '';
        $('#finderBrand').value = '';
        app.showAllVehicles = false;
      }
      app.setupType = button.dataset.type;
      app.syncSetup({ showBrands: changed });
    };
  });
  document.querySelectorAll('[data-mode]').forEach((button) => {
    button.onclick = () => {
      app.setupMode = button.dataset.mode;
      app.syncSetup();
    };
  });
  $('#vehicleName').oninput = () => {
    app.showAllVehicles = false;
    app.vehicleSuggestions();
  };
  $('#startBuild').onclick = () => {
    let vehicle = canonicalVehicleName($('#vehicleName').value.trim());
    if (app.setupMode === 'rebuild') {
      const exact = VEHICLE_INDEX.find(
        (entry) => normalizeVehicleName(entry.name) === normalizeVehicleName(vehicle),
      );
      if (exact) {
        vehicle = exact.name;
        app.setupType = exact.type;
      }
      if (!vehicle) {
        $('#vehicleName').focus();
        $('#vehicleNote').textContent = 'Enter your vehicle’s name to start rebuilding.';
        return;
      }
    }
    const name =
      app.setupMode === 'rebuild'
        ? `${vehicle} rebuild`
        : $('#projectName').value.trim() ||
          `My ${app.setupType === 'scooter' ? 'e-scooter' : 'e-bike'} build`;
    if (app.editMode) {
      if (app.state.type !== app.setupType) {
        app.state.selected = {};
        delete app.state.cockpit;
        app.state.specs = app.blank().specs;
      }
      if (app.state.vehicle !== vehicle || app.state.type !== app.setupType)
        app.invalidatePerformanceMeasurements('vehicle');
      app.state.type = app.setupType;
      app.state.name = name;
    } else app.state = app.blank(app.setupType, name);
    const vehicleChanged = app.state.vehicle !== vehicle || app.state.mode !== app.setupMode;
    app.state.mode = app.setupMode;
    app.state.vehicle = app.setupMode === 'rebuild' ? vehicle : '';
    if (!app.editMode || vehicleChanged) {
      delete app.state.cockpit;
      app.state.specs.motorCount = vehicleStockProfile(app.state.vehicle)?.motors || 1;
      delete app.state.specs.motorCountOverride;
    }
    app.category = 'Motors';
    $('#search').value = '';
    $('#brand').value = '';
    $('#vehicleFilter').value = 'current';
    app.save();
    app.render();
    $('#startDialog').close();
    $('#assistantText').textContent =
      app.setupMode === 'rebuild'
        ? `Your ${vehicle} rebuild starts with factory parts. Choose only the components you want to change; unchanged parts stay stock and estimates update automatically.`
        : 'Start with a motor or controller. Add a battery next, then open Review build to record your measurements.';
    app.toast(app.editMode ? 'Build details updated' : 'Welcome to your workshop');
  };
  $('#referencePhoto').onclick = () => {
    const ref = app.scene.getReference();
    if (ref)
      app.detail(
        `${ref.name} — original appearance`,
        `<img src="${esc(ref.image)}" alt="${esc(ref.name)}" class="detail-vehicle-photo"><p>${esc(ref.variantNote || 'Original model reference. Confirm your year and variant.')}</p><p>Selected modifications are recorded in your build. This image shows the reference vehicle.</p><p><a href="${esc(ref.source)}" target="_blank" rel="noopener noreferrer">${esc(ref.credit)} · original source ↗</a></p>`,
      );
  };
  $('#projectName').oninput = app.renderSelection;
  $('#categorySelect').onchange = (event) => {
    app.category = event.target.value;
    $('#search').value = '';
    $('#brand').value = '';
    app.renderTabs();
    app.renderCatalog();
  };
  $('#stockBaselineBtn').onclick = () => app.restoreStockPerformance(false);
  $('#rangeCruise').onchange = (event) => {
    app.state.performance = {
      ...app.state.performance,
      cruise: Number(event.target.value),
      schema: 2,
    };
    app.save();
    app.renderPerformance();
  };
  $('#tunePerformance').onclick = app.performanceDialog;
  $('#askForm').onsubmit = (event) => {
    event.preventDefault();
    app.ask($('#question').value);
  };
  document.querySelectorAll('[data-ask]').forEach((button) => {
    button.onclick = () => app.ask(button.dataset.ask);
  });
  for (const id of ['search', 'brand', 'appearanceFilter', 'vehicleFilter']) {
    $(`#${id}`)[id === 'search' ? 'oninput' : 'onchange'] = app.renderCatalog;
  }
  $('#newBuild').onclick = () => app.openStart();
  $('#editBuild').onclick = () => app.openStart(true);
  $('#studioNav').onclick = () =>
    window.scrollTo({ top: 0, behavior: reducedMotionEnabled() ? 'auto' : 'smooth' });
  $('#savedNav').onclick = app.savedBuilds;
  $('#guideNav').onclick = $('#about').onclick = app.guide;
  $('#reviewBuild').onclick = app.review;
  $('#exportBuild').onclick = app.exportBuild;
  $('#closeDetail').onclick = () => $('#detailDialog').close();
  $('#vehicleName').onkeydown = (event) => {
    const buttons = [...$('#vehicleSuggestions').querySelectorAll('button')];
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault();
      if (!buttons.length) return;
      const direction = event.key === 'ArrowDown' ? 1 : -1;
      const previous = app.activeVehicleSuggestion;
      app.activeVehicleSuggestion =
        previous < 0
          ? direction > 0
            ? 0
            : buttons.length - 1
          : (previous + direction + buttons.length) % buttons.length;
      buttons.forEach((button, index) =>
        button.classList.toggle('keyboard-active', index === app.activeVehicleSuggestion),
      );
      const active = buttons[app.activeVehicleSuggestion];
      $('#vehicleKeyboardStatus').textContent =
        `${active.dataset.vehicle}, result ${app.activeVehicleSuggestion + 1} of ${buttons.length}`;
      active.scrollIntoView({ block: 'nearest' });
    }
    if (event.key === 'Enter') {
      event.preventDefault();
      if (buttons.length) {
        buttons[Math.max(0, app.activeVehicleSuggestion)].click();
      } else $('#startBuild').click();
    }
  };
  $('#projectName').onkeydown = (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      $('#startBuild').click();
    }
  };
  app.render();
  if (app.isFirst) app.openStart();
}
