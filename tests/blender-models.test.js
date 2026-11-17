import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { CATALOG } from '@voltforge/shared/catalog';
import { PartPreviews } from '../apps/web/src/scene/components/index.js';
import {
  BLENDER_MODELS,
  createBlenderLoader,
  createBlenderAssembly,
  disposeModelResources,
} from '../apps/web/src/scene/blender-models.js';

function solid() {
  const root = new THREE.Group();
  root.add(new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshStandardMaterial()));
  return root;
}

function deferredLoader() {
  const pending = [];
  return {
    pending,
    loadAsync(url) {
      return new Promise((resolve, reject) => pending.push({ url, resolve, reject }));
    },
  };
}

test('a late GLB never replaces a newer vehicle, and its resources are released once', async () => {
  const loader = deferredLoader();
  const shown = [];
  const coordinator = createBlenderLoader({
    loader,
    onReady: (root, profile) => shown.push(profile),
  });
  const first = coordinator.load('kukirin-g4');
  const second = coordinator.load('surron-lbx');
  const stale = solid();
  let released = 0;
  stale.children[0].geometry.addEventListener('dispose', () => released++);
  stale.children[0].material.addEventListener('dispose', () => released++);
  loader.pending[1].resolve({ scene: solid() });
  assert.equal(await second, true);
  loader.pending[0].resolve({ scene: stale });
  assert.equal(await first, false);
  disposeModelResources(stale);
  assert.equal(released, 2);
  assert.deepEqual(shown, ['surron-lbx']);
});

test('cancellation, disposal, failures and unsupported profiles preserve the active scene', async () => {
  const loader = deferredLoader();
  const errors = [];
  let ready = 0;
  const coordinator = createBlenderLoader({
    loader,
    onReady: () => ready++,
    onError: (error) => errors.push(error.message),
  });
  assert.equal(await coordinator.load('commuter-scooter'), false);
  assert.equal(loader.pending.length, 0);
  const failed = coordinator.load('kukirin-g4');
  loader.pending[0].reject(new Error('asset missing'));
  assert.equal(await failed, false);
  assert.deepEqual(errors, ['asset missing']);
  const cancelled = coordinator.load('kukirin-g4');
  coordinator.cancel();
  loader.pending[1].reject(new Error('stale failure'));
  assert.equal(await cancelled, false);
  const disposed = coordinator.load('surron-lbx');
  const root = solid();
  let released = 0;
  root.children[0].geometry.addEventListener('dispose', () => released++);
  coordinator.dispose();
  loader.pending[2].resolve({ scene: root });
  assert.equal(await disposed, false);
  assert.equal(await coordinator.load('kukirin-g4'), false);
  assert.equal(released, 1);
  assert.equal(ready, 0);
  assert.deepEqual(errors, ['asset missing']);
});

test('empty GLBs become an explicit load failure', async () => {
  let error;
  const coordinator = createBlenderLoader({
    loader: { loadAsync: async () => ({ scene: new THREE.Group() }) },
    onError: (value) => {
      error = value;
    },
  });
  assert.equal(await coordinator.load('kukirin-g4'), false);
  assert.match(error.message, /no finite model geometry/);
});

test('resource disposal deduplicates shared mesh resources and protects scene materials/textures', () => {
  const root = solid();
  const mesh = root.children[0];
  const texture = new THREE.Texture();
  mesh.material.map = texture;
  root.add(new THREE.Mesh(mesh.geometry, mesh.material));
  let geometry = 0,
    material = 0,
    map = 0;
  mesh.geometry.addEventListener('dispose', () => geometry++);
  mesh.material.addEventListener('dispose', () => material++);
  texture.addEventListener('dispose', () => map++);
  disposeModelResources(root, new Set([mesh.material]));
  assert.deepEqual([geometry, material, map], [1, 0, 0]);
  disposeModelResources(root);
  disposeModelResources(root);
  assert.deepEqual([geometry, material, map], [1, 1, 1]);
});

test('exploded mounts preserve authored translations and rotations, and reset without drift', () => {
  const root = new THREE.Group();
  root.rotation.x = -Math.PI / 2;
  const mount = solid();
  mount.name = 'BatteryMount';
  mount.position.set(0.2, -0.3, 0.7);
  mount.rotation.z = 0.4;
  root.add(mount);
  const initial = mount.position.clone();
  const rotation = mount.quaternion.clone();
  const startWorld = mount.getWorldPosition(new THREE.Vector3());
  const assembly = createBlenderAssembly(root, () => {
    throw new Error('unverified');
  });
  assembly.setExploded(true);
  const expected = startWorld.clone().add(new THREE.Vector3(0, 0.5, -0.24));
  assert.ok(mount.getWorldPosition(new THREE.Vector3()).distanceTo(expected) < 1e-9);
  assembly.setExploded(true);
  assert.ok(mount.getWorldPosition(new THREE.Vector3()).distanceTo(expected) < 1e-9);
  assembly.setExploded(false);
  assert.ok(mount.position.distanceTo(initial) < 1e-9);
  assert.ok(mount.quaternion.equals(rotation));
  assembly.setSelection({ Batteries: { id: 'unverified' } });
  assert.equal(mount.children[0].visible, true);
  disposeModelResources(root);
});

for (const [profile, url] of Object.entries(BLENDER_MODELS)) {
  test(`${profile} exported GLB parses through Three.js and exposes solid, selectable mount geometry`, async () => {
    const file = await readFile(new URL(`../apps/web/public${url}`, import.meta.url));
    const bytes = file.buffer.slice(file.byteOffset, file.byteOffset + file.byteLength);
    const { scene: root } = await new GLTFLoader().parseAsync(bytes, '');
    const bounds = new THREE.Box3().setFromObject(root);
    const size = bounds.getSize(new THREE.Vector3());
    assert.ok(size.x > 1.1 && size.x < 2.3, `length ${size.x}`);
    assert.ok(size.y > 1 && size.y < 1.7, `height ${size.y}`);
    assert.ok(size.z > 0.2 && size.z < 0.9, `width ${size.z}`);
    assert.ok(Math.abs(bounds.min.y) < 0.06, `floor ${bounds.min.y}`);
    for (const name of [
      'BatteryMount',
      'ControllerMount',
      'MotorMount',
      'FrontWheel',
      'RearWheel',
    ]) {
      const mount = root.getObjectByName(name);
      assert.ok(mount, `${name} missing`);
      assert.equal(new THREE.Box3().setFromObject(mount).isEmpty(), false, `${name} empty`);
    }
    root.traverse((object) => {
      if (!object.isMesh) return;
      assert.ok(object.geometry.attributes.normal);
      assert.ok(object.matrixWorld.elements.every(Number.isFinite));
      for (const number of object.geometry.attributes.position.array)
        assert.ok(Number.isFinite(number));
    });
    const assembly = createBlenderAssembly(root, (part) => PartPreviews.createModel(part, THREE));
    const part = CATALOG.find(
      (entry) => PartPreviews.describe(entry).model && entry.category === 'Controllers',
    );
    assert.ok(part);
    assembly.setSelection({ Controllers: part });
    const controller = assembly.mounts.find((mount) => mount.category === 'Controllers');
    assert.equal(controller.preview.root.userData.selectedPartId, part.id);
    assert.ok(controller.stock.every((child) => !child.visible));
    const previewBounds = new THREE.Box3().setFromObject(controller.preview.root);
    assert.equal(previewBounds.isEmpty(), false);
    const authoredBounds = new THREE.Box3();
    controller.stock.forEach((child) =>
      authoredBounds.union(new THREE.Box3().setFromObject(child)),
    );
    assert.ok(
      authoredBounds.expandByScalar(0.00001).containsBox(previewBounds),
      'selected component exceeds visual envelope',
    );
    assembly.setSelection({});
    assert.equal(controller.preview, null);
    assert.ok(controller.stock.every((child) => child.visible));
    assembly.dispose();
    disposeModelResources(root);
  });
}
