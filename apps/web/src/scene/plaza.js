import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { disposeModelResources } from './blender-models.js';

const PARKED = [
  {
    name: 'Dualtron Thunder 3',
    url: '/models/expansion/premium/dualtron-thunder-3.glb',
    x: -2.1,
    z: -2.5,
    angle: -0.23,
  },
  {
    name: 'Sur-Ron Ultra Bee',
    url: '/models/catalog/lightmoto/sur-ron-ultra-bee.glb',
    x: 2.05,
    z: -2.65,
    angle: -0.45,
  },
];

/** Finite, meter-scale architecture and separately owned parked Blender vehicles. */
export function createChargingPlaza({
  scene,
  onChange,
  onStatus,
  onParkedVehicle,
  loader = new GLTFLoader(),
  canvas = document.querySelector('#scene'),
}) {
  const root = new THREE.Group();
  root.name = 'City charging plaza';
  scene.add(root);
  const state = { loading: true, failed: false, count: 0 };
  const resources = new Set();
  const parked = [];
  let disposed = false,
    settled = 0,
    failures = 0;
  const own = (resource) => (resources.add(resource), resource);
  const surface = (options) => own(new THREE.MeshStandardMaterial(options));
  const charcoal = surface({ color: 0x202a31, roughness: 0.52, metalness: 0.62 });
  const concrete = surface({ color: 0x717675, roughness: 0.83 });
  const steel = surface({ color: 0x849399, roughness: 0.32, metalness: 0.84 });
  const darkGlass = surface({ color: 0x263e4b, roughness: 0.21, metalness: 0.68 });
  const shopGlass = surface({
    color: 0x7b97a3,
    roughness: 0.2,
    metalness: 0.12,
    transparent: true,
    opacity: 0.18,
    depthWrite: false,
  });
  const timber = surface({ color: 0x6e4730, roughness: 0.72 });
  const foliage = surface({ color: 0x183426, roughness: 0.93 });
  const trunk = surface({ color: 0x3e3026, roughness: 0.95 });
  const warm = surface({
    color: 0xffedc4,
    emissive: 0xffd094,
    emissiveIntensity: 2.4,
    roughness: 0.4,
  });
  const cyan = surface({
    color: 0x7ce5dd,
    emissive: 0x55e1d6,
    emissiveIntensity: 1.6,
    roughness: 0.4,
  });
  const windowLight = surface({
    color: 0xbca886,
    emissive: 0x9c7951,
    emissiveIntensity: 0.7,
    roughness: 0.4,
  });

  let seed = 43;
  const random = () => (seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296;
  function texture(w, h, draw) {
    const element = document.createElement('canvas');
    element.width = w;
    element.height = h;
    draw(element.getContext('2d'), w, h);
    const result = own(new THREE.CanvasTexture(element));
    result.colorSpace = THREE.SRGBColorSpace;
    result.anisotropy = 4;
    return result;
  }
  const paving = texture(512, 512, (context, w, h) => {
    const pixels = context.createImageData(w, h);
    for (let i = 0; i < pixels.data.length; i += 4) {
      const v = 100 + random() * 24;
      pixels.data.set([v, v + 3, v + 5, 255], i);
    }
    context.putImageData(pixels, 0, 0);
    context.strokeStyle = '#363d43';
    context.lineWidth = 2;
    for (let row = 0; row < 4; row++)
      for (let col = -1; col < 5; col++)
        context.strokeRect(col * 128 + (row % 2) * 64, row * 128, 128, 128);
  });
  paving.wrapS = paving.wrapT = THREE.RepeatWrapping;
  paving.repeat.set(9, 9);
  const pavingMaterial = surface({
    color: 0xa8afb1,
    map: paving,
    bumpMap: paving,
    bumpScale: 0.008,
    roughness: 0.42,
    metalness: 0.12,
  });
  const whiteStone = surface({ color: 0x777f7e, roughness: 0.65 });
  function mesh(geometry, material, x, y, z) {
    own(geometry);
    const result = new THREE.Mesh(geometry, material);
    result.position.set(x, y, z);
    result.receiveShadow = true;
    root.add(result);
    return result;
  }
  const box = (w, h, d, material, x, y, z) =>
    mesh(new THREE.BoxGeometry(w, h, d), material, x, y, z);
  function rod(a, b, r, material) {
    const start = new THREE.Vector3(...a),
      end = new THREE.Vector3(...b),
      direction = end.clone().sub(start);
    const result = mesh(
      new THREE.CylinderGeometry(r, r, direction.length(), 10),
      material,
      0,
      0,
      0,
    );
    result.position.copy(start.add(end).multiplyScalar(0.5));
    result.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction.normalize());
    return result;
  }
  function cable(points) {
    const curve = new THREE.CatmullRomCurve3(points.map((point) => new THREE.Vector3(...point)));
    return mesh(new THREE.TubeGeometry(curve, 20, 0.012, 6, false), charcoal, 0, 0, 0);
  }
  function sign(text, subline, w, h, x, y, z) {
    const image = texture(1024, 256, (context, width, height) => {
      context.fillStyle = '#18262c';
      context.fillRect(0, 0, width, height);
      context.fillStyle = '#baf6e9';
      context.font = '600 62px sans-serif';
      context.fillText(text, 44, 104);
      context.fillStyle = '#b4c4c7';
      context.font = '26px sans-serif';
      context.fillText(subline, 46, 174);
    });
    const material = surface({
      map: image,
      emissiveMap: image,
      emissive: 0xffffff,
      emissiveIntensity: 0.55,
      roughness: 0.6,
    });
    return mesh(new THREE.PlaneGeometry(w, h), material, x, y, z);
  }

  const floor = mesh(new THREE.PlaneGeometry(28, 28), pavingMaterial, 0, -0.016, 0);
  floor.rotation.x = -Math.PI / 2;
  // A flush, framed standing area anchors the active vehicle without a display plinth.
  box(3.6, 0.018, 2.15, whiteStone, 0, -0.017, 0.12);
  for (const x of [-1.83, 1.83]) box(0.025, 0.012, 2.25, steel, x, -0.01, 0.12);
  for (const z of [-1.02, 1.26]) box(3.68, 0.012, 0.025, steel, 0, -0.01, z);
  // Charging canopy and edge-recessed luminaires, with air visible around the columns.
  box(8.6, 0.19, 2.7, charcoal, 0, 2.85, -2.85);
  box(8.4, 0.055, 2.5, timber, 0, 2.735, -2.85);
  for (const x of [-3.9, 3.9]) {
    box(0.12, 2.75, 0.12, charcoal, x, 1.36, -3.82);
    box(0.32, 0.045, 0.32, steel, x, 0.015, -3.82);
    for (const dx of [-0.105, 0.105])
      for (const dz of [-0.105, 0.105])
        mesh(new THREE.CylinderGeometry(0.014, 0.014, 0.015, 8), steel, x + dx, 0.045, -3.82 + dz);
  }
  for (const z of [-1.58, -4.1]) box(8.2, 0.016, 0.035, warm, 0, 2.72, z);
  for (const x of [-2.25, 0, 2.25]) box(0.035, 0.014, 2.15, warm, x, 2.696, -2.86);
  sign('VOLT / CITY', 'ELECTRIC RIDES  ·  CHARGING COURT', 2.55, 0.64, 0, 2.26, -4.32);

  for (const [i, x] of [-2.35, 2.3].entries()) {
    box(0.48, 1.27, 0.22, charcoal, x, 0.63, -3.7);
    box(0.43, 0.08, 0.24, steel, x, 1.29, -3.7);
    box(0.28, 0.36, 0.015, darkGlass, x, 0.98, -3.58);
    box(0.022, 0.93, 0.018, cyan, x - 0.19, 0.73, -3.575);
    sign(`0${i + 1} / READY`, 'PARK  ·  CONNECT  ·  RECHARGE', 0.31, 0.078, x, 0.98, -3.565);
    cable([
      [x + 0.23, 1.09, -3.66],
      [x + 0.48, 0.91, -3.51],
      [x + 0.52, 0.34, -3.45],
      [x + 0.32, 0.31, -3.43],
      [x + 0.27, 0.91, -3.56],
    ]);
    box(0.045, 0.14, 0.055, steel, x + 0.26, 0.97, -3.56);
    for (const offset of [-0.73, 0.73]) {
      box(0.025, 0.008, 1.9, whiteStone, x + offset, -0.006, -2.55);
      rod([x + offset, 0, -1.9], [x + offset, 0.59, -1.9], 0.04, charcoal);
      rod([x + offset, 0.48, -1.9], [x + offset, 0.52, -1.9], 0.042, cyan);
    }
    const light = new THREE.PointLight(0xffbb78, 16, 7, 2);
    light.position.set(x, 2.48, -2.25);
    root.add(light);
  }

  // Low planters and timber seating frame the forecourt without blocking rotation.
  for (const side of [-1, 1]) {
    const x = side * 4.8;
    box(1.45, 0.48, 1.6, concrete, x, 0.23, -2.35);
    box(1.3, 0.035, 1.45, trunk, x, 0.48, -2.35);
    rod([x, 0.48, -2.35], [x + side * 0.12, 2.6, -2.35], 0.065, trunk);
    const leafGeometry = own(new THREE.IcosahedronGeometry(0.12, 0));
    const leaves = own(new THREE.InstancedMesh(leafGeometry, foliage, 360));
    const transform = new THREE.Object3D();
    for (let j = 0; j < 360; j++) {
      const angle = random() * Math.PI * 2,
        radius = Math.cbrt(random());
      const height = random() * 2 - 1,
        horizontal = Math.sqrt(1 - height * height);
      transform.position.set(
        x + Math.cos(angle) * horizontal * radius * 0.87,
        2.6 + height * radius * 0.98,
        -2.35 + Math.sin(angle) * horizontal * radius * 0.78,
      );
      transform.rotation.set(random() * 3, random() * 3, random() * 3);
      transform.scale.setScalar(0.65 + random() * 0.95);
      transform.updateMatrix();
      leaves.setMatrixAt(j, transform.matrix);
      leaves.setColorAt(
        j,
        new THREE.Color().setHSL(0.29 + random() * 0.05, 0.25, 0.3 + random() * 0.3),
      );
    }
    root.add(leaves);
    for (const dx of [-0.5, 0.45]) rod([x, 1.75, -2.35], [x + dx, 2.7, -2.22], 0.025, trunk);
    for (const dx of [-0.57, 0.57]) box(0.12, 0.43, 0.44, charcoal, side * 4.55 + dx, 0.21, -0.72);
    for (let j = 0; j < 5; j++) box(1.6, 0.055, 0.07, timber, side * 4.55, 0.44, -0.93 + j * 0.095);
    rod([side * 6, 0, -0.5], [side * 6, 3.9, -0.5], 0.045, charcoal);
    box(0.55, 0.045, 0.22, charcoal, side * 6 - side * 0.22, 3.9, -0.5);
    box(0.43, 0.012, 0.16, warm, side * 6 - side * 0.22, 3.87, -0.5);
  }
  // Layered building fronts and window recesses create actual depth and parallax.
  for (const [x, width, height, z] of [
    [-5.6, 4.3, 8.6, -6.6],
    [0, 6.4, 10.5, -7.2],
    [5.9, 4.6, 7.5, -6.9],
  ]) {
    box(width, height - 2.8, 1.8, charcoal, x, (height + 2.8) / 2, z);
    box(width, 2.8, 0.12, timber, x, 1.4, z - 0.72);
    box(0.16, 2.8, 1.8, concrete, x - width / 2, 1.4, z);
    box(0.16, 2.8, 1.8, concrete, x + width / 2, 1.4, z);
    box(width, 0.06, 1.8, concrete, x, 0.02, z);
    box(width - 0.3, 0.045, 0.08, warm, x, 2.57, z - 0.57);
    box(width * 0.62, 0.92, 0.45, concrete, x, 0.48, z - 0.25);
    box(width * 0.65, 0.065, 0.53, timber, x, 0.96, z - 0.25);
    for (const offset of [-0.7, 0.7]) {
      mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.045, 20), timber, x + offset, 0.58, z + 0.37);
      rod([x + offset, 0.02, z + 0.37], [x + offset, 0.56, z + 0.37], 0.026, charcoal);
      box(0.28, 0.27, 0.08, darkGlass, x + offset, 1.12, z - 0.27);
    }
    for (let j = 0; j < Math.floor(width / 0.18); j++)
      box(0.035, 2.4, 0.045, charcoal, x - width / 2 + j * 0.18, 1.3, z - 0.64);
    box(width + 0.08, 0.12, 1.88, concrete, x, 2.8, z);
    for (let col = 0; col < Math.floor(width / 1.1); col++) {
      const xx = x - width / 2 + 0.64 + col * 1.1;
      mesh(new THREE.PlaneGeometry(1.04, 2.25), shopGlass, xx, 1.25, z + 0.95);
      box(0.025, 2.35, 0.09, charcoal, xx + 0.53, 1.25, z + 1);
      box(0.035, 0.36, 0.035, steel, xx + 0.35, 1.05, z + 1.02);
    }
    for (let floor = 2; floor < Math.floor(height / 1.35); floor++) {
      const count = Math.floor(width / 0.88);
      for (let col = 0; col < count; col++) {
        const xx = x - width / 2 + 0.52 + col * 0.88,
          yy = 0.85 + floor * 1.35;
        box(0.62, 0.85, 0.06, concrete, xx, yy, z + 0.925);
        box(0.58, 0.81, 0.065, random() > 0.68 ? windowLight : darkGlass, xx, yy, z + 0.96);
      }
    }
  }
  const shopLight = new THREE.PointLight(0xffc285, 18, 7, 2);
  shopLight.position.set(0, 2.1, -6.7);
  root.add(shopLight);
  // Bake repeated static surfaces into one draw call per material.
  const batches = new Map();
  for (const object of root.children)
    if (object.isMesh && !object.isInstancedMesh) {
      if (!batches.has(object.material)) batches.set(object.material, []);
      batches.get(object.material).push(object);
    }
  for (const [material, objects] of batches) {
    if (objects.length < 2) continue;
    const geometries = objects.map((object) => {
      object.updateMatrix();
      return object.geometry.clone().applyMatrix4(object.matrix);
    });
    const combined = mergeGeometries(geometries);
    for (const geometry of geometries) geometry.dispose();
    if (!combined) continue;
    for (const object of objects) {
      root.remove(object);
      resources.delete(object.geometry);
      object.geometry.dispose();
    }
    mesh(combined, material, 0, 0, 0);
  }
  const contactMap = texture(128, 128, (context) => {
    const gradient = context.createRadialGradient(64, 64, 8, 64, 64, 64);
    gradient.addColorStop(0, '#040b1688');
    gradient.addColorStop(1, '#040b1600');
    context.fillStyle = gradient;
    context.fillRect(0, 0, 128, 128);
  });
  const contactMaterial = own(
    new THREE.MeshBasicMaterial({ map: contactMap, transparent: true, depthWrite: false }),
  );
  function layout() {
    const compact = canvas.getBoundingClientRect().width < 600;
    root.rotation.y = compact ? 0.38 : 0.12;
    for (const { vehicle, entry, center, contact } of parked) {
      const x = compact ? Math.sign(entry.x) * 1.25 : entry.x;
      vehicle.position.x = x - center.x;
      contact.position.x = x;
    }
    onChange();
  }
  const observer = new ResizeObserver(() => {
    if (!disposed) layout();
  });
  observer.observe(canvas);
  layout();
  function notify() {
    if (disposed) return;
    state.loading = settled < PARKED.length;
    state.failed = failures > 0;
    state.count = parked.length;
    canvas.dataset.plazaState = state.loading ? 'loading' : state.failed ? 'partial' : 'ready';
    canvas.dataset.plazaVehicles = String(state.count);
    onStatus?.(state);
    onChange();
  }
  for (const entry of PARKED) {
    let vehicle;
    void loader
      .loadAsync(entry.url)
      .then((gltf) => {
        vehicle = gltf.scene;
        if (disposed) {
          disposeModelResources(vehicle);
          return;
        }
        vehicle.name = `Parked ${entry.name}`;
        vehicle.rotation.y = entry.angle;
        const bounds = new THREE.Box3().setFromObject(vehicle);
        if (
          bounds.isEmpty() ||
          !bounds.min.toArray().concat(bounds.max.toArray()).every(Number.isFinite)
        )
          throw new Error('Empty parked vehicle');
        const center = bounds.getCenter(new THREE.Vector3());
        vehicle.position.set(entry.x - center.x, -bounds.min.y, entry.z - center.z);
        vehicle.traverse((object) => {
          if (object.isMesh) {
            object.castShadow = false;
            object.receiveShadow = true;
          }
        });
        onParkedVehicle?.(vehicle);
        root.add(vehicle);
        const contact = mesh(
          new THREE.PlaneGeometry(2.1, 0.85),
          contactMaterial,
          entry.x,
          -0.004,
          entry.z,
        );
        contact.rotation.x = -Math.PI / 2;
        parked.push({ vehicle, entry, center, contact });
        layout();
        settled++;
        notify();
      })
      .catch(() => {
        if (vehicle) disposeModelResources(vehicle);
        if (!disposed) {
          settled++;
          failures++;
          notify();
        }
      });
  }
  notify();
  return {
    state,
    dispose() {
      if (disposed) return;
      disposed = true;
      observer.disconnect();
      scene.remove(root);
      for (const { vehicle } of parked) disposeModelResources(vehicle);
      for (const resource of resources) resource.dispose();
      resources.clear();
      root.clear();
      delete canvas.dataset.plazaState;
      delete canvas.dataset.plazaVehicles;
    },
  };
}
