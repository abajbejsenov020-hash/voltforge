import { $, esc } from '../ui/dom.js';
import { CATEGORIES, CATALOG } from '@voltforge/shared/catalog';
import { PartPreviews } from '../scene/components/index.js';
import { normalizeVehicleName, canonicalVehicleName } from '@voltforge/shared/vehicles';
export function createFeature(app) {
  function renderTabs() {
    const p = app.selected();
    $('#categorySelect').innerHTML = CATEGORIES.map(
      (c) => '<option ' + (c === app.category ? 'selected' : '') + '>' + esc(c) + '</option>',
    ).join('');
    $('.tabs').innerHTML = CATEGORIES.map(
      (c) =>
        `<button role="tab" aria-selected="${c === app.category}" data-cat="${c}">${c}${p[c] ? ' ·' : ''}</button>`,
    ).join('');
    $('.tabs')
      .querySelectorAll('button')
      .forEach(
        (b) =>
          (b.onclick = () => {
            app.category = b.dataset.cat;
            $('#search').value = '';
            $('#brand').value = '';
            app.renderCatalog();
            app.renderTabs();
          }),
      );
  }
  function renderCatalog() {
    let pool = CATALOG.filter(
      (p) =>
        p.category === app.category &&
        ($('#appearanceFilter').value === 'all' || PartPreviews.describe(p).reference) &&
        ($('#vehicleFilter').value === 'all' || p.type === 'both' || p.type === app.state.type) &&
        ($('#vehicleFilter').value !== 'model' ||
          (app.state.mode === 'rebuild' &&
            p.models?.some(
              (name) =>
                normalizeVehicleName(name) ===
                normalizeVehicleName(canonicalVehicleName(app.state.vehicle)),
            ))),
    );
    const brands = [...new Set(pool.map((p) => p.brand))],
      old = $('#brand').value;
    $('#brand').innerHTML =
      '<option value="">All brands</option>' +
      brands.map((b) => `<option ${b === old ? 'selected' : ''}>${b}</option>`).join('');
    const q = $('#search').value.trim().toLowerCase();
    pool = pool.filter(
      (p) =>
        (!$('#brand').value || p.brand === $('#brand').value) &&
        (!q ||
          normalizeVehicleName(
            [p.brand, p.name, p.detail, p.platform, ...(p.models || [])].join(' '),
          )
            .replace(/ /g, '')
            .includes(normalizeVehicleName(q).replace(/ /g, ''))),
    );
    pool.sort(
      (a, b) =>
        Number(!!PartPreviews.describe(b).reference) - Number(!!PartPreviews.describe(a).reference),
    );
    $('#resultsCount').textContent =
      pool.length +
      ' ' +
      (pool.length === 1
        ? {
            Motors: 'motor',
            Controllers: 'controller',
            Batteries: 'battery',
            Brakes: 'brake option',
            Displays: 'display',
            Accessories: 'accessory',
            'Tires & wheels': 'tire / wheel option',
            Suspension: 'suspension option',
          }[app.category]
        : app.category.toLowerCase()) +
      ' to explore';
    $('#catalogCount').textContent =
      $('#appearanceFilter').value === 'all'
        ? CATALOG.length
        : CATALOG.filter((p) => PartPreviews.describe(p).reference).length;
    $('#parts').innerHTML = pool.length
      ? pool
          .map((p) => {
            const chosen = app.state.selected[p.category] === p.id;
            return `<article class="part-card ${chosen ? 'selected' : ''}"><div class="part-top"><div class="component-tile">${PartPreviews.markup(p)}</div><div class="part-copy"><div class="part-brand">${esc(p.brand)}</div><div class="part-name">${esc(p.name)}</div><div class="part-spec">${esc(p.detail)}</div></div></div><div class="part-bottom"><span class="part-tag ${p.reference && !p.request ? 'known' : ''}">${p.template ? 'Planning template' : p.request ? 'Supplier confirmation' : 'Manufacturer reference'}</span><div class="part-actions"><button class="part-detail" data-detail="${p.id}">Inspect part</button><button class="add-part" data-add="${p.id}" aria-pressed="${chosen}" aria-label="${chosen ? 'Remove' : 'Add'} ${esc(p.brand + ' ' + p.name)}">${chosen ? 'Added' : 'Add'}</button></div></div></article>`;
          })
          .join('')
      : '<div class="empty">No parts match those filters.<br>Try another brand or browse all parts for this vehicle type. Model-specific lists include supplier-listed replacements and clearly marked requests.<br><button class="btn" id="clearFilters">Clear filters</button><button class="btn" id="showPlanningParts">Include templates & requests</button></div>';
    const selectedEntry = CATALOG.find((p) => p.id === app.state.selected[app.category]);
    if (
      $('#appearanceFilter').value === 'products' &&
      selectedEntry &&
      !PartPreviews.describe(selectedEntry).reference
    ) {
      $('#parts').insertAdjacentHTML(
        'afterbegin',
        '<div class="selected-planning-part">Your build uses ' +
          esc(selectedEntry.brand + ' ' + selectedEntry.name) +
          '. <button type="button" id="showSelectedPlanningPart">View it in the complete catalog</button></div>',
      );
      $('#showSelectedPlanningPart').onclick = () => {
        $('#appearanceFilter').value = 'all';
        app.renderCatalog();
      };
    }
    renderStockCard();
    PartPreviews.mount($('#parts'));
    $('#parts')
      .querySelectorAll('[data-add]')
      .forEach((b) => (b.onclick = () => app.togglePart(b.dataset.add)));
    $('#parts')
      .querySelectorAll('[data-detail]')
      .forEach((b) => (b.onclick = () => app.partDetail(b.dataset.detail)));
    if ($('#showPlanningParts'))
      $('#showPlanningParts').onclick = () => {
        $('#appearanceFilter').value = 'all';
        app.renderCatalog();
      };
    if ($('#clearFilters'))
      $('#clearFilters').onclick = () => {
        $('#search').value = '';
        $('#brand').value = '';
        $('#vehicleFilter').value = 'all';
        app.renderCatalog();
      };
  }
  function renderStockCard() {
    if (app.state.mode !== 'rebuild') return;
    const current = app.effectiveParts()[app.category];
    const changed = current && !current.stock;
    const stock = changed ? null : current;
    $('#parts').insertAdjacentHTML(
      'afterbegin',
      `<article class="stock-part-card" data-stock-category="${esc(app.category)}">
      <div class="stock-part-heading"><span class="stock-part-badge">${current?.stockEquivalent ? 'FACTORY REPLACEMENT' : changed ? 'MODIFIED' : 'STOCK · FACTORY FITTED'}</span>${changed ? `<button type="button" class="text-btn" id="returnToStock">Return to stock</button>` : ''}</div>
      <strong>${changed ? esc(current.brand + ' ' + current.name) : esc(stock?.name || app.state.vehicle + ' factory ' + app.category.toLowerCase())}</strong>
      <p>${current?.stockEquivalent ? 'Matching factory motor family. Overall performance depends on the remaining hardware; confirm the exact replacement version.' : changed ? 'This replaces the factory component. All other unchanged categories remain stock.' : 'Included automatically. Choose an upgrade below to replace it.'}</p>
    </article>`,
    );
    if ($('#returnToStock')) $('#returnToStock').onclick = () => app.togglePart(current.id);
  }
  function togglePart(id) {
    const p = CATALOG.find((p) => p.id === id);
    if (!p) return;
    if (['Motors', 'Controllers', 'Batteries'].includes(p.category)) {
      app.invalidatePerformanceMeasurements();
    }
    const removing = app.state.selected[p.category] === id;
    if (removing) delete app.state.selected[p.category];
    else app.state.selected[p.category] = id;
    if (p.category === 'Batteries') {
      app.state.specs.fullV = '';
      app.state.specs.bms = '';
      app.state.performance = {
        ...app.state.performance,
        nominalVoltage: '',
        capacityAh: '',
        rpm: '',
      };
    }
    if (p.category === 'Controllers') app.state.specs.batteryLimit = '';
    if (p.category === 'Motors') {
      app.state.performance = { ...app.state.performance };
      delete app.state.performance.power;
      delete app.state.performance.rpm;
      delete app.state.performance.wheel;
      if (removing && app.state.mode === 'rebuild') {
        delete app.state.specs.motorCountOverride;
        app.state.specs.motorCount = app.performanceProfile()?.motors || 1;
      }
    }
    app.save();
    app.render();
    const issues = app.checks().filter((i) => i.kind === 'conflict');
    $('#assistantText').textContent = issues.length
      ? issues[0].text
      : removing
        ? 'Part removed. Your build has been updated.'
        : p.brand + ' ' + p.name + ' added. ' + app.checks().find((i) => i.kind === 'unknown').text;
    app.toast(
      removing && app.state.mode === 'rebuild'
        ? 'Factory ' + p.category.toLowerCase() + ' restored'
        : removing
          ? 'Part removed'
          : p.name + ' added to your build',
    );
  }
  function partDetail(id) {
    const p = CATALOG.find((p) => p.id === id),
      appearance = PartPreviews.describe(p);
    if (!p) return;
    app.detail(
      p.brand + ' ' + p.name,
      `<div class="component-inspector">${PartPreviews.markup(p, true)}</div>${appearance.reference ? `<p class="component-disclosure">${esc(appearance.variantNote || 'Product-specific reference photograph from the linked supplier.')} The 3D tab is a photo-guided approximation; it is not measured manufacturer CAD. Confirm dimensions, connectors and revision before ordering.</p><p><a href="${esc(appearance.source)}" target="_blank" rel="noopener noreferrer">View this product’s appearance source ↗</a></p>` : `<div class="issue">${p.template ? 'This is a planning specification, so it has no fixed physical appearance. Choose a supplier and exact product before creating its model.' : p.request ? 'This entry is a replacement inquiry. The exact SKU, year and revision need confirmation before its appearance can be modeled.' : 'An exact product image or CAD model has not been verified for this entry.'}</div>`}<p>${esc(p.detail)}</p>${p.models ? '<p>Listed model family: ' + p.models.map(esc).join(', ') + '. Exact revision and fitment must be confirmed.</p>' : ''}${p.note ? '<p>' + esc(p.note) + '</p>' : ''}<p>${p.maxV ? 'Published upper voltage limit: ' + p.maxV + 'V. This is not a nominal battery rating. ' : ''}${p.dropout ? 'Listed motor opening: ' + p.dropout + 'mm. ' : ''}${p.channels ? 'Controller channels: ' + p.channels + '. ' : ''}${p.platform ? 'Platform: ' + esc(p.platform) + '. ' : ''}</p>${p.reference ? `<p><a href="${p.reference}" target="_blank" rel="noopener noreferrer">Open supplier reference ↗</a></p>` : ''}<button class="btn primary" id="detailAdd">${app.state.selected[p.category] === id ? 'Remove from build' : 'Add to build'}</button>`,
    );
    PartPreviews.mount($('#detailBody'));
    $('#detailAdd').onclick = () => {
      app.togglePart(id);
      $('#detailDialog').close();
    };
  }
  return { renderTabs, renderCatalog, togglePart, partDetail };
}
