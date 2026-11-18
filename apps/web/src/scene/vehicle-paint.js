import { normalizePaint, PAINT_ZONES } from '@voltforge/shared/build';

const deckFinishes = new Set([
  'g4 graphite grey satin powder coat',
  'model powder coat',
  'silver m4 cast aluminum',
  'model body finish',
  'dualtron satin black anodized aluminum',
]);
const frameFinishes = new Set([
  'graphite',
  'cast graphite aluminium',
  'satin black polymer',
  'black',
  'reference dark graphite frame',
  'reference frame coating',
  'grey',
  'silvergrey',
  'white',
  'navy',
  'blue',
  'yellow',
  'sage',
  'mint',
  'lime',
  'olive',
  'forest',
  'teal',
  'red',
  'orange',
  'pink',
]);
const bodyFinishes = new Set([
  'satin black polymer',
  'black',
  'graphite',
  'redbody',
  'yellow',
  'green',
  'navy',
  'orange',
]);
const rimFinishes = new Set([
  'dark anodized aluminium',
  'blackened steel',
  'machined gunmetal',
  'anodized gunmetal',
  'graphite',
]);

function paintZone(group, material, scooter, hasSeparateRotor) {
  if (!material?.color || material.map || material.transparent || material.emissive?.getHex())
    return null;
  const finish = material.name.toLowerCase();
  switch (group) {
    case 'Chassis':
      if (scooter) return deckFinishes.has(finish) ? 'deck' : null;
      return frameFinishes.has(finish) ? 'frame' : null;
    case 'Steering':
      return deckFinishes.has(finish) ? 'frame' : null;
    case 'Fork':
      return frameFinishes.has(finish) ? 'fork' : null;
    case 'RearSuspension':
      // The steel swingarm in some builds shares a mesh with pistons and fasteners.
      return frameFinishes.has(finish) ? 'swingarm' : null;
    case 'Bodywork':
      return bodyFinishes.has(finish) ? 'body' : null;
    case 'FrontWheel':
    case 'RearWheel':
      return rimFinishes.has(finish) || (hasSeparateRotor && finish === 'steel') ? 'rims' : null;
    default:
      return null;
  }
}

/** Paint clones are local to this assembly. Restore originals before releasing the GLB. */
export function createVehiclePaint(root) {
  const meshes = [];
  const colors = {};
  const copiesByZone = Object.fromEntries(
    Object.keys(PAINT_ZONES).map((zone) => [zone, new Map()]),
  );
  const scooter = Boolean(root.getObjectByName('Steering'));
  const rimGroups = new Set();

  for (const group of ['FrontWheel', 'RearWheel']) {
    if (root.getObjectByName(group)?.children.some((node) => node.material?.name === 'rotor')) {
      rimGroups.add(group);
    }
  }

  root.traverse((mesh) => {
    if (!mesh.isMesh) return;
    const group = mesh.parent?.name;
    const originals = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    const zones = originals.map((material) =>
      paintZone(group, material, scooter, rimGroups.has(group)),
    );
    if (!zones.some(Boolean)) return;
    zones.forEach((zone, index) => {
      if (zone && !Object.hasOwn(colors, zone))
        colors[zone] = `#${originals[index].color.getHexString()}`;
    });
    meshes.push({ mesh, original: mesh.material, originals, zones });
  });

  const zones = Object.keys(PAINT_ZONES).filter((zone) => Object.hasOwn(colors, zone));
  let current = {};
  return {
    get zones() {
      const visible = new Set();
      root.traverseVisible((object) => visible.add(object));
      const active = new Set();
      for (const binding of meshes) {
        if (!visible.has(binding.mesh)) continue;
        for (const zone of binding.zones) active.add(zone);
      }
      return zones.filter((zone) => active.has(zone));
    },
    colors,
    setPaint(value) {
      const paint = normalizePaint(value);
      if (zones.every((zone) => paint[zone] === current[zone])) return;
      current = paint;
      for (const { mesh, original, originals, zones } of meshes) {
        if (!zones.some((zone) => zone && paint[zone])) {
          mesh.material = original;
          continue;
        }
        const materials = originals.map((material, index) => {
          const zone = zones[index];
          if (!zone || !paint[zone]) return material;
          const copies = copiesByZone[zone];
          if (!copies.has(material)) copies.set(material, material.clone());
          const painted = copies.get(material);
          painted.color.set(paint[zone]);
          return painted;
        });
        mesh.material = Array.isArray(original) ? materials : materials[0];
      }
    },
    dispose() {
      for (const { mesh, original } of meshes) mesh.material = original;
      for (const copies of Object.values(copiesByZone)) {
        for (const material of copies.values()) material.dispose();
        copies.clear();
      }
    },
  };
}
