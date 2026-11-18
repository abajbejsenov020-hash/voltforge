import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { disposeModelResources } from './blender-models.js';

const PARKED = [
  { url: '/models/catalog/scooters/kukirin-g4-ultra.glb', x: -1.9, z: -2.6, angle: -0.25 },
  { url: '/models/surron-lbx.glb', x: 1.95, z: -2.7, angle: -0.48 },
];

/** A physical, meter-scale workshop. Parked vehicles own separate GLTF resources. */
export function createGarage({ scene, onChange, onStatus, onParkedVehicle }) {
  const root = new THREE.Group();
  root.name = 'Garage';
  // Face the room's open side toward the viewer's default three-quarter camera.
  root.rotation.y = 0.18;
  scene.add(root);
  let disposed = false;
  let settled = 0;
  let failed = 0;
  const parked = [];
  const loader = new GLTFLoader();
  const canvas = document.querySelector('#scene');
  const state = { loading: true, failed: false, count: 0 };
  const materials = new Set();
  const geometries = new Set();
  const textures = new Set();
  const material = (options) => {
    const result = new THREE.MeshStandardMaterial(options);
    materials.add(result);
    return result;
  };
  const metal = material({ color: 0x363e40, roughness: 0.62, metalness: 0.65 });
  const black = material({ color: 0x191f20, roughness: 0.82, metalness: 0.2 });
  const silver = material({ color: 0x9aacae, roughness: 0.38, metalness: 0.85 });
  const warmPaint = material({ color: 0xc0a47a, roughness: 0.75 });
  const orange = material({ color: 0x9a5531, roughness: 0.7 });
  function texture(width, height, draw) {
    const element = document.createElement('canvas');
    element.width = width;
    element.height = height;
    draw(element.getContext('2d'), width, height);
    const result = new THREE.CanvasTexture(element);
    result.colorSpace = THREE.SRGBColorSpace;
    result.wrapS = result.wrapT = THREE.RepeatWrapping;
    result.anisotropy = 4;
    textures.add(result);
    return result;
  }
  let seed = 17;
  const random = () => (seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296;
  const concrete = texture(512, 512, (context, width, height) => {
    const pixels = context.createImageData(width, height);
    for (let i = 0; i < pixels.data.length; i += 4) {
      const noise = random() * 8;
      pixels.data.set([91 + noise, 86 + noise, 77 + noise, 255], i);
    }
    context.putImageData(pixels, 0, 0);
    for (let i = 0; i < 100; i++) {
      const x = random() * width,
        y = random() * height;
      context.strokeStyle = `rgba(35,30,25,${random() * 0.12})`;
      context.lineWidth = random() * 2 + 0.3;
      context.beginPath();
      context.moveTo(x, y);
      context.lineTo(x + random() * 60 - 30, y + random() * 12);
      context.stroke();
    }
    context.strokeStyle = '#3b3c3750';
    context.lineWidth = 1.5;
    context.strokeRect(0, 0, width, height);
  });
  concrete.repeat.set(6, 6);
  const brick = texture(512, 256, (context, width, height) => {
    context.fillStyle = '#202626';
    context.fillRect(0, 0, width, height);
    for (let row = 0; row < 8; row++) {
      for (let col = -1; col < 9; col++) {
        const shade = 42 + Math.floor(random() * 13);
        context.fillStyle = `rgb(${shade},${shade + 4},${shade + 4})`;
        context.fillRect(col * 64 + (row % 2) * 32 + 1, row * 32 + 1, 61, 29);
      }
    }
  });
  brick.repeat.set(3, 2);
  const wood = texture(256, 64, (context, width, height) => {
    context.fillStyle = '#79553a';
    context.fillRect(0, 0, width, height);
    for (let i = 0; i < 100; i++) {
      context.fillStyle = `rgba(35,22,10,${random() * 0.22})`;
      context.fillRect(0, random() * height, width, random() * 1.2);
    }
  });
  const holes = texture(128, 128, (context, width, height) => {
    context.fillStyle = '#323b3c';
    context.fillRect(0, 0, width, height);
    context.fillStyle = '#11191b';
    for (let x = 8; x < width; x += 16)
      for (let y = 8; y < height; y += 16) {
        context.beginPath();
        context.arc(x, y, 1.7, 0, Math.PI * 2);
        context.fill();
      }
  });
  holes.repeat.set(3, 1.5);
  const floorMaterial = material({
    color: 0x9c8c72,
    map: concrete,
    bumpMap: concrete,
    bumpScale: 0.004,
    roughness: 0.78,
    metalness: 0.07,
  });
  const wallMaterial = material({ map: brick, bumpMap: brick, bumpScale: 0.028, roughness: 0.92 });
  const timber = material({ map: wood, roughness: 0.72 });
  const pegboard = material({ map: holes, roughness: 0.7, metalness: 0.4 });
  function mesh(geometry, surface, x, y, z) {
    geometries.add(geometry);
    const object = new THREE.Mesh(geometry, surface);
    object.position.set(x, y, z);
    object.receiveShadow = true;
    root.add(object);
    return object;
  }
  function box(w, h, d, surface, x, y, z) {
    return mesh(new THREE.BoxGeometry(w, h, d), surface, x, y, z);
  }
  // Finite floor with a real back wall and side walls; no infinite display plinth.
  const floor = mesh(new THREE.PlaneGeometry(15, 15), floorMaterial, 0, -0.015, 0);
  floor.rotation.x = -Math.PI / 2;
  mesh(new THREE.PlaneGeometry(7.8, 3.8), wallMaterial, 0, 1.9, -3.55);
  for (const side of [-1, 1]) {
    const wall = mesh(new THREE.PlaneGeometry(10, 3.8), wallMaterial, side * 3.9, 1.9, 1.45);
    wall.rotation.y = (side * -Math.PI) / 2;
    box(0.14, 3.8, 0.14, metal, side * 3.85, 1.9, -3.48);
    box(0.08, 0.12, 10, metal, side * 3.83, 3.58, 1.4);
  }
  box(7.8, 0.12, 0.1, metal, 0, 3.58, -3.45);
  box(7.8, 0.09, 0.06, black, 0, 0.055, -3.49);
  // Workbench and cabinets are modeled volumes, so close views retain depth.
  box(2.5, 0.1, 0.72, timber, 0, 0.9, -3.06);
  for (const side of [-1, 1]) {
    box(0.73, 0.76, 0.62, metal, side * 0.82, 0.47, -3.08);
    for (let row = 0; row < 4; row++) {
      box(0.65, 0.145, 0.025, black, side * 0.82, 0.21 + row * 0.17, -2.755);
      box(0.39, 0.015, 0.035, silver, side * 0.82, 0.26 + row * 0.17, -2.73);
    }
    for (const offset of [-0.25, 0.25])
      box(0.07, 0.11, 0.52, black, side * 0.82 + offset, 0.04, -3.08);
  }
  box(0.74, 0.11, 0.54, black, 0, 0.24, -3.07);
  box(0.55, 0.23, 0.3, orange, 0, 0.4, -3.05);
  box(2.45, 1.03, 0.055, pegboard, 0, 1.61, -3.49);
  box(2.6, 0.065, 0.28, timber, 0, 2.25, -3.35);
  // A compact set of steel tools; repeated handles share an instanced draw call.
  const toolGeometry = new THREE.CylinderGeometry(0.012, 0.012, 0.24, 6);
  geometries.add(toolGeometry);
  const tools = new THREE.InstancedMesh(toolGeometry, silver, 12);
  const transform = new THREE.Object3D();
  for (let i = 0; i < 12; i++) {
    transform.position.set(-1.03 + i * 0.185, 1.65 + (i % 3) * 0.08, -3.435);
    transform.scale.set(1, 0.7 + (i % 4) * 0.17, 1);
    transform.updateMatrix();
    tools.setMatrixAt(i, transform.matrix);
    if (i % 2 === 0) {
      const head = mesh(
        new THREE.TorusGeometry(0.027, 0.008, 4, 8),
        silver,
        transform.position.x,
        transform.position.y + 0.12 * transform.scale.y,
        -3.435,
      );
      head.rotation.z = 0.3;
    }
  }
  root.add(tools);
  // Shelf to the left, spare wheels to the right, and a small rolling toolbox.
  for (const x of [-3.5, -2.65]) box(0.05, 2.4, 0.06, metal, x, 1.2, -3.2);
  for (const y of [0.18, 0.85, 1.52, 2.2]) {
    box(1.02, 0.055, 0.48, timber, -3.075, y, -3.13);
    if (y < 2) {
      box(0.38, 0.23, 0.27, black, -3.21, y + 0.15, -3.11);
      box(0.15, 0.29, 0.16, orange, -2.85, y + 0.18, -3.11);
    }
  }
  for (let i = 0; i < 3; i++) {
    const tire = mesh(new THREE.TorusGeometry(0.27, 0.07, 8, 24), black, 3.1 + i * 0.2, 1.65, -3.2);
    tire.rotation.y = Math.PI / 2;
  }
  box(1.05, 0.055, 0.55, metal, 3.3, 1.3, -3.2);
  box(0.58, 0.66, 0.48, orange, 3.35, 0.4, -3.12);
  for (let i = 0; i < 4; i++) box(0.43, 0.015, 0.035, silver, 3.35, 0.22 + i * 0.13, -2.86);
  for (const side of [-1, 1]) {
    // Ceiling battens and bench lamps have visible luminous surfaces and real lights.
    const luminous = material({
      color: 0xffe6b5,
      emissive: 0xffcf8b,
      emissiveIntensity: 3,
      roughness: 0.4,
    });
    box(2.7, 0.035, 0.08, luminous, side * 2.0, 3.48, -1.2);
    const shade = mesh(
      new THREE.ConeGeometry(0.18, 0.14, 12, 1, true),
      metal,
      side * 0.88,
      2.23,
      -3.04,
    );
    const bulb = mesh(new THREE.SphereGeometry(0.045, 8, 6), luminous, side * 0.88, 2.18, -3.04);
    const lamp = new THREE.PointLight(0xffbc75, 7, 4, 2);
    lamp.position.copy(bulb.position);
    root.add(lamp);
  }
  const cool = new THREE.PointLight(0xaacfff, 6, 7, 2);
  cool.position.set(-3, 2.9, 0.5);
  root.add(cool);
  // Narrow high windows bring cool daylight into the warm working area.
  const windowMaterial = material({
    color: 0xa6c6d0,
    emissive: 0x738f9c,
    emissiveIntensity: 0.6,
    roughness: 0.35,
  });
  for (const x of [-2.6, 0, 2.6]) {
    box(2.25, 0.59, 0.055, metal, x, 2.96, -3.49);
    box(2.07, 0.43, 0.06, windowMaterial, x, 2.96, -3.45);
    for (const offset of [-0.52, 0, 0.52]) box(0.035, 0.45, 0.075, black, x + offset, 2.96, -3.405);
  }
  // Static room surfaces share a draw call per material instead of per prop.
  const surfaces = new Map();
  for (const object of root.children) {
    if (!object.isMesh || object.isInstancedMesh) continue;
    if (!surfaces.has(object.material)) surfaces.set(object.material, []);
    surfaces.get(object.material).push(object);
  }
  for (const [surface, objects] of surfaces) {
    if (objects.length < 2) continue;
    const baked = objects.map((object) => {
      object.updateMatrix();
      return object.geometry.clone().applyMatrix4(object.matrix);
    });
    const merged = mergeGeometries(baked);
    for (const geometry of baked) geometry.dispose();
    if (!merged) continue;
    for (const object of objects) {
      root.remove(object);
      object.geometry.dispose();
      geometries.delete(object.geometry);
    }
    mesh(merged, surface, 0, 0, 0);
  }
  const contactTexture = texture(128, 128, (context, width, height) => {
    const gradient = context.createRadialGradient(
      width / 2,
      height / 2,
      8,
      width / 2,
      height / 2,
      64,
    );
    gradient.addColorStop(0, '#080c0c88');
    gradient.addColorStop(0.55, '#080c0c44');
    gradient.addColorStop(1, '#080c0c00');
    context.fillStyle = gradient;
    context.fillRect(0, 0, width, height);
  });
  const contactMaterial = new THREE.MeshBasicMaterial({
    map: contactTexture,
    transparent: true,
    depthWrite: false,
    toneMapped: false,
  });
  materials.add(contactMaterial);
  function layoutParked() {
    if (disposed) return;
    const compact = canvas.getBoundingClientRect().width < 600;
    root.rotation.y = compact ? 0.45 : 0.18;
    for (const { vehicle, entry, offset, contact } of parked) {
      const x = compact ? Math.sign(entry.x) * 1.15 : entry.x;
      vehicle.position.x = x - offset;
      contact.position.x = x;
    }
    onChange();
  }
  const resizeObserver = new ResizeObserver(layoutParked);
  resizeObserver.observe(canvas);
  function notify() {
    if (disposed) return;
    state.loading = settled < PARKED.length;
    state.failed = failed > 0;
    state.count = parked.length;
    canvas.dataset.garageState = state.loading ? 'loading' : state.failed ? 'partial' : 'ready';
    canvas.dataset.garageVehicles = String(state.count);
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
        vehicle.name = `Parked ${entry.url.split('/').pop().replace('.glb', '')}`;
        vehicle.rotation.y = entry.angle;
        const bounds = new THREE.Box3().setFromObject(vehicle);
        if (
          bounds.isEmpty() ||
          !bounds.min.toArray().concat(bounds.max.toArray()).every(Number.isFinite)
        )
          throw new Error('Parked vehicle has no finite geometry');
        const center = bounds.getCenter(new THREE.Vector3());
        vehicle.position.set(entry.x - center.x, -bounds.min.y, entry.z - center.z);
        vehicle.traverse((object) => {
          if (object.isMesh) {
            // Only the active model spends shadow-map draw calls.
            object.castShadow = false;
            object.receiveShadow = true;
          }
        });
        onParkedVehicle?.(vehicle);
        root.add(vehicle);
        const contact = mesh(
          new THREE.PlaneGeometry(2.1, 0.75),
          contactMaterial,
          entry.x,
          -0.012,
          entry.z,
        );
        contact.rotation.x = -Math.PI / 2;
        parked.push({ vehicle, entry, offset: center.x, contact });
        layoutParked();
        settled++;
        notify();
      })
      .catch(() => {
        if (vehicle) disposeModelResources(vehicle);
        if (!disposed) {
          settled++;
          failed++;
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
      resizeObserver.disconnect();
      scene.remove(root);
      tools.dispose();
      for (const { vehicle } of parked) disposeModelResources(vehicle);
      for (const resource of [...geometries, ...materials, ...textures]) resource.dispose();
      root.clear();
      delete canvas.dataset.garageState;
      delete canvas.dataset.garageVehicles;
    },
  };
}
