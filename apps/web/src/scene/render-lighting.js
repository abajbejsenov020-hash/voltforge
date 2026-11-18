import * as THREE from 'three';

const STUDIO_PANELS = [
  { position: [3, 4.2, 4], size: [4.3, 3.2], light: [4.1, 3.8, 3.35] },
  { position: [-4, 2.7, 1], size: [2.1, 5], light: [1.12, 1.56, 2.16] },
  { position: [0, 3.2, -4.8], size: [4.5, 1], light: [3.9, 4.2, 4.8] },
];

/** Bake broad softboxes into a reflection map owned by the calling renderer. */
export function createReflectionMap(
  renderer,
  { panels = STUDIO_PANELS, background = 0x444b58, size = 128 } = {},
) {
  const room = new THREE.Scene();
  room.background = new THREE.Color(background);
  for (const panel of panels) {
    const mesh = new THREE.Mesh(
      new THREE.PlaneGeometry(...panel.size),
      new THREE.MeshBasicMaterial({ color: new THREE.Color(...panel.light), toneMapped: false }),
    );
    mesh.position.set(...panel.position);
    mesh.lookAt(0, 0, 0);
    room.add(mesh);
  }
  const generator = new THREE.PMREMGenerator(renderer);
  try {
    return generator.fromScene(room, 0.025, 0.1, 20, { size });
  } finally {
    generator.dispose();
    for (const panel of room.children) {
      panel.geometry.dispose();
      panel.material.dispose();
    }
  }
}

/** A soft footprint over the ground surfaces, including in Efficient mode. */
export function createContactTexture() {
  const size = 64;
  const texels = new Uint8Array(size * size * 4);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const distance = Math.hypot(((x + 0.5) * 2) / size - 1, ((y + 0.5) * 2) / size - 1);
      const opacity = 1 - THREE.MathUtils.smoothstep(distance, 0, 1);
      texels.set([255, 255, 255, Math.round(opacity * opacity * 255)], (y * size + x) * 4);
    }
  }
  const texture = new THREE.DataTexture(texels, size, size);
  texture.magFilter = texture.minFilter = THREE.LinearFilter;
  texture.needsUpdate = true;
  return texture;
}
