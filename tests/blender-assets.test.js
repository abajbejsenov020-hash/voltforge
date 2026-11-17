import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, statSync } from 'node:fs';
import { Matrix4, Box3, Vector3, Quaternion } from 'three';

function readGlb(name) {
  const buffer = readFileSync(new URL(`../apps/web/public/models/${name}.glb`, import.meta.url));
  assert.equal(buffer.readUInt32LE(0), 0x46546c67);
  assert.equal(buffer.readUInt32LE(4), 2);
  assert.equal(buffer.readUInt32LE(8), buffer.length);
  const jsonLength = buffer.readUInt32LE(12);
  assert.equal(buffer.readUInt32LE(16), 0x4e4f534a);
  const json = JSON.parse(buffer.subarray(20, 20 + jsonLength).toString('utf8'));
  const binHeader = 20 + jsonLength;
  assert.equal(buffer.readUInt32LE(binHeader + 4), 0x004e4942);
  const binary = buffer.subarray(binHeader + 8);
  return { buffer, json, binary };
}

for (const name of ['kukirin-g4', 'surron-lbx'])
  test(`${name} is a complete finite Blender GLB with usable component groups`, () => {
    const { buffer, json, binary } = readGlb(name);
    assert.ok(buffer.length < 20 * 1024 * 1024, 'web asset exceeds 20 MB budget');
    assert.ok(json.asset.generator.toLowerCase().includes('blender'));
    for (const group of [
      'BatteryMount',
      'ControllerMount',
      'MotorMount',
      'FrontWheel',
      'RearWheel',
    ])
      assert.ok(
        json.nodes.some((node) => node.name === group),
        `missing ${group}`,
      );
    assert.ok(statSync(new URL(`../assets/blender/${name}.blend`, import.meta.url)).size > 10000);
    const bounds = new Box3();
    let triangles = 0;
    function visit(index, parent) {
      const node = json.nodes[index];
      const local = node.matrix
        ? new Matrix4().fromArray(node.matrix)
        : new Matrix4().compose(
            new Vector3().fromArray(node.translation || [0, 0, 0]),
            new Quaternion().fromArray(node.rotation || [0, 0, 0, 1]),
            new Vector3().fromArray(node.scale || [1, 1, 1]),
          );
      const world = parent.clone().multiply(local);
      assert.ok(world.elements.every(Number.isFinite));
      if (node.mesh !== undefined)
        for (const primitive of json.meshes[node.mesh].primitives) {
          const accessor = json.accessors[primitive.attributes.POSITION],
            view = json.bufferViews[accessor.bufferView];
          assert.equal(accessor.componentType, 5126);
          assert.ok(accessor.count > 0);
          const offset = (view.byteOffset || 0) + (accessor.byteOffset || 0),
            stride = view.byteStride || 12;
          for (let i = 0; i < accessor.count; i++)
            for (let axis = 0; axis < 3; axis++)
              assert.ok(Number.isFinite(binary.readFloatLE(offset + i * stride + axis * 4)));
          bounds.union(
            new Box3(
              new Vector3().fromArray(accessor.min),
              new Vector3().fromArray(accessor.max),
            ).applyMatrix4(world),
          );
          triangles +=
            (primitive.indices !== undefined
              ? json.accessors[primitive.indices].count
              : accessor.count) / 3;
        }
      for (const child of node.children || []) visit(child, world);
    }
    for (const root of json.scenes[json.scene || 0].nodes) visit(root, new Matrix4());
    const size = bounds.getSize(new Vector3());
    assert.ok(size.x > 1 && size.x < 2.4, `vehicle length ${size.x}`);
    assert.ok(size.y > 0.9 && size.y < 1.8, `vehicle height ${size.y}`);
    assert.ok(size.z > 0.35 && size.z < 1.1, `vehicle width ${size.z}`);
    assert.ok(Math.abs(bounds.min.y) < 0.06, `vehicle floats/sinks ${bounds.min.y}`);
    assert.ok(triangles > 10000 && triangles < 250000, `triangle budget ${triangles}`);
    for (const resource of [...(json.buffers || []), ...(json.images || [])])
      assert.ok(
        !resource.uri || resource.uri.startsWith('data:'),
        'unexpected remote asset dependency',
      );
  });
