import * as THREE from 'three';
import { createBlenderLoader, disposeModelResources } from './blender-models.js';
import { addCoastalHorizon } from './coastal-light.js';
import { addCoastalArchitecture } from './coastal-architecture.js';

const SHORE = -5.1;
const PARKED = [
  { model: 'dualtron-thunder-3', x: -1.62, z: -2.48, yaw: -0.34, compactX: -1.08 },
  { model: 'talaria-sting-r-mx4', x: 1.48, z: -2.73, yaw: -0.44, compactX: 1.19 },
];

function paintedTexture(size, draw) {
  const sheet = document.createElement('canvas');
  sheet.width = sheet.height = size;
  draw(sheet.getContext('2d'), size);
  const texture = new THREE.CanvasTexture(sheet);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;
  return texture;
}

function addPromenade(root) {
  const paving = paintedTexture(384, (context, size) => {
    const shades = ['#a77d7a', '#b38a83', '#a8807d', '#b58b82', '#ba9289', '#aa827e'];
    context.fillStyle = '#896862';
    context.fillRect(0, 0, size, size);
    for (let row = 0; row < 6; row++) {
      for (let col = -1; col < 4; col++) {
        const x = col * 128 + (row % 2) * 64;
        const y = row * 64;
        context.fillStyle = shades[(row * 7 + col + shades.length) % shades.length];
        context.fillRect(x + 1, y + 1, 126, 62);
        context.fillStyle = '#e5bd9d62';
        context.fillRect(x + 1, y + 1, 126, 1);
      }
    }
    const pixels = context.getImageData(0, 0, size, size);
    let seed = 6371;
    for (let i = 0; i < pixels.data.length; i += 4) {
      seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
      const grain = (seed >>> 27) - 15;
      for (let c = 0; c < 3; c++) pixels.data[i + c] += grain;
    }
    context.putImageData(pixels, 0, 0);
  });
  paving.wrapS = paving.wrapT = THREE.RepeatWrapping;
  paving.repeat.set(13, 7);
  const pavers = new THREE.MeshStandardMaterial({
    color: 0xc4aba5,
    map: paving,
    bumpMap: paving,
    bumpScale: 0.009,
    roughness: 0.85,
  });
  const limestone = new THREE.MeshStandardMaterial({ color: 0xd9b898, roughness: 0.88 });
  const base = new THREE.MeshStandardMaterial({ color: 0xa58b86, roughness: 0.9 });
  const inlay = new THREE.MeshStandardMaterial({ color: 0xd1b893, roughness: 0.82 });
  const sand = new THREE.MeshStandardMaterial({ color: 0xc39977, roughness: 0.97 });
  const bronze = new THREE.MeshStandardMaterial({
    color: 0x335556,
    metalness: 0.42,
    roughness: 0.47,
  });
  const glass = new THREE.MeshStandardMaterial({
    color: 0xffc78b,
    emissive: 0xffbe88,
    emissiveIntensity: 1.6,
    roughness: 0.56,
  });
  function mesh(geometry, material, x, y, z) {
    const result = new THREE.Mesh(geometry, material);
    result.position.set(x, y, z);
    result.receiveShadow = true;
    root.add(result);
    return result;
  }
  const box = (w, h, d, material, x, y, z) =>
    mesh(new THREE.BoxGeometry(w, h, d), material, x, y, z);
  const depth = 30;
  box(64, 0.24, depth, pavers, 0, -0.13, SHORE + depth / 2);
  box(64, 0.57, 0.18, base, 0, -0.31, SHORE + 0.025);
  box(64, 0.1, 0.38, limestone, 0, -0.045, SHORE + 0.14);
  box(64, 0.005, 0.075, inlay, 0, -0.005, SHORE + 0.61);
  box(64, 0.005, 0.035, inlay, 0, -0.005, SHORE + 0.76);

  const beachSlope = new THREE.BufferGeometry();
  beachSlope.setAttribute(
    'position',
    new THREE.Float32BufferAttribute(
      [-50, -0.37, SHORE, 50, -0.37, SHORE, -50, -0.57, SHORE - 2.85, 50, -0.57, SHORE - 2.85],
      3,
    ),
  );
  beachSlope.setIndex([0, 1, 2, 1, 3, 2]);
  beachSlope.computeVertexNormals();
  mesh(beachSlope, sand, 0, 0, 0);

  for (const height of [0.35, 0.68]) {
    const handrail = mesh(
      new THREE.CylinderGeometry(0.022, 0.022, 64, 10),
      bronze,
      0,
      height,
      SHORE + 0.25,
    );
    handrail.rotation.z = Math.PI / 2;
  }
  const posts = new THREE.InstancedMesh(new THREE.BoxGeometry(0.055, 0.72, 0.065), bronze, 32);
  const transform = new THREE.Matrix4();
  for (let i = 0; i < posts.count; i++)
    posts.setMatrixAt(i, transform.makeTranslation((i - 15.5) * 2, 0.356, SHORE + 0.25));
  root.add(posts);

  for (const x of [-6, 4.95]) {
    mesh(new THREE.CylinderGeometry(0.039, 0.058, 2.55, 12), bronze, x, 1.275, -3.73);
    mesh(new THREE.CylinderGeometry(0.13, 0.16, 0.11, 18), bronze, x, 2.5, -3.73);
    mesh(new THREE.CylinderGeometry(0.13, 0.13, 0.13, 18), glass, x, 2.59, -3.73);
    mesh(new THREE.ConeGeometry(0.2, 0.12, 18), bronze, x, 2.71, -3.73);
  }
  for (const x of [-2.6, 2.6]) box(0.043, 0.002, 1.75, inlay, x, -0.007, -1.95);
}

/** The waterfront and parked models are owned by this scene setting. */
export function createCoastalSunset({
  scene,
  onChange,
  onStatus,
  canvas = document.querySelector('#scene'),
}) {
  const root = new THREE.Group();
  root.name = 'Coastal Sunset';
  scene.add(root);
  addCoastalHorizon(root, SHORE - 2.45);
  addPromenade(root);
  addCoastalArchitecture(root);

  const parked = [];
  const state = { loading: true, failed: false, count: 0 };
  let remaining = PARKED.length;
  let disposed = false;
  const shadowMap = paintedTexture(128, (context, size) => {
    const center = size / 2;
    const shade = context.createRadialGradient(center, center, 3, center, center, center);
    shade.addColorStop(0, '#281528a0');
    shade.addColorStop(0.58, '#28152846');
    shade.addColorStop(1, '#28152800');
    context.fillStyle = shade;
    context.fillRect(0, 0, size, size);
  });
  const shadowMaterial = new THREE.MeshBasicMaterial({
    map: shadowMap,
    transparent: true,
    depthWrite: false,
  });
  const shadowShape = new THREE.PlaneGeometry(2.13, 0.82).rotateX(-Math.PI / 2);

  function layout() {
    const compact = canvas.getBoundingClientRect().width < 600;
    root.rotation.y = compact ? 0.55 : 0.33;
    for (const { bay, entry } of parked) bay.position.x = compact ? entry.compactX : entry.x;
    onChange();
  }
  function notify() {
    state.loading = remaining > 0;
    state.count = parked.length;
    canvas.dataset.coastState = state.loading ? 'loading' : state.failed ? 'partial' : 'ready';
    canvas.dataset.coastVehicles = String(state.count);
    onStatus?.(state);
    onChange();
  }
  const observer = new ResizeObserver(() => {
    if (!disposed) layout();
  });
  observer.observe(canvas);
  layout();
  const loads = PARKED.map((entry) => {
    const coordinator = createBlenderLoader({
      onReady(vehicle) {
        vehicle.rotation.y = entry.yaw;
        const bounds = new THREE.Box3().setFromObject(vehicle);
        const center = bounds.getCenter(new THREE.Vector3());
        vehicle.position.set(-center.x, -bounds.min.y, -center.z);
        vehicle.traverse((object) => {
          if (object.isMesh) object.castShadow = false;
        });
        const contact = new THREE.Mesh(shadowShape, shadowMaterial);
        contact.position.y = -0.008;
        contact.rotation.y = entry.yaw;
        const bay = new THREE.Group();
        bay.name = `Parked ${entry.model}`;
        bay.position.z = entry.z;
        bay.add(vehicle, contact);
        root.add(bay);
        parked.push({ bay, entry });
        remaining--;
        layout();
        notify();
      },
      onError() {
        state.failed = true;
        remaining--;
        notify();
      },
    });
    void coordinator.load(entry.model);
    return coordinator;
  });
  notify();

  return {
    state,
    dispose() {
      if (disposed) return;
      disposed = true;
      for (const load of loads) load.dispose();
      observer.disconnect();
      scene.remove(root);
      root.traverse((object) => {
        if (object.isInstancedMesh) object.dispose();
      });
      disposeModelResources(root);
      if (!parked.length) {
        shadowMap.dispose();
        shadowMaterial.dispose();
        shadowShape.dispose();
      }
      delete canvas.dataset.coastState;
      delete canvas.dataset.coastVehicles;
    },
  };
}
