import { $, esc } from '../ui/dom.js';
import { VEHICLE_INDEX, normalizeVehicleName, findVehicles } from '@voltforge/shared/vehicles';
import {
  vehicleReference,
  VEHICLE_REFERENCES,
  featuredVehicles,
  vehicleArtworkAudit,
} from '../data/vehicle-library.js';

export function createFeature(app) {
  function openStart(edit = false) {
    $('#librarySize').textContent =
      `${VEHICLE_REFERENCES.length} pictured · ${VEHICLE_INDEX.length} indexed models`;
    app.editMode = edit;
    app.showAllVehicles = false;
    $('#finderBrand').innerHTML =
      '<option value="">All vehicle brands</option>' +
      [...new Set(VEHICLE_INDEX.map((v) => v.brand))]
        .sort()
        .map((brand) => `<option>${esc(brand)}</option>`)
        .join('');
    app.setupType = edit ? app.state.type : 'scooter';
    app.setupMode = edit ? app.state.mode : 'rebuild';
    $('#projectName').value = edit ? app.state.name : '';
    $('#vehicleName').value = edit ? app.state.vehicle : '';
    $('#photoModelsOnly').checked = false;
    syncSetup();
    $('#modelFinder').open = false;
    $('#startDialog').showModal();
  }
  function renderFeatured() {
    const shortcuts = $('#emotoBrands');
    shortcuts.hidden = app.setupType !== 'bike';
    shortcuts.innerHTML = ['Sur-Ron', 'Talaria', 'Arctic Leopard', 'Stark', 'E Ride Pro', 'Altis']
      .map(
        (brand) =>
          `<button type="button" data-emoto-brand="${esc(brand)}">${esc(brand)} <span>${VEHICLE_INDEX.filter((v) => v.brand === brand).length} models</span></button>`,
      )
      .join('');
    shortcuts.querySelectorAll('button').forEach((button) => {
      button.onclick = () => {
        $('#finderBrand').value = button.dataset.emotoBrand;
        $('#vehicleName').value = '';
        app.showAllVehicles = true;
        $('#modelFinder').open = true;
        vehicleSuggestions();
        $('#vehicleName').focus();
      };
    });
    const current = normalizeVehicleName($('#vehicleName').value);
    $('#featuredModels').innerHTML = featuredVehicles(app.setupType)
      .map((v) => {
        const indexed = VEHICLE_INDEX.find((entry) => entry.name === v.name);
        const brand = indexed?.brand || v.name.split(' ')[0],
          model = v.name.slice(brand.length).trim();
        const chosen = normalizeVehicleName(v.name) === current;
        return `<button class="featured-model ${chosen ? 'chosen' : ''}" aria-pressed="${chosen}" data-featured="${esc(v.name)}" data-featured-type="${v.type}"><img class="featured-photo" src="${v.image}" alt="${esc(v.name)}" width="600" height="600"><span class="featured-info"><span class="featured-brand">${esc(brand)}</span><span class="featured-name">${esc(model)}</span><span class="featured-action">${chosen ? 'Selected' : 'Select model'}</span></span></button>`;
      })
      .join('');
    $('#featuredModels')
      .querySelectorAll('button')
      .forEach((button) => {
        button.onclick = () => chooseVehicle(button.dataset.featured, button.dataset.featuredType);
      });
    const name = $('#vehicleName').value.trim();
    $('#selectionLabel').textContent =
      app.setupMode === 'new'
        ? $('#projectName').value.trim() ||
          `New ${app.setupType === 'bike' ? 'e-bike' : 'e-scooter'} build`
        : name || 'Select a model to continue';
    $('#startBuild').disabled = app.setupMode === 'rebuild' && !name;
    $('#selectionNote').textContent =
      app.setupMode === 'new'
        ? 'Configure a vehicle from a generic starting layout.'
        : vehicleReference(name)
          ? 'Original model reference included. Check your year and variant.'
          : vehicleArtworkAudit(name)
            ? 'Source audit: ' +
              vehicleArtworkAudit(name).reason +
              ' A labeled concept remains available.'
            : 'This name has no verified image yet. A clearly labeled concept view is available.';
  }
  function syncSetup() {
    document.querySelectorAll('[data-type]').forEach((button) => {
      button.classList.toggle('chosen', button.dataset.type === app.setupType);
      button.setAttribute('aria-pressed', button.dataset.type === app.setupType);
    });
    document.querySelectorAll('[data-mode]').forEach((button) => {
      button.classList.toggle('chosen', button.dataset.mode === app.setupMode);
    });
    for (const id of ['existingFields', 'modelFinder', 'featuredSection'])
      $(`#${id}`).hidden = app.setupMode !== 'rebuild';
    $('#newFields').hidden = app.setupMode !== 'new';
    $('#setupHeading').textContent =
      app.setupMode === 'rebuild' ? 'Start with your ride.' : 'Build something your own.';
    $('#setupDescription').textContent =
      app.setupMode === 'rebuild'
        ? 'Choose the vehicle you own. Make the next version yours.'
        : 'Choose a platform, name your project and start with the components.';
    vehicleSuggestions();
  }
  function vehicleSuggestions() {
    const query = $('#vehicleName').value.trim(),
      brand = $('#finderBrand').value;
    const allMatches = findVehicles(query, { type: app.setupType, brand, saved: app.builds });
    const photosOnly = $('#photoModelsOnly').checked;
    const matches = photosOnly ? allMatches.filter((v) => vehicleReference(v.name)) : allMatches;
    const shown = app.showAllVehicles ? matches : matches.slice(0, query ? 8 : 6);
    app.activeVehicleSuggestion = -1;
    $('#vehicleMatchCount').textContent =
      `${matches.length} ${photosOnly ? 'pictured models' : 'matches'}`;
    $('#vehicleSuggestions').innerHTML =
      shown
        .map((v) => {
          const ref = vehicleReference(v.name);
          return `<button type="button" data-vehicle="${esc(v.name)}" data-vehicle-type="${v.type}">${ref ? `<img src="${ref.image}" alt="" loading="lazy" width="88" height="72">` : '<span class="finder-no-photo" aria-hidden="true">—</span>'}<span class="finder-copy"><span>${esc(v.name)}</span><small>${ref ? 'Original product reference' : v.custom ? 'Saved custom name · no reference' : 'Indexed model · no verified image'}</small></span></button>`;
        })
        .join('') +
      (!matches.length
        ? `<p class="finder-empty">${photosOnly && allMatches.length ? 'This model has no verified image yet. Turn off “With product images” to select it from the complete index.' : 'No indexed match. Try the model or brand name, or use a custom name below.'}</p>`
        : '');
    $('#vehicleSuggestions')
      .querySelectorAll('button')
      .forEach((button) => {
        button.onclick = () => chooseVehicle(button.dataset.vehicle, button.dataset.vehicleType);
      });
    $('#browseVehicles').hidden = app.showAllVehicles || matches.length <= shown.length;
    $('#browseVehicles').textContent =
      `Show all ${matches.length} ${photosOnly ? 'pictured models' : 'matches'}`;
    const exact = allMatches.some(
      (v) =>
        normalizeVehicleName(v.name).replace(/ /g, '') ===
        normalizeVehicleName(query).replace(/ /g, ''),
    );
    $('#customVehicle').hidden = !query || exact;
    $('#customVehicle').textContent = `Use “${query}” as a custom name`;
    $('#vehicleNote').textContent =
      'Search supports model aliases and spacing variations. Product images show the original vehicle; variants and installed parts can differ.';
    renderFeatured();
  }
  function chooseVehicle(name, type) {
    $('#vehicleName').value = name;
    app.setupType = type;
    app.showAllVehicles = false;
    syncSetup();
    $('#vehicleNote').textContent =
      `Selected ${name}. Confirm your model year, version and installed parts.`;
  }
  return { openStart, renderFeatured, syncSetup, vehicleSuggestions, chooseVehicle };
}
