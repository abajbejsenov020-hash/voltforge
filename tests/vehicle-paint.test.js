import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { Texture } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { normalizePaint } from '@voltforge/shared/build';
import { createVehiclePaint } from '../apps/web/src/scene/vehicle-paint.js';

async function vehicle(asset) {
  const file = await readFile(new URL(`../apps/web/public/models/${asset}.glb`, import.meta.url));
  const loader = new GLTFLoader().register(() => ({
    name: 'NodeGeometryTextures',
    loadTexture: () => Promise.resolve(new Texture()),
  }));
  const { scene } = await loader.parseAsync(
    file.buffer.slice(file.byteOffset, file.byteOffset + file.byteLength),
    '',
  );
  return scene;
}

function finish(root, group, name) {
  return root.getObjectByName(group).children.find((mesh) => mesh.material?.name === name);
}

test('paint accepts only supported zones and six-digit hex colors', () => {
  assert.deepEqual(normalizePaint(), {});
  assert.deepEqual(normalizePaint({ frame: '#98B0AE', seat: '#171717', rims: 'orange' }), {
    frame: '#98b0ae',
  });
});

test('KuKirin paints the deck and both rims and preserves factory controls, tires, and rotors', async () => {
  const root = await vehicle('kukirin-g4');
  const { zones, colors, setPaint, dispose } = createVehiclePaint(root);
  assert.deepEqual(zones, ['frame', 'deck', 'rims']);
  const deck = finish(root, 'Chassis', 'G4 graphite grey satin powder coat');
  const stockDeck = deck.material;
  const stem = finish(root, 'Steering', stockDeck.name);
  assert.equal(stem.material, stockDeck);
  assert.equal(colors.deck, `#${stockDeck.color.getHexString()}`);
  const wheels = ['FrontWheel', 'RearWheel'];
  const rims = wheels.map((wheel) => finish(root, wheel, 'Dark anodized aluminium'));
  const tiresAndRotors = wheels.flatMap((wheel) =>
    ['Tire rubber', 'Brake rotor steel'].map((name) => finish(root, wheel, name)),
  );
  const stockProtected = tiresAndRotors.map((mesh) => mesh.material);
  setPaint({ deck: '#b02044', rims: '#217c83' });
  assert.equal(deck.material.color.getHexString(), 'b02044');
  for (const rim of rims) assert.equal(rim.material.color.getHexString(), '217c83');
  assert.equal(stem.material, stockDeck);
  assert.deepEqual(
    tiresAndRotors.map((mesh) => mesh.material),
    stockProtected,
  );
  setPaint({ rims: '#217c83' });
  assert.equal(deck.material, stockDeck);
  dispose();
});

test('Light Bee independently paints the frame, fork, swingarm and panels', async () => {
  const root = await vehicle('surron-lbx');
  const paint = createVehiclePaint(root);
  assert.deepEqual(paint.zones, ['frame', 'body', 'fork', 'swingarm', 'rims']);
  const frame = finish(root, 'Chassis', 'Cast graphite aluminium');
  const fork = finish(root, 'Fork', 'Cast graphite aluminium');
  const swingarm = finish(root, 'RearSuspension', 'Cast graphite aluminium');
  const body = finish(root, 'Bodywork', 'Satin black polymer');
  const decal = finish(root, 'Bodywork', 'Fluorescent yellow green wrap');
  const stock = [frame, fork, swingarm, body, decal].map((mesh) => mesh.material);
  paint.setPaint({ frame: '#69308a', fork: '#a6b761', body: '#274aa8', swingarm: '#d7461c' });
  assert.deepEqual(
    [frame, fork, body, swingarm].map((mesh) => mesh.material.color.getHexString()),
    ['69308a', 'a6b761', '274aa8', 'd7461c'],
  );
  assert.equal(decal.material, stock[4]);
  paint.dispose();
  assert.deepEqual(
    [frame, fork, swingarm, body, decal].map((mesh) => mesh.material),
    stock,
  );
});

test('Dualtron deck paint preserves the printed grip texture and red trim', async () => {
  const root = await vehicle('expansion/premium/dualtron-thunder-3');
  const paint = createVehiclePaint(root);
  const grip = finish(root, 'Chassis', 'Exact-model printed rubber deck');
  const redTrim = finish(root, 'Chassis', 'red');
  const materials = [grip.material, redTrim.material];
  paint.setPaint({ deck: '#355673', frame: '#217c83' });
  assert.ok(materials[0].map);
  assert.deepEqual([grip.material, redTrim.material], materials);
  paint.dispose();
});
