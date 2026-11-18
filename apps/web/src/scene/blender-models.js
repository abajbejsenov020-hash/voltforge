import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import {
  canonicalVehicleName,
  normalizeVehicleName,
  VEHICLE_INDEX,
} from '@voltforge/shared/vehicles';
import scooters from '../data/blender-scooters.json' with { type: 'json' };
import lightmoto from '../data/blender-lightmoto.json' with { type: 'json' };
import motoBicycle from '../data/blender-moto-bicycle.json' with { type: 'json' };
import { EXPANDED_BLENDER_VEHICLES } from '../data/vehicle-artwork.js';

export const BLENDER_VEHICLES = [
  {
    name: 'KuKirin G4',
    key: 'kukirin-g4',
    url: '/models/kukirin-g4.glb',
    nativeSource: 'assets/blender/kukirin-g4.blend',
    bytes: 4209580,
  },
  {
    name: 'Sur-Ron Light Bee X',
    key: 'surron-lbx',
    url: '/models/surron-lbx.glb',
    nativeSource: 'assets/blender/surron-lbx.blend',
    bytes: 3332800,
  },
  ...scooters,
  ...lightmoto,
  ...motoBicycle,
  ...EXPANDED_BLENDER_VEHICLES,
];
// A batch entry becomes available only after Blender has exported and checked it.
const available = BLENDER_VEHICLES.filter((entry) => entry.bytes > 0);
export const BLENDER_MODELS = Object.freeze(
  Object.fromEntries(available.map((entry) => [entry.key, entry.url])),
);
const byName = new Map(available.map((entry) => [normalizeVehicleName(entry.name), entry.key]));
const indexedNames = new Set(VEHICLE_INDEX.map((entry) => normalizeVehicleName(entry.name)));
export function blenderModelKey(name) {
  const exact = normalizeVehicleName(name);
  if (byName.has(exact)) return byName.get(exact);
  // A different catalog variant must not silently acquire a related model's geometry.
  if (indexedNames.has(exact)) return null;
  return byName.get(normalizeVehicleName(canonicalVehicleName(name))) || null;
}

// Each load owns its resources. No mutable scene or GPU resource is cached/shared.
const disposedResources = new WeakSet();
const closedImages = new WeakSet();
export function disposeModelResources(root, protectedMaterials = new Set()) {
  const resources = new Set();
  const protectedTextures = new Set();
  for (const material of protectedMaterials)
    for (const value of Object.values(material)) if (value?.isTexture) protectedTextures.add(value);
  const protectedImages = new Set(
    [...protectedTextures].flatMap((texture) => [texture.source?.data].flat()),
  );
  root.traverse((object) => {
    if (object.geometry) resources.add(object.geometry);
    for (const material of [object.material].flat().filter(Boolean)) {
      if (protectedMaterials.has(material)) continue;
      resources.add(material);
      for (const value of Object.values(material))
        if (value?.isTexture && !protectedTextures.has(value)) resources.add(value);
    }
  });
  for (const resource of resources) {
    if (disposedResources.has(resource)) continue;
    disposedResources.add(resource);
    resource.dispose();
    // GLTFLoader's ImageBitmaps need explicit CPU-side release as well as texture disposal.
    if (resource.isTexture)
      for (const image of [resource.source?.data].flat()) {
        if (
          typeof image?.close !== 'function' ||
          protectedImages.has(image) ||
          closedImages.has(image)
        )
          continue;
        closedImages.add(image);
        image.close();
      }
  }
}

/** A late completion can never replace a newer vehicle or a disposed viewer. */
export function createBlenderLoader({ loader = new GLTFLoader(), onReady, onError } = {}) {
  let generation = 0;
  let disposed = false;
  return {
    async load(profile) {
      const request = ++generation;
      const url = BLENDER_MODELS[profile];
      if (!url || disposed) return false;
      let root;
      try {
        const gltf = await loader.loadAsync(url);
        root = gltf.scene;
        if (disposed || request !== generation) {
          disposeModelResources(root);
          return false;
        }
        const bounds = new THREE.Box3().setFromObject(root);
        if (
          bounds.isEmpty() ||
          !bounds.min.toArray().concat(bounds.max.toArray()).every(Number.isFinite)
        )
          throw new Error('The Blender asset contains no finite model geometry');
        root.traverse((object) => {
          if (!object.isMesh) return;
          object.castShadow = true;
          object.receiveShadow = true;
        });
        onReady?.(root, profile);
        return true;
      } catch (error) {
        if (root) disposeModelResources(root);
        if (!disposed && request === generation) onError?.(error, profile);
        return false;
      }
    },
    cancel() {
      generation++;
    },
    dispose() {
      disposed = true;
      generation++;
    },
  };
}

export { createBlenderAssembly } from './vehicle-assembly.js';
