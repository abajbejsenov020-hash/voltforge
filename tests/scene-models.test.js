import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { CATALOG } from '@voltforge/shared/catalog';
import { COMPONENT_REFERENCES } from '@voltforge/shared/appearances';
import { getVehicleVisual } from '@voltforge/shared/visuals';
import { PartPreviews } from '../apps/web/src/scene/components/index.js';
import { buildComponentModel } from '../apps/web/src/scene/components/model-builder.js';
import { build as buildG4 } from '../apps/web/src/scene/models/g4Scooter.js';
import { build as buildCommuter } from '../apps/web/src/scene/models/commuterScooter.js';
import { build as buildScooter } from '../apps/web/src/scene/models/scooter.js';
import { build as buildBicycle } from '../apps/web/src/scene/models/bicycle.js';
import { build as buildLightBee } from '../apps/web/src/scene/models/lightBee.js';

function finiteGeometry(root, label) {
  root.updateMatrixWorld(true);
  let meshCount = 0;
  root.traverse((object) => {
    assert.ok(object.matrixWorld.elements.every(Number.isFinite), `${label}: invalid transform`);
    if (!object.isMesh) return;
    meshCount++;
    const position = object.geometry.attributes.position;
    assert.ok(position?.count > 0, `${label}: empty geometry`);
    for (const attribute of [position, object.geometry.attributes.normal, object.instanceMatrix]) {
      if (!attribute) continue;
      for (const number of attribute.array) {
        if (!Number.isFinite(number)) assert.fail(`${label}: nonfinite geometry attribute`);
      }
    }
  });
  assert.ok(meshCount > 0, `${label}: no renderable meshes`);
  const bounds = new THREE.Box3().setFromObject(root);
  const size = bounds.getSize(new THREE.Vector3());
  assert.equal(bounds.isEmpty(), false, `${label}: empty bounds`);
  assert.ok(
    [size.x, size.y, size.z].every((number) => Number.isFinite(number) && number > 0),
    `${label}: degenerate bounds`,
  );
  return { bounds, size };
}

function disposeGeometry(root) {
  const geometries = new Set();
  const materials = new Set();
  root.traverse((object) => {
    if (object.geometry) geometries.add(object.geometry);
    for (const material of [object.material].flat().filter(Boolean)) materials.add(material);
  });
  for (const geometry of geometries) geometry.dispose();
  for (const material of materials) material.dispose();
}

test('all 94 photographed products build finite, nonempty geometry through the public preview interface', () => {
  const products = CATALOG.filter((part) => COMPONENT_REFERENCES[part.id]);
  assert.equal(products.length, 94);
  for (const part of products) {
    const model = PartPreviews.createModel(part, THREE);
    try {
      finiteGeometry(model.root, `${part.id} ${part.brand} ${part.name}`);
      const appearance = PartPreviews.describe(part);
      assert.equal(model.root.userData.family, appearance.family, part.id);
      assert.ok(appearance.reference, `${part.id}: missing source photograph`);
      const markup = PartPreviews.markup(part, true);
      assert.ok(
        markup.includes(appearance.reference),
        `${part.id}: inspector uses the wrong reference`,
      );
      assert.ok(
        markup.includes('Photo-guided 3D approximation'),
        `${part.id}: missing fidelity disclosure`,
      );
    } finally {
      model.dispose();
    }
  }
});

test('the extracted component builder releases owned mesh resources when its preview is replaced', () => {
  const part = CATALOG.find((entry) => entry.brand === 'Fardriver' && entry.name === 'ND72260');
  const model = buildComponentModel(part, THREE, PartPreviews.describe);
  const geometries = new Set();
  const materials = new Set();
  model.root.traverse((object) => {
    if (object.geometry) geometries.add(object.geometry);
    for (const material of [object.material].flat().filter(Boolean)) materials.add(material);
  });
  const released = new Set();
  for (const resource of [...geometries, ...materials]) {
    resource.addEventListener('dispose', () => released.add(resource));
  }
  model.dispose();
  assert.ok(geometries.size > 0 && materials.size > 0);
  assert.equal(released.size, geometries.size + materials.size);
});

test('unidentified planning entries do not acquire a fabricated product model or photograph', () => {
  const template = CATALOG.find((part) => part.template && !COMPONENT_REFERENCES[part.id]);
  assert.ok(template);
  assert.equal(PartPreviews.describe(template).reference, null);
  assert.ok(PartPreviews.markup(template).includes('Exact part needed'));
  assert.ok(!PartPreviews.markup(template).includes('<canvas'));
  assert.ok(!PartPreviews.markup(template).includes('<img'));
  assert.throws(
    () => PartPreviews.createModel(template, THREE),
    /Exact product reference required/,
  );
});

// The extracted vehicle builders accept geometry helpers as their public input.
// Use real Three primitives here, while leaving canvas textures and WebGL visual
// checks to the browser suite. This exercises each builder without the viewer.
function vehicleContext(visual, parts = {}) {
  const model = new THREE.Group();
  const wheels = [];
  const materialNames = [
    'paint',
    'frame',
    'black',
    'rubber',
    'tread',
    'grip',
    'alloy',
    'silver',
    'darkMetal',
    'accent',
    'brake',
    'red',
    'lens',
    'screen',
    'cable',
    'label',
    'deck',
    'screenFace',
  ];
  const mat = (color, metalness = 0, roughness = 0.6, extra = {}) =>
    new THREE.MeshStandardMaterial({ color, metalness, roughness, ...extra });
  const M = Object.fromEntries(materialNames.map((name) => [name, mat(0x777777)]));
  const context = { T: THREE, M, model, visual, parts, wheels, mat };
  const mesh = (geometry, material, parent = model) => {
    assert.ok(material?.isMaterial, 'Builder requested an undeclared material');
    const value = new THREE.Mesh(geometry, material);
    parent.add(value);
    return value;
  };
  const position = (object, point) => {
    object.position.set(...point);
    return object;
  };
  const group = (name, parent = model) => {
    const value = new THREE.Group();
    value.name = name;
    parent.add(value);
    return value;
  };
  const cylinder = (
    r1,
    r2,
    length,
    material,
    point = [0, 0, 0],
    parent = model,
    axis = 'y',
    segments = 24,
  ) => {
    const value = position(
      mesh(new THREE.CylinderGeometry(r1, r2, length, segments), material, parent),
      point,
    );
    if (axis === 'z') value.rotation.x = Math.PI / 2;
    if (axis === 'x') value.rotation.z = Math.PI / 2;
    return value;
  };
  const rod = (start, end, radius, material, parent = model) => {
    const from = new THREE.Vector3(...start);
    const to = new THREE.Vector3(...end);
    const value = cylinder(radius, radius, from.distanceTo(to), material, [0, 0, 0], parent);
    value.position.copy(from).lerp(to, 0.5);
    value.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), to.sub(from).normalize());
    return value;
  };
  Object.assign(context, {
    mesh,
    group,
    cylinder,
    rod,
    box: (width, height, depth, material, point = [0, 0, 0], parent = model) =>
      position(mesh(new THREE.BoxGeometry(width, height, depth), material, parent), point),
    torus: (radius, thickness, material, point = [0, 0, 0], parent = model) =>
      position(mesh(new THREE.TorusGeometry(radius, thickness, 8, 32), material, parent), point),
    tube: (points, radius, material, parent = model, segments = 24) =>
      mesh(
        new THREE.TubeGeometry(
          new THREE.CatmullRomCurve3(points.map((point) => new THREE.Vector3(...point))),
          segments,
          radius,
          8,
          false,
        ),
        material,
        parent,
      ),
    bolt: (x, y, z, parent = model, radius = 0.006) =>
      cylinder(radius, radius, 0.007, M.silver, [x, y, z], parent, 'z', 6),
    lathe: (profile, material, parent = model) =>
      mesh(
        new THREE.LatheGeometry(
          profile.map((point) => new THREE.Vector2(...point)),
          24,
        ),
        material,
        parent,
      ),
    shock: (start, end, radius = 0.027, parent = model, material = M.accent) =>
      rod(start, end, radius, material, parent),
    wheel: (x, y, radius, width, motor, parent = model) => {
      wheels.push({ x, y, radius, width, motor });
      return position(mesh(new THREE.TorusGeometry(radius, width / 2, 12, 32), M.rubber, parent), [
        x,
        y,
        0,
      ]);
    },
    fender: (x, y, radius, width, parent = model) =>
      position(
        mesh(new THREE.TorusGeometry(radius + 0.018, width / 8, 8, 24, Math.PI), M.black, parent),
        [x, y, 0],
      ),
    grips: (x, y, halfWidth, parent = model) => {
      const value = group('grips', parent);
      for (const side of [-1, 1])
        cylinder(0.019, 0.019, 0.12, M.grip, [x, y, side * halfWidth], value, 'z');
      return value;
    },
    decal: (text, width, height, point, rotation = [0, 0, 0], parent = model) => {
      const value = position(mesh(new THREE.PlaneGeometry(width, height), M.label, parent), point);
      value.rotation.set(...rotation);
      return value;
    },
    texture: () => new THREE.Texture(),
    panel: (points, depth, material, z = 0, parent = model) => {
      const shape = new THREE.Shape(points.map((point) => new THREE.Vector2(...point)));
      return position(
        mesh(new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: false }), material, parent),
        [0, 0, z - depth / 2],
      );
    },
  });
  return context;
}

test('all extracted vehicle builders construct finite geometry and expose battery/controller envelopes', () => {
  const cases = [
    [buildG4, 'KuKirin G4', 'scooter'],
    [buildCommuter, 'Segway Ninebot Max G2', 'scooter'],
    [buildScooter, 'KuKirin G2 Max', 'scooter'],
    [buildScooter, 'Ausom DT2 Pro', 'scooter'],
    [buildScooter, 'NAMI Klima', 'scooter'],
    [buildScooter, 'Dualtron Thunder 3', 'scooter'],
    [buildBicycle, 'Trek Marlin+', 'bike'],
    [buildBicycle, 'Fiido M1 Pro', 'bike'],
    [buildBicycle, 'Fiido C11', 'bike'],
    [buildBicycle, 'Talaria Sting', 'bike'],
    [buildLightBee, 'Sur-Ron Light Bee X', 'bike'],
  ];
  for (const [build, name, type] of cases) {
    const context = vehicleContext(getVehicleVisual(name, type));
    try {
      build(context);
      const { size } = finiteGeometry(context.model, name);
      assert.ok(size.x > 0.9 && size.x < 3, `${name}: implausible length`);
      assert.ok(size.y > 0.6 && size.y < 2.5, `${name}: implausible height`);
      assert.equal(context.wheels.length, 2, `${name}: missing a wheel`);
      assert.ok(context.batteryGroup?.parent, `${name}: missing battery envelope`);
      assert.ok(context.controllerGroup?.parent, `${name}: missing controller envelope`);
      if (name === 'KuKirin G4')
        assert.deepEqual(
          context.wheels.map((wheel) => wheel.motor),
          [true, false],
        );
    } finally {
      disposeGeometry(context.model);
    }
  }
});

test('bicycle motor location follows the selected front-hub, rear-hub, or mid-drive part', () => {
  for (const [motorName, expected] of [
    ['Front Hub Motor', [false, true]],
    ['Rear Hub Motor', [true, false]],
    ['Mid-drive Motor', [false, false]],
  ]) {
    const context = vehicleContext(getVehicleVisual('Trek Marlin+', 'bike'), {
      Motors: { name: motorName },
    });
    try {
      buildBicycle(context);
      finiteGeometry(context.model, motorName);
      assert.deepEqual(
        context.wheels.map((wheel) => wheel.motor),
        expected,
        motorName,
      );
    } finally {
      disposeGeometry(context.model);
    }
  }
});

test('the vehicle viewer module can be imported before creating a browser renderer', async () => {
  const viewer = await import('../apps/web/src/scene/vehicle-scene.js');
  assert.equal(typeof viewer.createVehicleScene, 'function');
});
