import * as THREE from 'three';

function boundsIn(node, objects) {
  node.updateWorldMatrix(true, true);
  const inverse = node.matrixWorld.clone().invert();
  const bounds = new THREE.Box3();
  const transform = new THREE.Matrix4();
  for (const object of objects) {
    object.traverse((mesh) => {
      if (!mesh.isMesh) return;
      if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
      transform.multiplyMatrices(inverse, mesh.matrixWorld);
      bounds.union(mesh.geometry.boundingBox.clone().applyMatrix4(transform));
    });
  }
  return bounds;
}

const sizeOf = (bounds) => bounds.getSize(new THREE.Vector3());
const centerOf = (bounds) => bounds.getCenter(new THREE.Vector3());

function materialMeshes(node, pattern) {
  return (node?.children || []).filter(
    (mesh) => mesh.isMesh && mesh.material?.name && pattern.test(mesh.material.name),
  );
}

function splitBounds(node, objects, axis, midpoint) {
  const halves = [new THREE.Box3(), new THREE.Box3()];
  const inverse = node.matrixWorld.clone().invert();
  const transform = new THREE.Matrix4();
  const point = new THREE.Vector3();
  for (const object of objects) {
    object.traverse((mesh) => {
      if (!mesh.isMesh) return;
      transform.multiplyMatrices(inverse, mesh.matrixWorld);
      const positions = mesh.geometry.getAttribute('position');
      for (let i = 0; i < positions.count; i++) {
        point.fromBufferAttribute(positions, i).applyMatrix4(transform);
        halves[Number(point[axis] > midpoint)].expandByPoint(point);
      }
    });
  }
  return halves.filter((bounds) => !bounds.isEmpty());
}

function wheelAt(root, name) {
  const node = root.getObjectByName(name);
  if (!node) return null;
  const rubber = materialMeshes(
    node,
    /(?:tyre|tire).*rubber|rubber.*(?:tyre|tire)|^rubber(?:\.\d+)?$/i,
  );
  const tire = boundsIn(node, rubber);
  const size = sizeOf(tire);
  const isolated =
    size.x > 0.12 && Math.abs(size.x - size.y) < size.x * 0.1 && size.z < size.x * 0.65;
  return { node, rubber: isolated ? rubber : [], tire, isolated };
}

function slot(category, node, stock, families, fit) {
  if (!node || !stock.length) return null;
  const bounds = boundsIn(node, stock);
  if (bounds.isEmpty()) return null;
  return {
    category,
    node,
    stock: [...stock],
    families,
    fit,
    bounds,
    visibility: stock.map((child) => child.visible),
    preview: null,
  };
}

function motorSlot(node, wheels) {
  const mount = slot('Motors', node, node?.children || [], ['reference-mid']);
  if (!mount) return null;
  const diameter = sizeOf(mount.bounds).x;
  const axleCenters = wheels
    .map((wheel) =>
      node.worldToLocal(
        wheel.node.localToWorld(
          centerOf(wheel.isolated ? wheel.tire : boundsIn(wheel.node, wheel.node.children)),
        ),
      ),
    )
    .sort((a, b) => a.x - b.x);
  const atAxle = (bounds, axle) => {
    const center = centerOf(bounds);
    return Math.hypot(center.x - axle.x, center.y - axle.y) < 0.075;
  };
  if (axleCenters.length === 2 && diameter > (axleCenters[1].x - axleCenters[0].x) * 0.8) {
    const midpoint = (axleCenters[0].x + axleCenters[1].x) / 2;
    const halves = splitBounds(node, mount.stock, 'x', midpoint);
    if (halves.length === 2 && halves.every((bounds, i) => atAxle(bounds, axleCenters[i]))) {
      mount.families = ['reference-hub'];
      mount.placements = halves;
    } else mount.families = [];
  } else if (axleCenters.some((axle) => atAxle(mount.bounds, axle))) {
    mount.families = ['reference-hub'];
  }
  return mount;
}

function wheelSlots(wheel) {
  if (!wheel.isolated) return [];
  const rotorMeshes = materialMeshes(wheel.node, /^rotor$|brake.*rotor/i);
  const rotor = slot('Brakes', wheel.node, rotorMeshes, ['chosen-rotor']);
  const rotorSize = rotor && sizeOf(rotor.bounds);
  const rotorCenter = rotor && centerOf(rotor.bounds);
  const wheelCenter = centerOf(wheel.tire);
  const isolatedRotor =
    rotor &&
    rotorSize.x > 0.08 &&
    rotorSize.z < 0.02 &&
    Math.hypot(rotorCenter.x - wheelCenter.x, rotorCenter.y - wheelCenter.y) < 0.025;
  return [
    slot('Tires & wheels', wheel.node, wheel.rubber, ['chosen-tire'], 'tire'),
    isolatedRotor ? rotor : null,
  ];
}

function gripSlot(cockpit) {
  const rubber = materialMeshes(cockpit, /grip|textured rubber|(?:tyre|tire) rubber|^rubber$/i);
  const mount = slot('Accessories', cockpit, rubber, ['chosen-grips'], 'grip');
  if (!mount) return null;
  const halves = splitBounds(cockpit, rubber, 'z', 0);
  const isolated =
    halves.length === 2 &&
    halves.every((bounds, side) => {
      const size = sizeOf(bounds);
      const innerEdge = side === 0 ? -bounds.max.z : bounds.min.z;
      return innerEdge > 0.12 && size.x < 0.09 && size.y < 0.085 && size.z > 0.07 && size.z < 0.18;
    });
  if (!isolated) return null;
  mount.placements = halves;
  return mount;
}

function bestOrientation(preview, envelope) {
  // The catalogue models use product-photo axes. Mount their long and thin sides
  // against the corresponding factory envelope while preserving their proportions.
  const quarter = Math.PI / 2;
  const rotations = [
    [0, 0, 0],
    [-quarter, 0, 0],
    [0, quarter, 0],
    [0, 0, quarter],
    [-quarter, 0, quarter],
    [0, quarter, quarter],
  ];
  let best = { rotation: rotations[0], scale: 0 };
  for (const rotation of rotations) {
    preview.rotation.set(...rotation);
    const size = sizeOf(new THREE.Box3().setFromObject(preview));
    const scale = Math.min(envelope.x / size.x, envelope.y / size.y, envelope.z / size.z);
    if (scale > best.scale) best = { rotation, scale };
  }
  preview.rotation.set(...best.rotation);
}

function placePreview(preview, mount, bounds) {
  const envelope = sizeOf(bounds);
  if (mount.fit === 'box') bestOrientation(preview, envelope);
  if (mount.fit === 'grip') preview.rotation.y = Math.PI / 2;
  if (mount.fit === 'fork') {
    const rake = Math.atan2(Math.max(0, envelope.x - 0.06), envelope.y);
    preview.rotation.set(0, 0, rake);
    preview.rotateY(Math.PI / 2);
  }
  const source = new THREE.Box3().setFromObject(preview);
  const size = sizeOf(source);
  const width = envelope.z / size.z;
  const diameter = Math.min(envelope.x / size.x, envelope.y / size.y);
  const scale = Math.min(width, diameter);
  if (!(scale > 0) || !Number.isFinite(scale)) throw new Error('Invalid mounting envelope');
  if (mount.fit === 'tire') preview.scale.set(diameter, diameter, width);
  else if (mount.fit === 'grip') {
    const thickness = Math.min(envelope.x / size.x, envelope.y / size.y);
    // Span the exposed grip sleeve without changing the handlebar width.
    preview.scale.set(width, thickness, thickness);
  } else preview.scale.multiplyScalar(scale);
  const fitted = new THREE.Box3().setFromObject(preview);
  preview.position.add(centerOf(bounds).sub(centerOf(fitted)));
  preview.traverse((mesh) => {
    if (!mesh.isMesh) return;
    mesh.castShadow = true;
    mesh.receiveShadow = true;
  });
}

function clearPreview(mount) {
  if (!mount.preview) return;
  mount.node.remove(mount.preview.root);
  mount.preview.dispose();
  mount.preview = null;
  mount.stock.forEach((child, i) => {
    child.visible = mount.visibility[i];
  });
}

function buildPreview(mount, part, createComponent) {
  const resources = [];
  const root = new THREE.Group();
  root.userData.selectedPartId = part.id;
  const dispose = () => {
    for (const preview of resources) preview.dispose();
  };
  try {
    const sourceModel = () => {
      const preview = createComponent(part);
      resources.push(preview);
      const { family } = preview.root.userData;
      if (!mount.families.includes(family)) throw new Error('No matching socket');
      if (family === 'reference-hub') {
        for (const child of [...preview.root.children]) {
          if (child.userData.tireGeometry) child.removeFromParent();
        }
      }
      return preview.root;
    };
    const positions = mount.placements || [mount.bounds];
    const previews =
      mount.fit === 'grip' ? [...sourceModel().children] : positions.map(sourceModel);
    if (previews.length !== positions.length) throw new Error('Incomplete component model');
    for (const [index, preview] of previews.entries()) {
      preview.removeFromParent();
      placePreview(preview, mount, positions[index]);
      root.add(preview);
    }
    return { root, dispose };
  } catch {
    dispose();
    return null;
  }
}

function detach(node, lift, slide, from, extract = 0) {
  return (
    node && {
      node,
      base: node.position.clone(),
      lift: new THREE.Vector3(...lift),
      slide: new THREE.Vector3(...slide),
      from,
      extract,
    }
  );
}

/** Replacements occupy independently authored factory geometry and are visual approximations. */
export function createBlenderAssembly(root, createComponent) {
  const find = (name) => root.getObjectByName(name);
  const battery = find('BatteryMount');
  const controller = find('ControllerMount');
  const motor = find('MotorMount');
  const fork = find('Fork');
  const front = wheelAt(root, 'FrontWheel');
  const rear = wheelAt(root, 'RearWheel');
  const wheels = [front, rear].filter(Boolean);
  const motorMount = motorSlot(motor, wheels);
  const hubDrive = motorMount?.families.includes('reference-hub');
  const mounts = [
    slot(
      'Batteries',
      battery,
      battery?.children || [],
      ['reference-battery', 'chosen-scooter-pack'],
      'box',
    ),
    slot(
      'Controllers',
      controller,
      controller?.children || [],
      ['reference-controller', 'nd72260'],
      'box',
    ),
    motorMount,
    ...wheels.flatMap(wheelSlots),
    gripSlot(find('Cockpit') || find('Steering')),
    slot('Suspension', fork, fork?.children || [], ['chosen-fork'], 'fork'),
  ].filter(Boolean);
  const byCategory = Map.groupBy(mounts, (mount) => mount.category);
  const previous = new Map();
  const size = sizeOf(new THREE.Box3().setFromObject(root));
  const width = Math.max(0.38, size.z);
  const lift = size.y * 0.3;
  const movement = [
    detach(front?.node, [0, 0.04, 0], [0.06, 0.06, width * (hubDrive ? -0.92 : 0.99)], 0.06, 0.3),
    detach(rear?.node, [0, 0.04, 0], [-0.06, 0.08, -width * 0.99], 0.09, 0.3),
    detach(battery, [0, lift, 0], [-0.06, 0, width * 0.76], 0.1),
    detach(controller, [0, lift * 0.84, 0], [0.06, 0, -width * 0.73], 0.19),
    detach(motor, [0, lift * 0.43, 0], [0, 0, width * 0.94], 0.25, hubDrive ? 0.26 : 0),
  ].filter(Boolean);
  const offset = new THREE.Vector3();
  const inverse = new THREE.Matrix3();
  const transform = new THREE.Matrix4();
  return {
    mounts,
    canExplode: movement.length > 0,
    setSelection(selection, { motorCount } = {}) {
      const installed = {};
      for (const [category, slots] of byCategory) {
        const part = selection[category];
        const key = part && `${part.id}:${category === 'Motors' ? (motorCount ?? '') : ''}`;
        if (previous.get(category) !== key) {
          previous.set(category, key);
          for (const mount of slots) clearPreview(mount);
          const count = slots[0].placements?.length ?? 1;
          if (part && (category !== 'Motors' || motorCount == null || motorCount === count)) {
            for (const mount of slots) {
              mount.preview = buildPreview(mount, part, createComponent);
              if (!mount.preview) break;
              mount.node.add(mount.preview.root);
              for (const child of mount.stock) child.visible = false;
            }
            // For paired mounts, leave both factory parts in place if either position is unsupported.
            if (slots.some((mount) => !mount.preview))
              for (const mount of slots) clearPreview(mount);
          }
        }
        if (part) installed[category] = slots.every((mount) => !!mount.preview);
      }
      return Object.fromEntries(
        Object.keys(selection).map((category) => [category, installed[category] ?? false]),
      );
    },
    setExploded(progress) {
      const t = THREE.MathUtils.clamp(Number(progress), 0, 1);
      for (const piece of movement) {
        const { node, base, lift, slide, from, extract } = piece;
        const liftProgress = THREE.MathUtils.smoothstep(t, from + extract * 0.3, from + 0.37);
        const earlySlide = THREE.MathUtils.smoothstep(t, from, from + 0.21) * extract;
        const slideProgress =
          earlySlide + THREE.MathUtils.smoothstep(t, from + 0.22, 1) * (1 - extract);
        node.parent.updateWorldMatrix(true, false);
        inverse.setFromMatrix4(transform.copy(node.parent.matrixWorld).invert());
        offset.copy(lift).multiplyScalar(liftProgress).addScaledVector(slide, slideProgress);
        node.position.copy(base).add(offset.applyMatrix3(inverse));
      }
    },
    dispose() {
      for (const mount of mounts) clearPreview(mount);
      previous.clear();
    },
  };
}
