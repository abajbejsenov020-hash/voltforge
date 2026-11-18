import * as THREE from 'three';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
import { createGarage } from './garage.js';
import { createChargingPlaza } from './plaza.js';
import { createCoastalSunset } from './coastal-sunset.js';

const PHYSICAL_STAGES = {
  garage: createGarage,
  plaza: createChargingPlaza,
  coast: createCoastalSunset,
};

const SETTINGS = {
  garage: {
    url: '/environments/auto_service_1k.hdr',
    rotation: 1.1,
    exposure: 1.0,
  },
  plaza: {
    url: '/environments/courtyard_1k.hdr',
    rotation: -0.8,
    exposure: 0.98,
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

/** Physical settings surround the model; HDR maps supply material reflections. */
export function createStageEnvironment({ renderer, scene, floor, grid, key, fill, onChange }) {
  const loader = new RGBELoader();
  const generator = new THREE.PMREMGenerator(renderer);
  const fallbackEnvironment = scene.environment;
  const defaultKeyPosition = key.position.clone();
  const defaultFillPosition = fill.position.clone();
  const ambientLights = scene.children
    .filter(
      (light) =>
        light.isHemisphereLight || (light.isDirectionalLight && light !== key && light !== fill),
    )
    .map((light) => ({ light, intensity: light.intensity }));
  const cache = new Map();
  let sequence = 0;
  let disposed = false;
  let physicalStage = null;
  let activeName = '';
  let stageLighting = 'loading';
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
  function physicalStatus() {
    if (disposed || !physicalStage) return;
    const title = { coast: 'Coastal Sunset', plaza: 'City plaza', garage: 'Garage' }[activeName];
    const status = document.querySelector('#sceneEnvironmentStatus');
    if (status)
      status.textContent =
        stageLighting === 'loading'
          ? 'Loading setting…'
          : physicalStage.state.loading
            ? title + ' · parking Blender models…'
            : physicalStage.state.failed
              ? title + ' · parked model unavailable'
              : activeName === 'plaza'
                ? 'City plaza · 3D night setting'
                : activeName === 'coast'
                  ? 'Coastal Sunset · 3D waterfront'
                  : stageLighting === 'hdr'
                    ? 'Garage · 3D workshop'
                    : 'Garage · studio lighting';
  }
  function prepare(name) {
    const physical = Object.hasOwn(PHYSICAL_STAGES, name);
    const coast = name === 'coast';
    floor.material = physical ? shadowMaterial : groundMaterial;
    floor.visible = !physical;
    floor.position.y = physical ? -0.006 : -0.046;
    platform.visible = rim.visible = !physical;
    seams.visible = !physical && name !== 'studio';
    grid.visible = false;
    scene.fog =
      name === 'plaza'
        ? new THREE.FogExp2(0x142235, 0.038)
        : coast
          ? new THREE.FogExp2(0xc5a0b2, 0.025)
          : null;
    scene.backgroundIntensity = 1;
    scene.backgroundBlurriness = 0;
    scene.backgroundRotation.y = 0;
    scene.environmentRotation.y = 0;
    key.position.copy(defaultKeyPosition);
    fill.position.copy(defaultFillPosition);
    key.color.setHex(coast ? 0xffbd96 : physical ? 0xffdfb6 : 0xfff8e9);
    fill.color.setHex(coast ? 0xd9dcff : physical ? 0xb8d7ff : 0xe4ecff);
    if (coast) {
      key.position.set(-3, 3.5, -5);
      fill.position.set(2, 2.5, 3);
    }
    key.intensity = name === 'plaza' ? 2.3 : physical ? 2.8 : 4;
    fill.intensity = name === 'plaza' ? 0.9 : physical ? 1.45 : 2;
    for (const { light, intensity } of ambientLights)
      light.intensity = intensity * (name === 'plaza' ? 0.2 : physical ? 0.48 : 1);
    scene.environment = fallbackEnvironment;
    scene.environmentIntensity = coast ? 0.55 : physical ? 0.65 : 1;
    renderer.toneMappingExposure = physical ? 1 : 1.12;
  }
  async function set(requestedName = 'garage') {
    if (disposed) return;
    const name =
      requestedName === 'studio' ||
      Object.hasOwn(SETTINGS, requestedName) ||
      Object.hasOwn(PHYSICAL_STAGES, requestedName)
        ? requestedName
        : 'garage';
    const revision = ++sequence;
    if (name !== activeName) {
      physicalStage?.dispose();
      physicalStage = null;
    }
    activeName = name;
    const status = document.querySelector('#sceneEnvironmentStatus');
    prepare(name);
    scene.background = new THREE.Color(
      { coast: 0xca9db6, plaza: 0x131f30, garage: 0x343b3d }[name] ?? 0xe8e5df,
    );
    const create = PHYSICAL_STAGES[name];
    if (create) {
      stageLighting = name === 'coast' ? 'studio' : 'loading';
      if (!physicalStage) {
        physicalStage = create({ scene, onChange, onStatus: physicalStatus });
      }
    }
    if (name === 'coast') {
      physicalStatus();
      onChange();
      return;
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
      scene.environmentIntensity = name === 'plaza' ? 0.2 : name === 'garage' ? 0.68 : 0.85;
      scene.environmentRotation.y = setting.rotation;
    }
    renderer.toneMappingExposure = setting.exposure;
    if (create) {
      stageLighting = light ? 'hdr' : 'studio';
      physicalStatus();
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
      physicalStage?.dispose();
      physicalStage = null;
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
