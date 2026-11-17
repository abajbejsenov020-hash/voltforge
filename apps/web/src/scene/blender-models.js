import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

export const BLENDER_MODELS = Object.freeze({
  'kukirin-g4': '/models/kukirin-g4.glb',
  'surron-lbx': '/models/surron-lbx.glb',
});

// Each load owns its resources. No mutable scene or GPU resource is cached/shared.
const disposedResources = new WeakSet();
export function disposeModelResources(root, protectedMaterials = new Set()) {
  const resources = new Set();
  const protectedTextures = new Set();
  for (const material of protectedMaterials)
    for (const value of Object.values(material)) if (value?.isTexture) protectedTextures.add(value);
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

function localBounds(root) {
  root.updateWorldMatrix(true, true);
  const inverse = root.matrixWorld.clone().invert();
  const bounds = new THREE.Box3();
  root.traverse((object) => {
    if (!object.isMesh) return;
    object.geometry.computeBoundingBox();
    bounds.union(
      object.geometry.boundingBox
        .clone()
        .applyMatrix4(new THREE.Matrix4().multiplyMatrices(inverse, object.matrixWorld)),
    );
  });
  return bounds;
}

/** Mount transforms are authored by Blender; preserve their complete base pose. */
export function createBlenderAssembly(root, createComponent) {
  const mounts = [
    ['Batteries', 'BatteryMount', new THREE.Vector3(0, 0.5, -0.24)],
    ['Controllers', 'ControllerMount', new THREE.Vector3(0, 0.28, 0.27)],
    ['Motors', 'MotorMount', new THREE.Vector3(0, 0.12, 0.25)],
  ]
    .map(([category, name, offset]) => {
      const node = root.getObjectByName(name);
      if (!node) return null;
      const bounds = localBounds(node);
      return {
        category,
        node,
        offset,
        base: node.position.clone(),
        stock: [...node.children],
        bounds,
        preview: null,
        id: null,
      };
    })
    .filter(Boolean);
  return {
    mounts,
    setSelection(selection) {
      for (const mount of mounts) {
        const part = selection[mount.category];
        if (mount.id === (part?.id || null)) continue;
        if (mount.preview) {
          mount.node.remove(mount.preview.root);
          mount.preview.dispose();
          mount.preview = null;
        }
        mount.stock.forEach((child) => {
          child.visible = true;
        });
        mount.id = part?.id || null;
        if (!part || mount.bounds.isEmpty()) continue;
        let preview;
        try {
          preview = createComponent(part);
          const bounds = new THREE.Box3().setFromObject(preview.root);
          const size = bounds.getSize(new THREE.Vector3());
          const envelope = mount.bounds.getSize(new THREE.Vector3());
          const scale = Math.min(...['x', 'y', 'z'].map((axis) => envelope[axis] / size[axis]));
          if (!Number.isFinite(scale) || scale <= 0) {
            preview.dispose();
            continue;
          }
          preview.root.scale.multiplyScalar(scale);
          preview.root.position
            .copy(mount.bounds.getCenter(new THREE.Vector3()))
            .sub(bounds.getCenter(new THREE.Vector3()).multiplyScalar(scale));
          preview.root.userData.selectedPartId = part.id;
          preview.root.traverse((object) => {
            if (object.isMesh) {
              object.castShadow = true;
              object.receiveShadow = true;
            }
          });
          mount.stock.forEach((child) => {
            child.visible = false;
          });
          mount.node.add(preview.root);
          mount.preview = preview;
        } catch {
          preview?.dispose();
          // An unverified catalogue entry keeps the authored, solid stock envelope.
        }
      }
    },
    setExploded(exploded) {
      for (const mount of mounts) {
        mount.node.position.copy(mount.base);
        if (!exploded) continue;
        mount.node.updateWorldMatrix(true, false);
        const point = mount.node.getWorldPosition(new THREE.Vector3()).add(mount.offset);
        mount.node.position.copy(mount.node.parent.worldToLocal(point));
      }
    },
    dispose() {
      for (const mount of mounts) {
        if (!mount.preview) continue;
        mount.node.remove(mount.preview.root);
        mount.preview.dispose();
        mount.preview = null;
      }
    },
  };
}
