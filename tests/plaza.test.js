import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { createChargingPlaza } from '../apps/web/src/scene/plaza.js';

function fixture(t) {
  const previousDocument = globalThis.document,
    previousObserver = globalThis.ResizeObserver;
  let disconnected = 0;
  const context = {
    createImageData: (w, h) => ({ data: new Uint8ClampedArray(w * h * 4) }),
    putImageData() {},
    strokeRect() {},
    fillRect() {},
    fillText() {},
    createRadialGradient: () => ({ addColorStop() {} }),
  };
  globalThis.document = { createElement: () => ({ getContext: () => context }) };
  globalThis.ResizeObserver = class {
    observe() {}
    disconnect() {
      disconnected++;
    }
  };
  t.after(() => {
    if (previousDocument === undefined) delete globalThis.document;
    else globalThis.document = previousDocument;
    if (previousObserver === undefined) delete globalThis.ResizeObserver;
    else globalThis.ResizeObserver = previousObserver;
  });
  const canvas = { dataset: {}, getBoundingClientRect: () => ({ width: 1000 }) };
  const scene = new THREE.Scene(),
    pending = [];
  const loader = {
    loadAsync(url) {
      return new Promise((resolve, reject) => pending.push({ url, resolve, reject }));
    },
  };
  const plaza = createChargingPlaza({ scene, canvas, loader, onChange() {} });
  return { plaza, scene, canvas, pending, disconnected: () => disconnected };
}
function vehicle() {
  const root = new THREE.Group();
  root.add(new THREE.Mesh(new THREE.BoxGeometry(1.6, 1.2, 0.4), new THREE.MeshStandardMaterial()));
  return root;
}
async function flush() {
  await Promise.resolve();
  await Promise.resolve();
}

test('plaza has finite batched architecture, meter-scale parked vehicles and owned resource disposal', async (t) => {
  const f = fixture(t),
    root = f.scene.getObjectByName('City charging plaza');
  assert.ok(root);
  const meshes = root.children.filter((child) => child.isMesh);
  assert.ok(meshes.length < 30, `static draw-call budget: ${meshes.length}`);
  const bounds = new THREE.Box3().setFromObject(root);
  assert.ok(bounds.min.toArray().concat(bounds.max.toArray()).every(Number.isFinite));
  assert.ok(bounds.max.y > 8 && bounds.max.x < 20);
  assert.match(f.pending[0].url, /dualtron-thunder-3/);
  assert.match(f.pending[1].url, /sur-ron-ultra-bee/);
  const resources = new Set();
  root.traverse((object) => {
    if (!object.isMesh) return;
    resources.add(object.geometry);
    resources.add(object.material);
    for (const value of Object.values(object.material)) if (value?.isTexture) resources.add(value);
  });
  const releases = new Map();
  for (const resource of resources)
    resource.addEventListener('dispose', () =>
      releases.set(resource, (releases.get(resource) || 0) + 1),
    );
  for (const pending of f.pending) pending.resolve({ scene: vehicle() });
  await flush();
  assert.equal(f.canvas.dataset.plazaState, 'ready');
  assert.equal(f.canvas.dataset.plazaVehicles, '2');
  for (const name of ['Parked Dualtron Thunder 3', 'Parked Sur-Ron Ultra Bee']) {
    const box = new THREE.Box3().setFromObject(root.getObjectByName(name));
    assert.ok(Math.abs(box.min.y) < 1e-6, 'parked tires contact floor');
    assert.ok(box.getSize(new THREE.Vector3()).x > 1.4, 'real meter scale');
  }
  f.plaza.dispose();
  f.plaza.dispose();
  assert.equal(f.scene.children.length, 0);
  assert.equal(f.disconnected(), 1);
  assert.equal(f.canvas.dataset.plazaState, undefined);
  for (const resource of resources) assert.equal(releases.get(resource), 1, resource.type);
});

test('vehicles arriving after a setting switch are released and cannot restore stale scene state', async (t) => {
  const f = fixture(t);
  f.plaza.dispose();
  let released = 0;
  for (const pending of f.pending) {
    const root = vehicle(),
      mesh = root.children[0];
    mesh.geometry.addEventListener('dispose', () => released++);
    mesh.material.addEventListener('dispose', () => released++);
    pending.resolve({ scene: root });
  }
  await flush();
  assert.equal(released, 4);
  assert.equal(f.scene.children.length, 0);
  assert.equal(f.canvas.dataset.plazaState, undefined);
});

test('an empty or missing parked model reports partial status while retaining the architecture', async (t) => {
  const f = fixture(t);
  f.pending[0].resolve({ scene: new THREE.Group() });
  f.pending[1].resolve({ scene: vehicle() });
  await flush();
  assert.equal(f.canvas.dataset.plazaState, 'partial');
  assert.equal(f.canvas.dataset.plazaVehicles, '1');
  assert.ok(f.scene.getObjectByName('City charging plaza'));
  f.plaza.dispose();
});
