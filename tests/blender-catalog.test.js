import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, statSync } from 'node:fs';
import { createHash } from 'node:crypto';
import refs from '../apps/web/src/data/vehicle-references.json' with { type: 'json' };
import {
  BLENDER_VEHICLES,
  BLENDER_MODELS,
  blenderModelKey,
} from '../apps/web/src/scene/blender-models.js';
import { VEHICLE_INDEX } from '@voltforge/shared/vehicles';
import { vehicleReference } from '../apps/web/src/data/vehicle-library.js';

test('every pictured vehicle resolves to its own completed Blender entry', () => {
  assert.equal(BLENDER_VEHICLES.length, 60);
  assert.equal(new Set(BLENDER_VEHICLES.map((entry) => entry.name)).size, 60);
  assert.equal(new Set(BLENDER_VEHICLES.map((entry) => entry.key)).size, 60);
  assert.equal(Object.keys(BLENDER_MODELS).length, 60);
  for (const reference of refs) {
    const entry = BLENDER_VEHICLES.find((item) => item.name === reference.name);
    assert.ok(entry, reference.name);
    assert.equal(blenderModelKey(reference.name), entry.key, reference.name);
    assert.equal(BLENDER_MODELS[entry.key], entry.url, reference.name);
    assert.equal(vehicleReference(reference.name)?.name, reference.name);
  }
  assert.equal(blenderModelKey('surron lbx'), 'surron-lbx');
  assert.equal(blenderModelKey('Kugoo Kirin G4'), 'kukirin-g4');
});

test('unpictured indexed variants never silently borrow a related Blender model', () => {
  const pictured = new Set(refs.map((ref) => ref.name));
  for (const vehicle of VEHICLE_INDEX.filter((vehicle) => !pictured.has(vehicle.name)))
    assert.equal(blenderModelKey(vehicle.name), null, vehicle.name);
  assert.equal(blenderModelKey('My custom prototype'), null);
});

test('all completed catalog entries include local GLBs, native sources and actual Blender geometry', () => {
  const hashes = new Map();
  for (const entry of BLENDER_VEHICLES) {
    const path = new URL('../apps/web/public' + entry.url, import.meta.url);
    const bytes = readFileSync(path);
    assert.equal(bytes.readUInt32LE(0), 0x46546c67, entry.name);
    assert.equal(bytes.readUInt32LE(4), 2, entry.name);
    assert.equal(bytes.readUInt32LE(8), bytes.length, entry.name);
    assert.equal(bytes.length, entry.bytes, entry.name + ' manifest size');
    assert.ok(bytes.length < 20 * 1024 * 1024, entry.name + ' web file budget');
    const json = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)).toString());
    assert.ok(json.asset.generator.toLowerCase().includes('blender'), entry.name);
    assert.ok(json.meshes.length > 5, entry.name + ' missing solid assemblies');
    for (const name of ['FrontWheel', 'RearWheel', 'BatteryMount', 'ControllerMount', 'MotorMount'])
      assert.ok(
        json.nodes.some((node) => node.name === name),
        entry.name + ' ' + name,
      );
    for (const accessor of json.accessors.filter((item) => item.type === 'VEC3' && item.min))
      assert.ok(
        accessor.min.concat(accessor.max).every(Number.isFinite),
        entry.name + ' finite bounds',
      );
    assert.ok(
      statSync(new URL('../' + entry.nativeSource, import.meta.url)).size > 10000,
      entry.name + ' editable source',
    );
    const hash = createHash('sha256').update(bytes).digest('hex');
    const previous = hashes.get(hash);
    if (previous)
      assert.equal(
        previous.image,
        entry.image,
        entry.name + ' unrelated image must not be a copied binary',
      );
    hashes.set(hash, entry);
  }
});
