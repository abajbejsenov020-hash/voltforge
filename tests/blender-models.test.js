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

test('owned decoded bitmaps close once while images shared with protected scene textures stay open', () => {
  let closed = 0;
  const image = { close: () => closed++ };
  const owned = new THREE.Texture(image),
    protectedTexture = new THREE.Texture(image);
  const protectedMaterial = new THREE.MeshStandardMaterial({ map: protectedTexture });
  const root = solid();
  root.children[0].material.map = owned;
  root.add(new THREE.Mesh(new THREE.BoxGeometry(), protectedMaterial));
  disposeModelResources(root, new Set([protectedMaterial]));
  assert.equal(closed, 0);
  disposeModelResources(root);
  disposeModelResources(root);
  assert.equal(closed, 1);
});

test('exploded mounts lift before sliding, reverse without drift, and leave the chassis in place', () => {
  const root = new THREE.Group();
  root.rotation.x = -Math.PI / 2;
  const chassis = solid();
  chassis.name = 'Chassis';
  const battery = solid();
  battery.name = 'BatteryMount';
  battery.position.set(0.2, -0.3, 0.7);
  battery.rotation.z = 0.4;
  root.add(chassis, battery);
  const initial = battery.position.clone();
  const rotation = battery.quaternion.clone();
  const start = battery.getWorldPosition(new THREE.Vector3());
  const assembly = createBlenderAssembly(root, () => {
    throw new Error('unverified');
  });
  assert.equal(assembly.canExplode, true);
  assembly.setExploded(0.3);
  const lifted = battery.getWorldPosition(new THREE.Vector3());
  assert.ok(lifted.y > start.y);
  assert.ok(Math.abs(lifted.z - start.z) < 1e-9);
  assembly.setExploded(1);
  const extended = battery.getWorldPosition(new THREE.Vector3());
  assert.ok(extended.y > lifted.y);
  assert.ok(extended.z > start.z);
  assembly.setExploded(0.3);
  assert.ok(battery.getWorldPosition(new THREE.Vector3()).distanceTo(lifted) < 1e-9);
  assembly.setExploded(0);
  assert.ok(battery.position.distanceTo(initial) < 1e-9);
  assert.ok(battery.quaternion.equals(rotation));
  assert.deepEqual(chassis.position.toArray(), [0, 0, 0]);
  assert.deepEqual(assembly.setSelection({ Batteries: { id: 'unverified' } }), {
    Batteries: false,
  });
  assert.equal(battery.children[0].visible, true);
  disposeModelResources(root);
});

async function loadVehicle(url) {
  const file = await readFile(new URL(`../apps/web/public${url}`, import.meta.url));
  const bytes = file.buffer.slice(file.byteOffset, file.byteOffset + file.byteLength);
  // Node preserves geometry/material slots. The browser tests decode embedded images.
  const loader = new GLTFLoader().register(() => ({
    name: 'NodeGeometryTextures',
    loadTexture: () => Promise.resolve(new THREE.Texture()),
  }));
  const { scene } = await loader.parseAsync(bytes, '');
  return scene;
}

function select(...ids) {
  return Object.fromEntries(
    ids.map((id) => {
      const part = CATALOG.find((entry) => entry.id === id);
      assert.ok(part, id);
      return [part.category, part];
    }),
  );
}

for (const [profile, ids] of [
  ['kukirin-g4', ['p4', 'p291', 'p308', 'p296', 'p299', 'p304']],
  ['surron-lbx', ['p169', 'p291', 'p179', 'p297', 'p303', 'p304']],
]) {
  test(`${profile} replaces selected geometry, keeps adjacent stock hardware, and resets through disassembly`, async () => {
    const root = await loadVehicle(BLENDER_MODELS[profile]);
    const assembly = createBlenderAssembly(root, (part) => PartPreviews.createModel(part, THREE));
    const selection = select(...ids);
    const chosenMounts = assembly.mounts.filter((mount) => selection[mount.category]);
    const removed = new Set(chosenMounts.flatMap((mount) => mount.stock));
    const original = new Map();
    root.traverse((object) => {
      if (object.isMesh) original.set(object, object.visible);
    });
    const installed = assembly.setSelection(selection, { motorCount: 1 });
    assert.deepEqual(
      installed,
      Object.fromEntries(Object.keys(selection).map((name) => [name, true])),
    );
    for (const [mesh, visible] of original)
      assert.equal(mesh.visible, visible && !removed.has(mesh));
    const chassis = root.getObjectByName('Chassis');
    const chassisStart = chassis.getWorldPosition(new THREE.Vector3());
    assembly.setExploded(0.5);
    assembly.setExploded(1);
    assert.ok(chassis.getWorldPosition(new THREE.Vector3()).equals(chassisStart));
    const battery = assembly.mounts.find(({ category }) => category === 'Batteries');
    const controller = assembly.mounts.find(({ category }) => category === 'Controllers');
    const packPosition = battery.preview.root.getWorldPosition(new THREE.Vector3());
    const controllerPosition = controller.preview.root.getWorldPosition(new THREE.Vector3());
    assert.ok(packPosition.z > 0.3 && controllerPosition.z < -0.3);
    for (const mount of chosenMounts) {
      assert.equal(mount.preview.root.parent, mount.node);
      assert.equal(mount.preview.root.visible, true);
      assert.equal(mount.preview.root.userData.selectedPartId, selection[mount.category].id);
    }
    const restored = { ...selection };
    delete restored.Controllers;
    assert.equal(assembly.setSelection(restored, { motorCount: 1 }).Motors, true);
    assert.equal(controller.preview, null);
    assert.ok(controller.stock.every((mesh) => mesh.visible));
    assembly.setExploded(0);
    assembly.setSelection({});
    for (const [mesh, visible] of original) assert.equal(mesh.visible, visible);
    assert.ok(chosenMounts.every((mount) => mount.preview === null));
    assembly.dispose();
    disposeModelResources(root);
  });
}

test('a dual-hub scooter replaces both axle motors without adding duplicate tires', async () => {
  const root = await loadVehicle(BLENDER_MODELS['kukirin-g4-ultra']);
  const assembly = createBlenderAssembly(root, (part) => PartPreviews.createModel(part, THREE));
  const selection = select('p2');
  const motor = assembly.mounts.find(({ category }) => category === 'Motors');
  assert.deepEqual(assembly.setSelection(selection, { motorCount: 1 }), { Motors: false });
  assert.ok(motor.stock.every((mesh) => mesh.visible));
  assert.deepEqual(assembly.setSelection(selection, { motorCount: 2 }), { Motors: true });
  assert.ok(motor.stock.every((mesh) => !mesh.visible));
  assert.equal(motor.preview.root.children.length, 2);
  root.updateMatrixWorld(true);
  const centers = motor.preview.root.children.map((child) =>
    new THREE.Box3().setFromObject(child).getCenter(new THREE.Vector3()),
  );
  assert.ok(centers[0].x < -0.45 && centers[1].x > 0.45);
  motor.preview.root.traverse((mesh) => assert.equal(mesh.userData.tireGeometry, undefined));
  assert.deepEqual(assembly.setSelection(select('p169'), { motorCount: 2 }), { Motors: false });
  assert.ok(motor.stock.every((mesh) => mesh.visible));
  assembly.dispose();
  disposeModelResources(root);
});

for (const [profile, url] of Object.entries(BLENDER_MODELS)) {
  test(`${profile} exported GLB parses through Three.js and exposes solid, selectable mount geometry`, async () => {
    const root = await loadVehicle(url);
    const bounds = new THREE.Box3().setFromObject(root);
    const size = bounds.getSize(new THREE.Vector3());
    // The expanded catalog includes junior motorcycles and wider road-legal mirrors.
    assert.ok(size.x > 0.6 && size.x < 2.6, `length ${size.x}`);
    assert.ok(size.y > 0.4 && size.y < 1.85, `height ${size.y}`);
    assert.ok(size.z > 0.2 && size.z < 1.2, `width ${size.z}`);
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
