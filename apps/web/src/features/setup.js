import { $, esc } from '../ui/dom.js';
import {
  VEHICLE_INDEX,
  canonicalVehicleName,
  normalizeVehicleName,
  findVehicles,
} from '@voltforge/shared/vehicles';
import { vehicleReference, featuredBrands, vehicleArtworkAudit } from '../data/vehicle-library.js';

export function createFeature(app) {
  let renderedBrandType;

  function openStart(edit = false) {
    app.editMode = edit;
    app.showAllVehicles = false;
    app.setupType = edit ? app.state.type : 'scooter';
    app.setupMode = edit ? app.state.mode : 'rebuild';
    $('#finderBrand').value = '';
    $('#projectName').value = edit ? app.state.name : '';
    $('#vehicleName').value = edit ? app.state.vehicle : '';
    $('#photoModelsOnly').checked = false;
    $('#modelFinder').hidden = !edit;
    syncSetup();
    $('#startDialog').showModal();
  }

  function renderBrands() {
    if (renderedBrandType === app.setupType) return;
    renderedBrandType = app.setupType;
    const brands = featuredBrands(app.setupType);
    const previousBrand = $('#finderBrand').value;
    $('#finderBrand').innerHTML =
      '<option value="">All vehicle brands</option>' +
      brands
        .map(({ brand }) => brand)
        .sort((a, b) => a.localeCompare(b))
        .map((brand) => `<option>${esc(brand)}</option>`)
        .join('');
    $('#finderBrand').value = brands.some(({ brand }) => brand === previousBrand)
      ? previousBrand
      : '';
    $('#featuredModels').innerHTML = brands
      .map(({ brand, reference }, index) => {
        const caption = reference?.name.startsWith(`${brand} `)
          ? reference.name.slice(brand.length + 1)
          : reference?.name;
        const photo = reference
          ? `<img class="featured-photo" src="${esc(reference.image)}" alt="" loading="${index < 4 ? 'eager' : 'lazy'}" width="600" height="450">`
          : '';
        return `<button type="button" class="featured-model" data-featured-brand="${esc(brand)}">${photo}<span class="featured-info"><span class="featured-name">${esc(brand)}</span>${caption ? `<span class="featured-caption">${esc(caption)}</span>` : ''}</span></button>`;
      })
      .join('');
  }

  function openModelFinder(brand = '') {
    $('#finderBrand').value = brand;
    if (brand) $('#vehicleName').value = '';
    $('#photoModelsOnly').checked = false;
    $('#modelFinder').hidden = false;
    app.showAllVehicles = Boolean(brand);
    vehicleSuggestions();
    $('#vehicleName').focus();
  }

  $('#featuredModels').onclick = (event) => {
    const button = event.target.closest('[data-featured-brand]');
    if (button) openModelFinder(button.dataset.featuredBrand);
  };
  $('#browseModelLibrary').onclick = () => {
    if ($('#modelFinder').hidden) openModelFinder();
    else {
      $('#modelFinder').hidden = true;
      renderSelection();
    }
  };

  function renderSelection() {
    const finderOpen = !$('#modelFinder').hidden;
    const brand = $('#finderBrand').value;
    $('#featuredModels').hidden = finderOpen;
    $('#featuredHeading').textContent = !finderOpen
      ? 'Choose a brand'
      : brand
        ? `${brand} models`
        : 'Find your model';
    $('#browseModelLibrary').textContent = finderOpen ? 'Browse brands' : 'Search by model';
    $('#browseModelLibrary').setAttribute('aria-expanded', String(finderOpen));
    $('#setupSelection').hidden = app.setupMode === 'rebuild' && !finderOpen;
    $('#vehicleName').placeholder = brand ? `Search ${brand} models` : 'Brand or model name';
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
        : !name
          ? ''
          : vehicleReference(name)
            ? 'Original model reference included. Check your year and variant.'
            : vehicleArtworkAudit(name)
              ? 'Source audit: ' +
                vehicleArtworkAudit(name).reason +
                ' A labeled concept remains available.'
              : 'This name has no verified image yet. A clearly labeled concept view is available.';
  }
  function syncSetup({ showBrands = false } = {}) {
    if (showBrands) $('#modelFinder').hidden = true;
    renderBrands();
    document.querySelectorAll('[data-type]').forEach((button) => {
      button.classList.toggle('chosen', button.dataset.type === app.setupType);
      button.setAttribute('aria-pressed', button.dataset.type === app.setupType);
    });
    document.querySelectorAll('[data-mode]').forEach((button) => {
      button.classList.toggle('chosen', button.dataset.mode === app.setupMode);
    });
    $('#featuredSection').hidden = app.setupMode !== 'rebuild';
    $('#newFields').hidden = app.setupMode !== 'new';
    $('#setupHeading').textContent =
      app.setupMode === 'rebuild' ? 'Start with your ride.' : 'Build something your own.';
    $('#setupDescription').textContent =
      app.setupMode === 'rebuild'
        ? 'Pick a brand or search for the vehicle you own.'
        : 'Choose a platform, name your project and start with the components.';
    vehicleSuggestions();
  }
  function vehicleSuggestions() {
    const query = $('#vehicleName').value.trim(),
      brand = $('#finderBrand').value;
    const allMatches = findVehicles(query, {
      type: app.setupType,
      brand,
      saved: app.builds,
    }).filter((vehicle) => !brand || vehicle.type === app.setupType);
    const photosOnly = $('#photoModelsOnly').checked;
    const matches = photosOnly ? allMatches.filter((v) => vehicleReference(v.name)) : allMatches;
    const shown = app.showAllVehicles ? matches : matches.slice(0, query ? 8 : 6);
    app.activeVehicleSuggestion = -1;
    $('#vehicleKeyboardStatus').textContent = '';
    $('#vehicleMatchCount').textContent =
      `${matches.length} ${photosOnly ? (matches.length === 1 ? 'pictured model' : 'pictured models') : matches.length === 1 ? 'match' : 'matches'}`;
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
    const canonicalQuery = canonicalVehicleName(query);
    const compactQuery = normalizeVehicleName(canonicalQuery).replace(/ /g, '');
    const exact =
      VEHICLE_INDEX.some((vehicle) => vehicle.name === canonicalQuery) ||
      allMatches.some(
        (vehicle) => normalizeVehicleName(vehicle.name).replace(/ /g, '') === compactQuery,
      );
    $('#customVehicle').hidden = !query || exact;
    $('#customVehicle').textContent = `Use “${query}” as a custom name`;
    $('#vehicleNote').textContent =
      'Search supports model aliases and spacing variations. Product images show the original vehicle; variants and installed parts can differ.';
    renderSelection();
  }
  function chooseVehicle(name, type) {
    $('#vehicleName').value = name;
    app.setupType = type;
    app.showAllVehicles = false;
    syncSetup();
    $('#vehicleNote').textContent =
      `Selected ${name}. Confirm your model year, version and installed parts.`;
    $('#startBuild').focus();
  }
  return { openStart, renderSelection, syncSetup, vehicleSuggestions, chooseVehicle };
}
