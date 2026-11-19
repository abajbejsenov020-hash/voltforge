import assert from 'node:assert/strict';
import test from 'node:test';
import { BoxGeometry, Group, Mesh, MeshStandardMaterial, Object3D } from 'three';
import { createBuild } from '@voltforge/shared/build';
import { normalizeCockpit } from '@voltforge/shared/cockpit';
import { createBuildValidator } from '../apps/api/src/validation.js';
import { createVehicleCockpit } from '../apps/web/src/scene/vehicle-cockpit.js';

function cockpitFixture() {
  const root = new Group();
  const steering = new Group();
  root.add(steering);
  const mount = (name, z) => {
    const point = new Object3D();
    point.name = 'VF_Cockpit_' + name;
    point.position.set(0, 1.2, z);
    steering.add(point);
  };
  const part = (tag, z, length) => {
    const mesh = new Mesh(new BoxGeometry(0.035, 0.036, length), new MeshStandardMaterial());
    mesh.userData.vfCockpit = tag;
    mesh.position.set(0, 1.2, z);
    steering.add(mesh);
    return mesh;
  };
  mount('Center', 0);
  mount('GripA', 0.27);
  mount('GripB', -0.27);
  return {
    root,
    bar: part('bar', 0, 0.66),
    gripA: part('gripA', 0.27, 0.12),
    gripB: part('gripB', -0.27, 0.12),
    brakeA: part('controlA', 0.195, 0.014),
    throttleB: part('controlB', -0.195, 0.014),
    hose: part('cable', 0, 0.015),
  };
}

test('cockpit options retain a supported shape, width and rider-selected colors through API validation', () => {
  const cockpit = { grip: 'diamond', color: 'teal', bar: 'high-rise', width: 760 };
  assert.deepEqual(normalizeCockpit(cockpit), cockpit);
  assert.deepEqual(normalizeCockpit({ color: 'red', width: 800, bar: 'toString' }), {});
  const validate = createBuildValidator([], []);
  const build = createBuild();
  assert.ok(!Object.hasOwn(validate(build), 'cockpit'));
  assert.deepEqual(validate({ ...build, cockpit }).cockpit, cockpit);
  for (const invalid of [{ width: 690 }, { bar: 'flat', width: '760' }, { grip: 'stock' }])
    assert.throws(() => validate({ ...build, cockpit: invalid }), { code: 'INVALID_BUILD' });
});

test('changing width moves both grips and side controls, and restoring stock resets original geometry', () => {
  const { root, bar, gripA, gripB, brakeA, throttleB, hose } = cockpitFixture();
  const cockpit = createVehicleCockpit(root);
  const generated = root.getObjectByName('CustomCockpit');
  assert.equal(cockpit.width, 660);
  cockpit.apply({ bar: 'high-rise', width: 760 });
  assert.equal(cockpit.width, 760);
  assert.equal(bar.visible, false);
  assert.equal(hose.visible, false);
  assert.ok(generated.getObjectByName('Re-routed brake hose A')?.isMesh);
  assert.ok(Math.abs(gripA.position.z - gripB.position.z - 0.64) < 0.001);
  assert.ok(Math.abs(brakeA.position.z - 0.245) < 0.001);
  assert.ok(Math.abs(throttleB.position.z + 0.245) < 0.001);
  assert.ok(gripA.position.y > 1.24);
  assert.ok(generated.getObjectByName('Replacement handlebar A')?.isMesh);
  cockpit.apply({ grip: 'waffle', color: 'teal' });
  assert.equal(bar.visible, true);
  assert.equal(hose.visible, true);
  assert.equal(gripA.visible, false);
  assert.equal(gripB.visible, false);
  assert.equal(brakeA.position.z, 0.195);
  assert.equal(generated.getObjectByName('Grip sleeve').material.color.getHexString(), '1b9f98');
  assert.ok(generated.getObjectByName('Raised waffle grip tread')?.isInstancedMesh);
  cockpit.apply({});
  assert.equal(cockpit.width, 660);
  assert.equal(bar.visible, true);
  assert.equal(gripA.visible, true);
  assert.equal(generated.children.length, 0);
  cockpit.dispose();
  assert.ok(!root.getObjectByName('CustomCockpit'));
});
