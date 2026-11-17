import * as THREE from 'three';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
import { createGarage } from './garage.js';

const SETTINGS = {
  garage: {
    url: '/environments/auto_service_1k.hdr',
    rotation: 1.1,
    exposure: 1.0,
  },
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

/** A physical garage surrounds the model; HDR maps supply material reflections. */
export function createStageEnvironment({ renderer, scene, floor, grid, key, fill, onChange }) {
  const loader = new RGBELoader();
  const generator = new THREE.PMREMGenerator(renderer);
  const fallbackEnvironment = scene.environment;
  const ambientLights = scene.children
    .filter(
      (light) =>
        light.isHemisphereLight || (light.isDirectionalLight && light !== key && light !== fill),
    )
    .map((light) => ({ light, intensity: light.intensity }));
  const cache = new Map();
  let sequence = 0;
  let disposed = false;
  let garage = null;
  let activeName = '';
  let garageLighting = 'loading';
  const shadowMaterial = floor.material;
  shadowMaterial.opacity = 0.28;
  shadowMaterial.color.setHex(0x151817);
  const groundMaterial = new THREE.MeshStandardMaterial({
    color: 0x8b8984,
    roughness: 0.76,
    metalness: 0.03,
  });
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
  const seamGeometry = new THREE.BoxGeometry(0.005, 0.001, 18);
  const seamMaterial = new THREE.MeshStandardMaterial({ color: 0x6e706c, roughness: 1 });
  for (const x of [-6, -4, -2, 2, 4, 6]) {
    const line = new THREE.Mesh(seamGeometry, seamMaterial);
    line.position.set(x, -0.044, 0);
    seams.add(line);
  }
  scene.add(seams);

  function cached(key, load) {
    if (!cache.has(key)) {
      const pending = load().catch((error) => {
        cache.delete(key);
        throw error;
      });
      cache.set(key, pending);
    }
    return cache.get(key);
  }
  function hdr(url) {
    return cached(url, async () => {
      const texture = await loader.loadAsync(url);
      if (disposed) {
        texture.dispose();
        return null;
      }
      texture.mapping = THREE.EquirectangularReflectionMapping;
      let target;
      try {
        target = generator.fromEquirectangular(texture);
      } catch (error) {
        texture.dispose();
        throw error;
      }
      return {
        texture,
        target,
        dispose: () => {
          texture.dispose();
          target.dispose();
        },
      };
    });
  }
  function garageStatus() {
    if (disposed || activeName !== 'garage' || !garage) return;
    const status = document.querySelector('#sceneEnvironmentStatus');
    if (status)
      status.textContent =
        garageLighting === 'loading'
          ? 'Loading setting…'
          : garage.state.loading
            ? 'Garage · parking Blender models…'
            : garage.state.failed
              ? 'Garage · parked model unavailable'
              : garageLighting === 'hdr'
                ? 'Garage · 3D workshop'
                : 'Garage · studio lighting';
  }
  function prepare(name) {
    const garage = name === 'garage';
    floor.material = garage ? shadowMaterial : groundMaterial;
    floor.visible = !garage;
    floor.position.y = garage ? -0.006 : -0.046;
    platform.visible = rim.visible = !garage;
    seams.visible = !garage && name !== 'studio';
    grid.visible = false;
    scene.backgroundIntensity = 1;
    scene.backgroundBlurriness = 0;
    scene.backgroundRotation.y = 0;
    scene.environmentRotation.y = 0;
    key.color.setHex(garage ? 0xffdfb6 : 0xfff8e9);
    fill.color.setHex(garage ? 0xb8d7ff : 0xe4ecff);
    key.intensity = garage ? 2.8 : 4;
    fill.intensity = garage ? 1.45 : 2;
    for (const { light, intensity } of ambientLights)
      light.intensity = garage ? intensity * 0.48 : intensity;
    scene.environment = fallbackEnvironment;
    scene.environmentIntensity = garage ? 0.65 : 1;
    renderer.toneMappingExposure = garage ? 1 : 1.12;
  }
  async function set(requestedName = 'garage') {
    if (disposed) return;
    const name = requestedName === 'studio' || SETTINGS[requestedName] ? requestedName : 'garage';
    const revision = ++sequence;
    activeName = name;
    if (name !== 'garage') {
      garage?.dispose();
      garage = null;
    }
    const status = document.querySelector('#sceneEnvironmentStatus');
    prepare(name);
    scene.background = new THREE.Color(name === 'garage' ? 0x343b3d : 0xe8e5df);
    if (name === 'garage') {
      garageLighting = 'loading';
      if (!garage) garage = createGarage({ scene, onChange, onStatus: garageStatus });
    }
    if (name === 'studio') {
      groundMaterial.color.setHex(0xb6b5ad);
      if (status) status.textContent = 'Studio';
      onChange();
      return;
    }
    const setting = SETTINGS[name];
    if (status) status.textContent = 'Loading setting…';
    onChange();
    const [lighting] = await Promise.allSettled([hdr(setting.url)]);
    if (disposed || revision !== sequence) return;
    const light = lighting.status === 'fulfilled' ? lighting.value : null;
    if (light) {
      scene.environment = light.target.texture;
      scene.environmentIntensity = name === 'garage' ? 0.68 : 0.85;
      scene.environmentRotation.y = setting.rotation;
    }
    renderer.toneMappingExposure = setting.exposure;
    if (name === 'garage') {
      garageLighting = light ? 'hdr' : 'studio';
      garageStatus();
    } else {
      groundMaterial.color.setHex(setting.ground);
      key.intensity = 2.5;
      fill.intensity = 1.2;
      key.color.setHex(name === 'workshop' ? 0xffedcf : 0xfff8ec);
      if (light) {
        scene.background = light.texture;
        scene.backgroundRotation.y = setting.rotation;
        scene.backgroundBlurriness = 0.018;
      }
      if (status)
        status.textContent = light
          ? name === 'workshop'
            ? 'Workshop'
            : 'Courtyard'
          : 'Studio fallback';
    }
    onChange();
  }
  return {
    set,
    dispose() {
      if (disposed) return;
      disposed = true;
      sequence++;
      garage?.dispose();
      garage = null;
      for (const pending of cache.values())
        void pending.then(
          (entry) => entry?.dispose(),
          () => {},
        );
      cache.clear();
      generator.dispose();
      for (const mesh of [platform, rim]) {
        scene.remove(mesh);
        mesh.geometry.dispose();
        mesh.material.dispose();
      }
      scene.remove(seams);
      seamGeometry.dispose();
      seamMaterial.dispose();
      // The scene owns and disposes whichever material is currently on its floor.
      (floor.material === shadowMaterial ? groundMaterial : shadowMaterial).dispose();
    },
  };
}
