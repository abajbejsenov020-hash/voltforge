import { vehicleReference } from '../data/vehicle-library.js';
import { getVehicleVisual } from '@voltforge/shared/visuals';
import { BLENDER_MODELS } from './blender-models.js';

/** Photo references and photo-based Blender models retain distinct fidelity labels. */
export function createVehicleViewer({ sceneFactory }) {
  const root = document.querySelector('.stage');
  const canvas = document.querySelector('#scene');
  const photo = document.querySelector('#vehiclePhoto');
  const missing = document.querySelector('#vehicleReferenceMissing');
  const source = document.querySelector('#vehiclePhotoSource');
  const setting = document.querySelector('#sceneSetting');
  const viewButtons = root.querySelectorAll('button[data-presentation]');
  let mode = 'photo',
    reference = null,
    vehicleName = '',
    type = 'scooter';
  let selection = {},
    category = 'Motors',
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
            ? 'Loading photo-based Blender model · temporary concept shown'
            : 'Drag to rotate · Scroll to zoom · Appearance concept, not measured manufacturer CAD';
  }
  canvas.addEventListener('modelsourcechange', modelNote);
  function show() {
    const inPhoto = mode === 'photo',
      hasPhoto = Boolean(reference) && !imageFailed;
    root.dataset.presentation = mode;
    canvas.hidden = inPhoto;
    document.querySelector('#vehicleReference').hidden = !inPhoto || !hasPhoto;
    missing.hidden = !inPhoto || hasPhoto;
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
    document.querySelector('#referenceVariant').hidden = !inPhoto || !hasPhoto;
    if (!inPhoto) {
      getScene().update(type, selection, category, vehicleName);
      scene.resize?.();
    }
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
    scene?.setEnvironment?.(setting.value);
  };
  return {
    getReference: () => reference,
    update(nextType, nextSelection, nextCategory, nextName) {
      const changed = vehicleName !== (nextName || '');
      type = nextType;
      selection = nextSelection;
      category = nextCategory;
      vehicleName = nextName || '';
      if (changed || !reference) {
        reference = vehicleReference(vehicleName);
        imageFailed = false;
        if (changed)
          mode = BLENDER_MODELS[getVehicleVisual(vehicleName, type).profile] ? 'concept' : 'photo';
        if (reference) {
          photo.src = reference.image;
          photo.alt = `${reference.name} — original product reference`;
          source.href = reference.source;
          source.textContent = `${reference.credit} · image source ↗`;
          document.querySelector('#referenceVariant').textContent = reference.variantNote || '';
        }
      }
      // Also invalidate an in-flight model when changing vehicles in photo mode.
      if (scene) scene.update(type, selection, category, vehicleName);
      show();
    },
    dispose() {
      canvas.removeEventListener('modelsourcechange', modelNote);
      scene?.dispose?.();
    },
  };
}
