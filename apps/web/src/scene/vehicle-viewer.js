import { vehicleReference, vehicleArtworkAudit } from '../data/vehicle-library.js';
import { blenderModelKey } from './blender-models.js';
import { PAINT_ZONES } from '@voltforge/shared/build';

/** Photo references and photo-based Blender models retain distinct fidelity labels. */
export function createVehicleViewer({ sceneFactory, onPaintChange }) {
  const root = document.querySelector('.stage');
  const canvas = document.querySelector('#scene');
  const photo = document.querySelector('#vehiclePhoto');
  const missing = document.querySelector('#vehicleReferenceMissing');
  const source = document.querySelector('#vehiclePhotoSource');
  const setting = document.querySelector('#sceneSetting');
  const modelEdits = document.querySelector('#modelEdits');
  const swapStatus = document.querySelector('#swapStatus');
  const paintControls = document.querySelector('#paintControls');
  const paintZone = document.querySelector('#paintZone');
  const paintColor = document.querySelector('#paintColor');
  const resetPaint = document.querySelector('#resetPaint');
  const environmentKey = 'voltforge-scene-environment';
  try {
    const savedEnvironment = localStorage.getItem(environmentKey);
    if ([...setting.options].some((option) => option.value === savedEnvironment))
      setting.value = savedEnvironment;
  } catch {
    // Private or blocked storage still permits an in-memory environment choice.
  }
  root.dataset.environment = setting.value;
  const viewButtons = root.querySelectorAll('button[data-presentation]');
  let mode = 'photo',
    reference = null,
    vehicleName = '',
    type = 'scooter';
  let selection = {},
    paint = {},
    zones = [],
    category = 'Motors',
    motorCount,
    scene,
    imageFailed = false;

  function getScene() {
    if (!scene) {
      scene = sceneFactory();
      scene.setEnvironment?.(setting.value);
    }
    return scene;
  }
  function modelNote() {
    const blender = canvas.dataset.modelSource === 'blender';
    const waiting = canvas.dataset.modelState === 'loading';
    const button = root.querySelector('[data-presentation="concept"]');
    button.textContent = blender || waiting ? '3D model' : '3D concept';
    canvas.setAttribute(
      'aria-label',
      `Interactive 3D vehicle ${blender ? 'model' : 'concept'}. Drag or use arrow keys to rotate; plus and minus to zoom.`,
    );
    document.querySelector('#sceneNote').textContent =
      mode === 'photo'
        ? 'Original appearance · selected modifications are listed in your build'
        : blender
          ? 'Drag to rotate · Scroll to zoom · Photo-based Blender model, not manufacturer CAD'
          : waiting
            ? 'Loading photo-based Blender model…'
            : 'Drag to rotate · Scroll to zoom · Appearance concept, not measured manufacturer CAD';
  }
  function syncPaintInput() {
    const zone = paintZone.value;
    paintColor.value = paint[zone] || scene?.getPaintColors?.()[zone] || '#64696e';
    resetPaint.disabled = !paint[zone];
    resetPaint.setAttribute('aria-label', 'Reset ' + (PAINT_ZONES[zone] || 'paint') + ' color');
  }
  function syncModelEdits() {
    const is3D = mode === 'concept';
    const available = is3D ? scene?.getPaintZones?.() || [] : [];
    if (available.join() !== zones.join()) {
      const previous = paintZone.value;
      zones = available;
      paintZone.replaceChildren(...zones.map((zone) => new Option(PAINT_ZONES[zone], zone)));
      if (zones.includes(previous)) paintZone.value = previous;
    }
    paintControls.hidden = zones.length === 0;
    syncPaintInput();
    const selected = Object.keys(selection);
    const swaps = scene?.getSwaps?.() || {};
    const shown = selected.filter((category) => swaps[category]);
    const unshown = selected.filter((category) => !swaps[category]);
    const report = [];
    if (is3D && selected.length) {
      if (canvas.dataset.modelState === 'loading') report.push('Loading the 3D build…');
      else {
        if (shown.length) report.push(`In the 3D build: ${shown.join(', ')}.`);
        if (shown.length && (swaps.Batteries || swaps.Controllers))
          report.push('Use Exploded view to see parts inside the vehicle.');
        if (unshown.length) report.push(`3D replacement unavailable: ${unshown.join(', ')}.`);
      }
    }
    const message = report.join(' ');
    swapStatus.hidden = !message;
    if (swapStatus.textContent !== message) swapStatus.textContent = message;
    modelEdits.hidden = paintControls.hidden && swapStatus.hidden;
  }
  function onModelChange() {
    modelNote();
    syncModelEdits();
  }
  function applyPaint(next, save) {
    paint = next;
    scene?.setPaint?.(paint);
    resetPaint.disabled = !paint[paintZone.value];
    if (save) onPaintChange?.(paint);
  }
  paintZone.onchange = syncPaintInput;
  paintColor.oninput = () =>
    paintZone.value && applyPaint({ ...paint, [paintZone.value]: paintColor.value }, false);
  paintColor.onchange = () =>
    paintZone.value && applyPaint({ ...paint, [paintZone.value]: paintColor.value }, true);
  resetPaint.onclick = () => {
    const next = { ...paint };
    delete next[paintZone.value];
    applyPaint(next, true);
    syncPaintInput();
    paintColor.focus();
  };
  canvas.addEventListener('modelsourcechange', onModelChange);
  function show() {
    const inPhoto = mode === 'photo',
      hasPhoto = Boolean(reference) && !imageFailed;
    root.dataset.presentation = mode;
    canvas.hidden = inPhoto;
    document.querySelector('#vehicleReference').hidden = !inPhoto || !hasPhoto;
    missing.hidden = !inPhoto || hasPhoto;
    const audit = vehicleArtworkAudit(vehicleName);
    missing.querySelector('p').textContent = imageFailed
      ? 'The product image could not load. You can still inspect the 3D view.'
      : audit
        ? audit.reason
        : 'No verified image is available for this configuration yet.';
    source.hidden = !inPhoto || !hasPhoto;
    root
      .querySelectorAll(
        '.stage-controls,.model-inspection,#sceneEnvironmentStatus,#sceneModelStatus',
      )
      .forEach((element) => {
        element.hidden = inPhoto;
      });
    viewButtons.forEach((button) =>
      button.setAttribute('aria-pressed', String(button.dataset.presentation === mode)),
    );
    document.querySelector('#modelLabel').textContent = vehicleName || 'Custom build';
    modelNote();
    document.querySelector('#referencePhoto').hidden = !hasPhoto;
    document.querySelector('#referenceVariant').hidden = !reference?.variantNote;
    if (!inPhoto) {
      getScene().update(type, selection, category, vehicleName, paint, motorCount);
      scene.resize?.();
    }
    syncModelEdits();
  }
  viewButtons.forEach((button) => {
    button.onclick = () => {
      mode = button.dataset.presentation;
      show();
    };
  });
  document.querySelector('#openConceptView').onclick = () => {
    mode = 'concept';
    show();
  };
  photo.onerror = () => {
    imageFailed = true;
    show();
  };
  setting.onchange = () => {
    root.dataset.environment = setting.value;
    try {
      localStorage.setItem(environmentKey, setting.value);
    } catch {
      // The setting remains usable without persistent browser storage.
    }
    scene?.setEnvironment?.(setting.value);
  };
  return {
    getReference: () => reference,
    inspectBuild() {
      mode = 'concept';
      show();
      canvas.focus({ preventScroll: true });
      root.scrollIntoView({ block: 'nearest' });
    },
    update(nextType, nextSelection, nextCategory, nextName, nextPaint = {}, nextMotorCount) {
      const changed = vehicleName !== (nextName || '');
      type = nextType;
      selection = nextSelection;
      category = nextCategory;
      paint = nextPaint;
      motorCount = nextMotorCount;
      vehicleName = nextName || '';
      if (changed || !reference) {
        reference = vehicleReference(vehicleName);
        imageFailed = false;
        if (changed) mode = blenderModelKey(vehicleName) ? 'concept' : 'photo';
        if (reference) {
          photo.src = reference.image;
          photo.alt = `${reference.name} — original product reference`;
          source.href = reference.source;
          source.textContent = `${reference.credit} · image source ↗`;
          document.querySelector('#referenceVariant').textContent = reference.variantNote || '';
        }
      }
      // Also invalidate an in-flight model when changing vehicles in photo mode.
      if (scene && mode === 'photo')
        scene.update(type, selection, category, vehicleName, paint, motorCount);
      show();
    },
    dispose() {
      canvas.removeEventListener('modelsourcechange', onModelChange);
      scene?.dispose?.();
    },
  };
}
