import * as THREE from 'three';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

const SETTINGS = {
  workshop: {
    url: '/environments/auto_service_1k.hdr',
    rotation: 1.1,
    ground: 0x8b8984,
    exposure: 1.12,
  },
  courtyard: {
    url: '/environments/courtyard_1k.hdr',
    rotation: -0.8,
    ground: 0xb0aaa0,
    exposure: 1.0,
  },
};

/** Real HDR panoramas supply reflection/lighting; geometry still remains conceptual. */
export function createStageEnvironment({ renderer, scene, floor, grid, key, fill, onChange }) {
  const loader = new RGBELoader();
  const generator = new THREE.PMREMGenerator(renderer);
  const fallbackEnvironment = scene.environment;
  const cache = new Map();
  let sequence = 0;
  floor.material.dispose();
  floor.material = new THREE.MeshStandardMaterial({
    color: 0x8b8984,
    roughness: 0.76,
    metalness: 0.03,
  });
  floor.position.y = -0.046;
  const platform = new THREE.Mesh(
    new THREE.CylinderGeometry(1.24, 1.25, 0.04, 96),
    new THREE.MeshStandardMaterial({ color: 0x5e6261, metalness: 0.1, roughness: 0.58 }),
  );
  platform.position.y = -0.024;
  platform.receiveShadow = true;
  scene.add(platform);
  const rim = new THREE.Mesh(
    new THREE.TorusGeometry(1.23, 0.004, 8, 96),
    new THREE.MeshStandardMaterial({ color: 0xb69a84, metalness: 0.65, roughness: 0.45 }),
  );
  rim.rotation.x = -Math.PI / 2;
  rim.position.y = -0.002;
  scene.add(rim);
  const seams = new THREE.Group();
  for (const x of [-6, -4, -2, 2, 4, 6]) {
    const line = new THREE.Mesh(
      new THREE.BoxGeometry(0.005, 0.001, 18),
      new THREE.MeshStandardMaterial({ color: 0x6e706c, roughness: 1 }),
    );
    line.position.set(x, -0.044, 0);
    seams.add(line);
  }
  scene.add(seams);
  async function set(name = 'workshop') {
    const revision = ++sequence;
    const status = document.querySelector('#sceneEnvironmentStatus');
    if (name === 'studio') {
      scene.background = new THREE.Color(0xe8e5df);
      scene.environment = fallbackEnvironment;
      scene.environmentIntensity = 1;
      floor.material.color.setHex(0xb6b5ad);
      grid.visible = false;
      seams.visible = false;
      renderer.toneMappingExposure = 1.12;
      key.color.setHex(0xfff8e9);
      key.intensity = 4;
      fill.intensity = 2;
      scene.backgroundRotation.y = scene.environmentRotation.y = 0;
      if (status) status.textContent = 'Studio';
      onChange();
      return;
    }
    const setting = SETTINGS[name] || SETTINGS.workshop;
    if (status) status.textContent = 'Loading setting…';
    try {
      let entry = cache.get(name);
      if (!entry) {
        const texture = await loader.loadAsync(setting.url);
        texture.mapping = THREE.EquirectangularReflectionMapping;
        entry = { texture, environment: generator.fromEquirectangular(texture).texture };
        cache.set(name, entry);
      }
      if (revision !== sequence) return;
      scene.background = entry.texture;
      scene.environment = entry.environment;
      scene.backgroundBlurriness = 0.018;
      scene.environmentIntensity = 0.85;
      scene.backgroundRotation.y = scene.environmentRotation.y = setting.rotation;
      floor.material.color.setHex(setting.ground);
      seams.visible = true;
      grid.visible = false;
      renderer.toneMappingExposure = setting.exposure;
      key.intensity = 2.5;
      fill.intensity = 1.2;
      key.color.setHex(name === 'workshop' ? 0xffedcf : 0xfff8ec);
      if (status) status.textContent = name === 'workshop' ? 'Workshop' : 'Courtyard';
      onChange();
    } catch (error) {
      if (revision !== sequence) return;
      scene.background = new THREE.Color(0xe8e5df);
      scene.environment = fallbackEnvironment;
      if (status) status.textContent = 'Studio fallback';
      console.warn('Environment unavailable; studio lighting retained.', error);
      onChange();
    }
  }
  return { set };
}
