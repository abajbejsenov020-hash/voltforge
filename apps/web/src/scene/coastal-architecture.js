import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

// Warm coastal stucco and a rounded corner tower make the waterfront legible from either street.
function addBeachfrontBuildings(root) {
  const stucco = (color) =>
    new THREE.MeshStandardMaterial({
      color,
      emissive: color,
      emissiveIntensity: 0.05,
      roughness: 0.82,
    });
  const trim = stucco(0xffded0);
  const peach = stucco(0xe2a291);
  const coral = stucco(0xd8817e);
  const mint = stucco(0x77b9b2);
  const base = stucco(0xa88d83);
  const canvas = stucco(0xf1d8ba);
  const teal = stucco(0x2c646c);
  const glass = new THREE.MeshStandardMaterial({
    color: 0x314957,
    roughness: 0.26,
    metalness: 0.18,
  });
  const glassReflection = new THREE.MeshStandardMaterial({
    color: 0x698a9c,
    roughness: 0.37,
    metalness: 0.1,
  });
  const windowLight = new THREE.MeshStandardMaterial({
    color: 0xcc9f7a,
    emissive: 0xd78550,
    emissiveIntensity: 0.35,
    roughness: 0.54,
  });
  const neon = new THREE.MeshStandardMaterial({
    color: 0xffb19b,
    emissive: 0xf96f7f,
    emissiveIntensity: 1.2,
    roughness: 0.45,
  });
  const batches = new Map();

  function surface(material, geometry, x, y, z, angle = 0) {
    const shape = geometry.index ? geometry.toNonIndexed() : geometry;
    if (shape !== geometry) geometry.dispose();
    shape.rotateY(angle);
    shape.translate(x, y, z);
    if (!batches.has(material)) batches.set(material, []);
    batches.get(material).push(shape);
  }
  const box = (material, x, y, z, w, h, d, angle) =>
    surface(material, new THREE.BoxGeometry(w, h, d), x, y, z, angle);

  function roundedBlock(material, x, y, z, width, height, depth, radius) {
    const w = width / 2;
    const d = depth / 2;
    const shape = new THREE.Shape();
    shape.moveTo(-w + radius, -d);
    shape.lineTo(w - radius, -d);
    shape.quadraticCurveTo(w, -d, w, -d + radius);
    shape.lineTo(w, d - radius);
    shape.quadraticCurveTo(w, d, w - radius, d);
    shape.lineTo(-w + radius, d);
    shape.quadraticCurveTo(-w, d, -w, d - radius);
    shape.lineTo(-w, -d + radius);
    shape.quadraticCurveTo(-w, -d, -w + radius, -d);
    const geometry = new THREE.ExtrudeGeometry(shape, {
      depth: height,
      bevelEnabled: false,
      curveSegments: 6,
    });
    geometry.rotateX(-Math.PI / 2);
    geometry.translate(0, -height / 2, 0);
    surface(material, geometry, x, y, z);
  }

  function window(x, y, z, w, h, panel, angle = 0) {
    // The projecting sill, mullions and two glass tones read at oblique angles.
    const normalX = Math.sin(angle);
    const normalZ = Math.cos(angle);
    const tangentX = normalZ;
    const tangentZ = -normalX;
    box(trim, x, y, z, w + 0.09, h + 0.09, 0.05, angle);
    box(panel, x + normalX * 0.03, y, z + normalZ * 0.03, w, h, 0.024, angle);
    if (panel === glass) {
      box(
        glassReflection,
        x + normalX * 0.043,
        y + h * 0.31,
        z + normalZ * 0.043,
        w - 0.025,
        h * 0.17,
        0.005,
        angle,
      );
    }
    for (const u of [-w / 6, w / 6]) {
      box(
        teal,
        x + tangentX * u + normalX * 0.047,
        y,
        z + tangentZ * u + normalZ * 0.047,
        0.023,
        h,
        0.016,
        angle,
      );
    }
    box(
      trim,
      x + normalX * 0.063,
      y - h / 2 - 0.031,
      z + normalZ * 0.063,
      w + 0.13,
      0.046,
      0.12,
      angle,
    );
  }

  const x = -6.68;
  const z = -3.17;
  const width = 5.3;
  const depth = 3.45;
  const front = z + depth / 2;
  const floor = 0.08;
  roundedBlock(base, x, floor / 2, z, width + 0.2, floor, depth + 0.2, 0.25);
  roundedBlock(peach, x, 2.31, z, width, 4.46, depth, 0.23);
  roundedBlock(coral, x + 1.48, 2.92, front - 0.48, 1.51, 3.14, 1.32, 0.42);
  roundedBlock(peach, x + 1.48, 4.66, front - 0.48, 1.24, 0.44, 1.05, 0.3);
  roundedBlock(trim, x + 1.48, 4.91, front - 0.48, 0.96, 0.1, 0.87, 0.27);
  for (const y of [1.65, 3.1, 4.46]) {
    roundedBlock(trim, x, y, z, width + 0.24, 0.1, depth + 0.24, 0.31);
    roundedBlock(teal, x, y - 0.07, z, width + 0.1, 0.033, depth + 0.11, 0.26);
    roundedBlock(trim, x + 1.48, y, front - 0.48, 1.65, 0.09, 1.48, 0.49);
  }
  roundedBlock(neon, x, 4.49, z, width + 0.25, 0.015, depth + 0.26, 0.32);
  for (const y of [2.32, 3.74]) {
    for (const dx of [-1.93, -0.89, 0.21]) {
      window(x + dx, y, front + 0.012, 0.76, 0.77, dx === -0.89 && y > 3 ? windowLight : glass);
    }
    window(x + 1.48, y, front + 0.19, 0.55, 0.76, glass);
    for (const dz of [-1.08, 0, 1.08]) {
      window(x + width / 2 + 0.012, y, z + dz, 0.73, 0.75, glass, Math.PI / 2);
      window(x + dz * 1.63, y, z - depth / 2 - 0.012, 0.79, 0.74, glass, Math.PI);
    }
  }
  for (const dx of [-1.48, -0.5, 0.48, 1.48]) {
    window(x + dx, 0.84, front + 0.019, 0.79, 1.19, dx === -0.5 ? windowLight : glass);
  }
  const east = x + width / 2;
  for (const dz of [-1.1, 0, 1.1]) {
    window(east + 0.018, 0.83, z + dz, 0.72, 1.18, dz === 0 ? windowLight : glass, Math.PI / 2);
  }
  roundedBlock(coral, east + 0.17, 1.5, z, 0.58, 0.15, 3.41, 0.21);
  roundedBlock(canvas, east + 0.17, 1.601, z, 0.56, 0.06, 3.4, 0.19);
  box(trim, east + 0.09, 0.15, z, 0.17, 0.09, 3.39);
  roundedBlock(coral, x, 1.51, front + 0.45, 4.28, 0.15, 1.12, 0.21);
  roundedBlock(canvas, x, 1.613, front + 0.45, 4.25, 0.065, 1.09, 0.2);
  box(teal, x, 0.12, front + 0.29, 4.25, 0.07, 0.58);
  for (const dx of [-2.22, 2.22]) {
    box(trim, x + dx, 0.78, front + 0.16, 0.11, 1.42, 0.13);
    box(windowLight, x + dx, 1.28, front + 0.257, 0.064, 0.11, 0.05);
  }
  for (const dx of [-0.3, -0.15, 0, 0.15, 0.3]) {
    box(trim, x + 1.48 + dx, 4.64, front + 0.057, 0.029, 0.32, 0.028);
  }

  const sideX = -11.75;
  const sideZ = -1.55;
  const sideFront = sideZ + 1.64;
  roundedBlock(mint, sideX, 1.78, sideZ, 4.3, 3.56, 3.28, 0.24);
  roundedBlock(trim, sideX, 3.58, sideZ, 4.53, 0.13, 3.52, 0.31);
  roundedBlock(trim, sideX, 1.53, sideZ, 4.5, 0.09, 3.49, 0.3);
  roundedBlock(teal, sideX, 1.45, sideZ, 4.39, 0.035, 3.4, 0.29);
  for (const dx of [-1.38, -0.46, 0.46, 1.38]) {
    window(sideX + dx, 2.46, sideFront + 0.012, 0.67, 0.83, dx > 1 ? windowLight : glass);
    window(sideX + dx, 0.81, sideFront + 0.012, 0.72, 1.2, dx < 0 ? glass : windowLight);
  }
  for (const dz of [-1.1, 0, 1.1]) {
    window(sideX + 2.16, 2.46, sideZ + dz, 0.72, 0.84, glass, Math.PI / 2);
  }
  roundedBlock(canvas, sideX, 1.39, sideFront + 0.32, 4.12, 0.15, 0.91, 0.2);

  const buildings = new THREE.Group();
  buildings.name = 'Pastel Art Deco storefronts';
  for (const [material, pieces] of batches) {
    const geometry = mergeGeometries(pieces);
    for (const piece of pieces) piece.dispose();
    buildings.add(new THREE.Mesh(geometry, material));
  }
  root.add(buildings);
}

function addShorePalms(root) {
  const bark = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.97 });
  const fronds = new THREE.MeshStandardMaterial({
    vertexColors: true,
    side: THREE.DoubleSide,
    roughness: 0.92,
  });
  let seed = 82;
  const random = () => (seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296;
  const barkLight = new THREE.Color(0x97785a);
  const barkDark = new THREE.Color(0x574534);
  const olive = new THREE.Color(0x627636);
  const green = new THREE.Color(0x254e3a);
  const barkPoints = [];
  const barkColors = [];
  const barkIndices = [];
  const leafPoints = [];
  const leafColors = [];
  const leafIndices = [];

  function vertex(points, colors, vec, color) {
    vec.toArray(points, points.length);
    color.toArray(colors, colors.length);
  }
  function geometry(points, colors, indices) {
    const shape = new THREE.BufferGeometry();
    shape.setAttribute('position', new THREE.Float32BufferAttribute(points, 3));
    shape.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    shape.setIndex(indices);
    shape.computeVertexNormals();
    return shape;
  }

  const palms = [
    { x: -2.65, z: -4.57, h: 1.93, lean: -0.27, spread: 1.07 },
    { x: 2.72, z: -4.63, h: 2.14, lean: 0.28, spread: 1.23 },
    { x: -3.93, z: -4.9, h: 3.64, lean: 0.34, spread: 1.36 },
    { x: 5.4, z: -3.23, h: 3.47, lean: 0.43, spread: 1.13 },
    { x: 6.18, z: 2.22, h: 4.67, lean: -0.58, spread: 1.49 },
  ];
  for (const { x, z, h, lean, spread } of palms) {
    const leanZ = random() * 0.35 - 0.18;
    const trunk = (t) => new THREE.Vector3(x + lean * t * t, h * t, z + leanZ * t * t);
    const sections = Math.round(h / 0.11) * 3;
    const sides = 10;
    const baseIndex = barkPoints.length / 3;
    for (let i = 0; i <= sections; i++) {
      const t = i / sections;
      const center = trunk(t);
      const scar = i % 3;
      const radius = 0.067 + 0.072 * Math.exp(-t * 15) + 0.041 * t ** 18;
      for (let j = 0; j < sides; j++) {
        const angle = (j / sides) * Math.PI * 2;
        const ridge = radius * (scar === 1 ? 1.055 : 1) * (1 + random() * 0.09);
        const p = new THREE.Vector3(
          center.x + Math.cos(angle) * ridge,
          center.y + Math.sin(3 * angle) * 0.013,
          center.z + Math.sin(angle) * ridge,
        );
        const color = barkLight
          .clone()
          .lerp(barkDark, (scar === 0 ? 0.62 : 0.18) + random() * 0.22);
        vertex(barkPoints, barkColors, p, color);
        if (i === sections) continue;
        const a = baseIndex + i * sides + j;
        const b = baseIndex + i * sides + ((j + 1) % sides);
        barkIndices.push(a, a + sides, b, b, a + sides, b + sides);
      }
    }

    const crown = trunk(0.988);
    const frondCount = 16;
    const phase = random() * Math.PI * 2;
    for (let i = 0; i < frondCount; i++) {
      const angle = phase + (i / frondCount) * Math.PI * 2 + (random() - 0.5) * 0.32;
      const outward = new THREE.Vector3(Math.cos(angle), 0, Math.sin(angle));
      const sideways = new THREE.Vector3(-outward.z, 0, outward.x);
      const length = spread * (0.73 + random() * 0.41);
      const young = i % 4 === 0;
      const rise = young ? 0.62 + random() * 0.24 : 0.43 + random() * 0.19;
      const drop = young ? 0.1 + random() * 0.18 : 0.53 + random() * 0.34;
      const twist = (random() - 0.5) * 0.27;
      const spine = (t) =>
        crown
          .clone()
          .addScaledVector(outward, length * t)
          .addScaledVector(sideways, twist * t * t)
          .add(new THREE.Vector3(0, Math.sin(2.65 * t) * rise - drop * t * t, 0));
      const color = green.clone().lerp(olive, 0.19 + random() * 0.53);

      const rachis = new THREE.CatmullRomCurve3(Array.from({ length: 8 }, (_, j) => spine(j / 7)));
      const stem = new THREE.TubeGeometry(rachis, 12, 0.012, 4, false);
      const stemOffset = leafPoints.length / 3;
      const position = stem.getAttribute('position');
      const stemColor = color.clone().lerp(barkLight, 0.28);
      for (let j = 0; j < position.count; j++) {
        vertex(
          leafPoints,
          leafColors,
          new THREE.Vector3().fromBufferAttribute(position, j),
          stemColor,
        );
      }
      for (const index of stem.index.array) leafIndices.push(index + stemOffset);
      stem.dispose();

      const count = 16;
      const steps = 5;
      for (let j = 0; j < count; j++) {
        for (const side of [-1, 1]) {
          const t = 0.11 + 0.865 * ((j + random() * 0.55) / count);
          const start = spine(t);
          const bladeLength =
            length * Math.pow(Math.sin(Math.PI * t), 0.67) * (0.245 + random() * 0.16);
          const width = bladeLength * (0.067 + random() * 0.022);
          const leafColor = color.clone().lerp(side < 0 ? olive : green, random() * 0.22);
          const droop = young ? 0.37 : 0.75;
          const offset = leafPoints.length / 3;
          for (let k = 0; k <= steps; k++) {
            const u = k / steps;
            const bend = start
              .clone()
              .addScaledVector(sideways, side * bladeLength * Math.sin(u * 1.13))
              .addScaledVector(outward, bladeLength * (0.24 * u + u * u * 0.24));
            bend.y += bladeLength * (0.21 * Math.sin(Math.PI * u) - u * u * droop);
            const halfWidth = width * Math.sin(Math.PI * u) ** 0.8 + 0.0003;
            vertex(
              leafPoints,
              leafColors,
              bend.clone().addScaledVector(outward, -halfWidth),
              leafColor,
            );
            vertex(
              leafPoints,
              leafColors,
              bend.clone().add(new THREE.Vector3(0, halfWidth * 0.55, 0)),
              leafColor,
            );
            vertex(leafPoints, leafColors, bend.addScaledVector(outward, halfWidth), leafColor);
            if (k === steps) continue;
            const a = offset + k * 3;
            leafIndices.push(
              a,
              a + 3,
              a + 1,
              a + 1,
              a + 3,
              a + 4,
              a + 1,
              a + 4,
              a + 2,
              a + 2,
              a + 4,
              a + 5,
            );
          }
        }
      }
    }
  }
  const trunks = new THREE.Mesh(geometry(barkPoints, barkColors, barkIndices), bark);
  trunks.name = 'Curved palm trunks with leaf scars';
  const crowns = new THREE.Mesh(geometry(leafPoints, leafColors, leafIndices), fronds);
  crowns.name = 'Feathered palm crowns';
  root.add(trunks, crowns);
}

export function addCoastalArchitecture(root) {
  addBeachfrontBuildings(root);
  addShorePalms(root);
}
