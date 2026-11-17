import { vehicleReference } from '../data/vehicle-library.js';

/** Product references preserve real appearance; the rotatable view is a separate concept. */
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
  function show() {
    const inPhoto = mode === 'photo',
      hasPhoto = Boolean(reference) && !imageFailed;
    root.dataset.presentation = mode;
    canvas.hidden = inPhoto;
    document.querySelector('#vehicleReference').hidden = !inPhoto || !hasPhoto;
    missing.hidden = !inPhoto || hasPhoto;
    source.hidden = !inPhoto || !hasPhoto;
    root
      .querySelectorAll('.stage-controls,.model-inspection,#sceneEnvironmentStatus')
      .forEach((element) => {
        element.hidden = inPhoto;
      });
    viewButtons.forEach((button) =>
      button.setAttribute('aria-pressed', String(button.dataset.presentation === mode)),
    );
    document.querySelector('#modelLabel').textContent = vehicleName || 'Custom build';
    document.querySelector('#sceneNote').textContent = inPhoto
      ? 'Original appearance · selected modifications are listed in your build'
      : 'Drag to rotate · Scroll to zoom · Appearance concept, not measured manufacturer CAD';
    document.querySelector('#referencePhoto').hidden = !hasPhoto;
    document.querySelector('#referenceVariant').hidden = !inPhoto || !hasPhoto;
    if (!inPhoto) getScene().update(type, selection, category, vehicleName);
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
        if (changed) mode = 'photo';
        if (reference) {
          photo.src = reference.image;
          photo.alt = `${reference.name} — original product reference`;
          source.href = reference.source;
          source.textContent = `${reference.credit} · image source ↗`;
          document.querySelector('#referenceVariant').textContent = reference.variantNote || '';
        }
      }
      if (scene && mode === 'concept') scene.update(type, selection, category, vehicleName);
      show();
    },
  };
}
