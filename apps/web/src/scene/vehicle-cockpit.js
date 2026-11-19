import {
  BoxGeometry,
  CatmullRomCurve3,
  CylinderGeometry,
  Group,
  InstancedMesh,
  Matrix4,
  Mesh,
  MeshStandardMaterial,
  SphereGeometry,
  TubeGeometry,
  Vector3,
} from 'three';
import { GRIP_COLORS, normalizeCockpit } from '@voltforge/shared/cockpit';
import { disposeModelResources } from './blender-models.js';

const profiles = {
  flat: { rise: 0, sweep: 0 },
  swept: { rise: 0.009, sweep: 0.051 },
  'low-rise': { rise: 0.028, sweep: 0.018 },
  'high-rise': { rise: 0.052, sweep: 0.024 },
};
const yAxis = new Vector3(0, 1, 0);
const tubeRadius = 0.0111;

function addMesh(group, geometry, material, position, name) {
  const mesh = new Mesh(geometry, material);
  mesh.name = name;
  mesh.position.copy(position);
  mesh.castShadow = mesh.receiveShadow = true;
  group.add(mesh);
  return mesh;
}

function cylinder(group, radius, length, material, position, axis, name) {
  const mesh = addMesh(
    group,
    new CylinderGeometry(radius, radius, length, 28),
    material,
    position,
    name,
  );
  mesh.quaternion.setFromUnitVectors(yAxis, axis);
  return mesh;
}

function tread(group, material, position, axis, up, across, length, radius, diamond) {
  const rows = diamond ? 14 : 10;
  const sides = diamond ? 10 : 8;
  const detail = new InstancedMesh(
    new BoxGeometry(diamond ? 0.0042 : 0.0065, diamond ? 0.0042 : 0.0062, 0.0017),
    material,
    rows * sides,
  );
  detail.name = diamond ? 'Molded diamond grip texture' : 'Raised waffle grip tread';
  const rotation = new Matrix4().makeRotationZ(diamond ? Math.PI / 4 : 0);
  const transform = new Matrix4();
  const radial = new Vector3();
  const tangent = new Vector3();
  for (let row = 0; row < rows; row++) {
    const offset = (row / (rows - 1) - 0.5) * (length - 0.021);
    for (let side = 0; side < sides; side++) {
      const angle = ((side + (diamond ? (row % 2) * 0.5 : 0)) * Math.PI * 2) / sides;
      radial.copy(up).multiplyScalar(Math.cos(angle)).addScaledVector(across, Math.sin(angle));
      tangent.crossVectors(axis, radial);
      transform
        .makeBasis(tangent, axis, radial)
        .multiply(rotation)
        .setPosition(
          position.clone().addScaledVector(axis, offset).addScaledVector(radial, radius),
        );
      detail.setMatrixAt(row * sides + side, transform);
    }
  }
  detail.instanceMatrix.needsUpdate = true;
  detail.castShadow = detail.receiveShadow = true;
  group.add(detail);
}

function addGrip(group, { position, length, axis, up, rear, style, rubber, hardware }) {
  const radius = style === 'foam' ? 0.0195 : 0.018;
  cylinder(group, radius, length - 0.004, rubber, position, axis, 'Grip sleeve');
  if (style === 'diamond' || style === 'waffle')
    tread(group, rubber, position, axis, up, rear, length, radius, style === 'diamond');
  if (style === 'ribbed' || style === 'lock-on') {
    const rib = new CylinderGeometry(radius + 0.0011, radius + 0.0011, 0.0016, 24);
    const count = style === 'lock-on' ? 14 : 20;
    for (let row = 0; row < count; row++) {
      const ring = addMesh(
        group,
        rib,
        rubber,
        position.clone().addScaledVector(axis, (row / (count - 1) - 0.5) * (length - 0.023)),
        'Molded grip rib',
      );
      ring.quaternion.setFromUnitVectors(yAxis, axis);
    }
  }
  if (style === 'ergonomic') {
    const support = addMesh(
      group,
      new SphereGeometry(1, 28, 16),
      rubber,
      position.clone().addScaledVector(rear, 0.015),
      'Palm support',
    );
    support.quaternion.setFromRotationMatrix(new Matrix4().makeBasis(rear, axis, up));
    support.scale.set(0.033, length * 0.43, 0.009);
  }
  for (const end of [-1, 1]) {
    const collar = style === 'lock-on';
    const capLength = collar ? 0.007 : 0.0025;
    cylinder(
      group,
      radius + (collar ? 0.0018 : 0.0005),
      capLength,
      collar ? hardware : rubber,
      position.clone().addScaledVector(axis, (end * (length - capLength)) / 2),
      axis,
      collar ? 'Anodized lock-on collar' : 'Rounded grip end',
    );
  }
}

function gripExtent(nodes, mount, axis) {
  let min = Infinity;
  let max = -Infinity;
  const local = new Vector3();
  for (const { mesh } of nodes) {
    mesh.geometry.computeBoundingBox();
    const bounds = mesh.geometry.boundingBox;
    for (const x of [bounds.min.x, bounds.max.x])
      for (const y of [bounds.min.y, bounds.max.y])
        for (const z of [bounds.min.z, bounds.max.z]) {
          local.set(x, y, z).applyMatrix4(mesh.matrixWorld);
          const projection = mount.worldToLocal(local).dot(axis);
          min = Math.min(min, projection);
          max = Math.max(max, projection);
        }
  }
  const length = max - min;
  return length >= 0.07 && length <= 0.19 ? length : 0.118;
}

/** Use the Blender-authored clamp and grip centers as the mounting reference. */
export function createVehicleCockpit(root) {
  const center = root.getObjectByName('VF_Cockpit_Center');
  const handles = [
    root.getObjectByName('VF_Cockpit_GripA'),
    root.getObjectByName('VF_Cockpit_GripB'),
  ];
  const mount = center?.parent;
  if (!mount || handles.some((handle) => handle?.parent !== mount)) return null;
  const stock = { bar: [], gripA: [], gripB: [], controlA: [], controlB: [], cable: [] };
  mount.traverse((mesh) => {
    const tag = mesh.userData.vfCockpit;
    if (mesh.isMesh && Object.hasOwn(stock, tag))
      stock[tag].push({ mesh, position: mesh.position.clone(), visible: mesh.visible });
  });
  if (!stock.bar.length || !stock.gripA.length || !stock.gripB.length) return null;
  const axis = handles[1].position.clone().sub(handles[0].position);
  const span = axis.length();
  if (!(span > 0.25 && span < 1)) return null;
  axis.normalize();
  root.updateMatrixWorld(true);
  const up = mount
    .worldToLocal(mount.getWorldPosition(new Vector3()).add(yAxis))
    .projectOnPlane(axis)
    .normalize();
  const rear = new Vector3().crossVectors(up, axis).normalize();
  const lengths = [gripExtent(stock.gripA, mount, axis), gripExtent(stock.gripB, mount, axis)];
  const stockWidth = span + (lengths[0] + lengths[1]) / 2;
  const generated = new Group();
  generated.name = 'CustomCockpit';
  mount.add(generated);

  function rerouteCable(tag, side, handle, length, material) {
    const junction = root.getObjectByName('VF_Cockpit_Cable' + tag);
    const port = handle
      .clone()
      .addScaledVector(axis, -side * (length / 2 + 0.016))
      .addScaledVector(up, -0.012);
    const end =
      junction?.parent === mount
        ? junction.position.clone()
        : center.position
            .clone()
            .addScaledVector(up, -0.28)
            .addScaledVector(axis, side * 0.025);
    const path = new CatmullRomCurve3([
      port,
      port
        .clone()
        .addScaledVector(axis, -side * 0.027)
        .addScaledVector(up, -0.035),
      end
        .clone()
        .addScaledVector(up, 0.082)
        .addScaledVector(axis, side * 0.031),
      end,
    ]);
    addMesh(
      generated,
      new TubeGeometry(path, 36, 0.0035, 10, false),
      material,
      new Vector3(),
      'Re-routed brake hose ' + tag,
    );
  }

  function restore() {
    for (const entries of Object.values(stock))
      for (const { mesh, position, visible } of entries) {
        mesh.position.copy(position);
        mesh.visible = visible;
      }
    disposeModelResources(generated);
    generated.clear();
  }

  function move(entries, original, next) {
    const before = mount.localToWorld(original.clone());
    const after = mount.localToWorld(next.clone());
    for (const { mesh, position } of entries) {
      const delta = mesh.parent
        .worldToLocal(after.clone())
        .sub(mesh.parent.worldToLocal(before.clone()));
      mesh.position.copy(position).add(delta);
    }
  }

  let measuredWidth = Math.round(stockWidth * 1000);
  return {
    get width() {
      return measuredWidth;
    },
    centerWorld: () => center.getWorldPosition(new Vector3()),
    apply(value) {
      const { bar, grip, color, width } = normalizeCockpit(value);
      restore();
      measuredWidth = width || Math.round(stockWidth * 1000);
      const profile = profiles[bar];
      const hardware =
        profile || grip === 'lock-on'
          ? new MeshStandardMaterial({ color: '#303840', metalness: 0.66, roughness: 0.36 })
          : null;
      const rubber = grip
        ? new MeshStandardMaterial({ color: GRIP_COLORS[color || 'black'].color, roughness: 0.82 })
        : null;
      const cable =
        profile && stock.cable.length
          ? new MeshStandardMaterial({ color: '#24282b', roughness: 0.62 })
          : null;
      for (const [index, handle] of handles.entries()) {
        const side = index === 0 ? -1 : 1;
        const tag = index === 0 ? 'A' : 'B';
        const length = lengths[index];
        let position = handle.position;
        if (profile) {
          const half = measuredWidth / 2000;
          const point = (lateral, rise, sweep) =>
            center.position
              .clone()
              .addScaledVector(axis, side * lateral)
              .addScaledVector(up, rise)
              .addScaledVector(rear, sweep);
          position = point(half - length / 2, profile.rise, profile.sweep);
          const straight = half - length - 0.014;
          const bend = new CatmullRomCurve3([
            point(0, 0, 0),
            point(0.063, 0, 0),
            point(Math.max(straight * 0.65, 0.07), profile.rise * 0.73, profile.sweep * 0.78),
            point(Math.max(straight, 0.078), profile.rise, profile.sweep),
            point(half - length * 0.46, profile.rise, profile.sweep),
            point(half, profile.rise, profile.sweep),
          ]);
          const tube = addMesh(
            generated,
            new TubeGeometry(bend, 48, tubeRadius, 16, false),
            hardware,
            new Vector3(),
            'Replacement handlebar ' + tag,
          );
          tube.userData.widthMm = measuredWidth;
          move(stock['grip' + tag], handle.position, position);
          move(stock['control' + tag], handle.position, position);
          if (cable) rerouteCable(tag, side, position, length, cable);
        }
        if (grip) {
          for (const { mesh } of stock['grip' + tag]) mesh.visible = false;
          addGrip(generated, { position, length, axis, up, rear, style: grip, rubber, hardware });
        }
      }
      if (profile) {
        for (const { mesh } of stock.bar) mesh.visible = false;
        for (const { mesh } of stock.cable) mesh.visible = false;
        cylinder(
          generated,
          0.0159,
          0.085,
          hardware,
          center.position,
          axis,
          'Handlebar clamp sleeve',
        );
      }
    },
    dispose() {
      restore();
      generated.removeFromParent();
    },
  };
}
