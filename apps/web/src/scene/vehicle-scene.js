import { createStageEnvironment } from './environment.js';
import { build as buildscooter } from './models/scooter.js';
import { build as buildbicycle } from './models/bicycle.js';
import { build as buildg4Scooter } from './models/g4Scooter.js';
import { build as buildlightBee } from './models/lightBee.js';
import { build as buildcommuterScooter } from './models/commuterScooter.js';
import * as THREE from 'three';
import { getVehicleVisual } from '@voltforge/shared/visuals';
import { normalizeVehicleName } from '@voltforge/shared/vehicles';
import { PartPreviews } from './components/index.js';
import { createVehiclePaint } from './vehicle-paint.js';
import {
  BLENDER_MODELS,
  blenderModelKey,
  createBlenderLoader,
  createBlenderAssembly,
  disposeModelResources,
} from './blender-models.js';
/* Procedural concept geometry is approximate. Three.js uses its upstream MIT license. */
export function createVehicleScene() {
  const T = THREE,
    canvas = document.querySelector('#scene');
  let renderer;
  try {
    renderer = new T.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance',
    });
  } catch (error) {
    console.error('3D renderer unavailable', error);
    const p = document.createElement('p');
    p.textContent =
      'Detailed 3D requires WebGL 2. Parts selection, checks and estimates remain available.';
    p.style.cssText =
      'position:absolute;top:45%;left:10%;right:10%;text-align:center;color:#6e7f5a';
    canvas.after(p);
    return { update() {} };
  }
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = T.PCFShadowMap;
  renderer.outputColorSpace = T.SRGBColorSpace;
  renderer.toneMapping = T.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.12;
  const scene = new T.Scene(),
    camera = new T.PerspectiveCamera(33, 1, 0.02, 50),
    target = new T.Vector3(0, 0.55, 0);
  let model = new T.Group(),
    kind = 'scooter',
    parts = {},
    visual = getVehicleVisual('', 'scooter'),
    selectionKey = '',
    azimuth = 0.5,
    elevation = 0.22,
    distance = 2.95,
    zoom = 1,
    motorCount,
    auto = false,
    explode = false,
    explodeProgress = 0,
    transition = null,
    drag = null,
    frameId = 0,
    pending = false,
    view = 'overall',
    assembly = null,
    paintModel = null,
    paint = {},
    swaps = {},
    requestedProfile = '',
    assembledFit = null,
    explodedFit = null,
    explodedDistance = 0,
    framing = null,
    settingName = '',
    disposed = false;
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const explodeButton = document.querySelector('#explode');
  const rotateButton = document.querySelector('#rotate');
  const explodedCenter = new T.Vector3();
  const assembledTargets = {
    overall: new T.Vector3(),
    cockpit: new T.Vector3(),
    drivetrain: new T.Vector3(),
    frame: new T.Vector3(),
  };
  const listeners = new AbortController();
  const listen = (name, handler, options = {}) =>
    canvas.addEventListener(name, handler, { ...options, signal: listeners.signal });
  function modelState(source, state, text) {
    for (const element of [canvas, canvas.closest('.stage')].filter(Boolean)) {
      element.dataset.modelSource = source;
      element.dataset.modelState = state;
      element.dataset.modelProfile = visual.profile;
    }
    const status = document.querySelector('#sceneModelStatus');
    if (status) status.textContent = text;
    canvas.dispatchEvent(new CustomEvent('modelsourcechange'));
  }
  const blenderLoader = createBlenderLoader({
    onReady(root) {
      disposeModel();
      scene.remove(model);
      model = root;
      scene.add(model);
      paintModel = createVehiclePaint(model);
      paintModel.setPaint(paint);
      mountParts();
      modelState('blender', 'ready', 'Blender · photo-based 3D model');
      setView(view);
      resize();
    },
    onError(error) {
      console.warn('Blender model unavailable; showing procedural concept', error);
      disposeModel();
      buildProcedural();
      model.visible = true;
      modelState('fallback', 'error', '3D model unavailable · concept fallback');
      requestDraw();
    },
  });
  scene.add(model);
  scene.add(new T.HemisphereLight(0xf4f3ef, 0x747678, 2.3));
  const key = new T.DirectionalLight(0xfff8e9, 4);
  key.position.set(2.5, 4, 3);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, {
    left: -2.3,
    right: 2.3,
    top: 2.3,
    bottom: -2.3,
    near: 0.1,
    far: 12,
  });
  key.shadow.bias = -0.0003;
  key.shadow.normalBias = 0.008;
  key.shadow.radius = 3;
  scene.add(key);
  const fill = new T.DirectionalLight(0xe4ecff, 2);
  fill.position.set(-2, 2, -3);
  scene.add(fill);
  const rim = new T.DirectionalLight(0xffffff, 2.7);
  rim.position.set(-2, 3, 1);
  scene.add(rim);
  const envScene = new T.Scene();
  envScene.background = new T.Color(0xc8c7c3);
  for (const [pos, scale] of [
    [
      [0, 3, 0],
      [5, 0.1, 5],
    ],
    [
      [3, 1, 0],
      [0.1, 3, 4],
    ],
    [
      [-3, 1, -1],
      [0.1, 2, 3],
    ],
  ]) {
    const m = new T.Mesh(new T.BoxGeometry(...scale), new T.MeshBasicMaterial({ color: 0xffffff }));
    m.position.set(...pos);
    envScene.add(m);
  }
  const pmrem = new T.PMREMGenerator(renderer),
    studioEnvironment = pmrem.fromScene(envScene, 0.08);
  scene.environment = studioEnvironment.texture;
  pmrem.dispose();
  envScene.traverse((o) => {
    o.geometry?.dispose();
    o.material?.dispose();
  });
  const floor = new T.Mesh(new T.PlaneGeometry(200, 200), new T.ShadowMaterial({ opacity: 0.17 }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.006;
  floor.receiveShadow = true;
  scene.add(floor);
  const grid = new T.GridHelper(8, 80, 0xc3c2bd, 0xd3d1cc);
  grid.material.transparent = true;
  grid.material.opacity = 0.07;
  grid.position.y = -0.004;
  scene.add(grid);
  const environment = createStageEnvironment({
    renderer,
    scene,
    floor,
    grid,
    key,
    fill,
    onChange: requestDraw,
  });
  void setEnvironment(document.querySelector('#sceneSetting')?.value || 'garage');
  function mat(color, metalness = 0, roughness = 0.6, extra = {}) {
    return new T.MeshStandardMaterial({ color, metalness, roughness, ...extra });
  }
  const M = {
    paint: mat(0x292e2b, 0.72, 0.26),
    frame: mat(0x3a3d40, 0.7, 0.29),
    black: mat(0x111512, 0.2, 0.44),
    rubber: mat(0x181b18, 0, 0.91),
    tread: mat(0x1d201c, 0, 0.95),
    grip: mat(0x242723, 0, 0.96),
    alloy: mat(0xa8afaa, 0.94, 0.22),
    silver: mat(0xc4c9c6, 0.94, 0.15),
    darkMetal: mat(0x555e57, 0.88, 0.29),
    accent: mat(0xb77a54, 0.65, 0.29),
    brake: mat(0x686d69, 0.95, 0.31),
    red: mat(0xab312c, 0.2, 0.3),
    lens: mat(0xf3f6df, 0.3, 0.17, { emissive: 0xfff6cc, emissiveIntensity: 0.45 }),
    screen: mat(0x152721, 0.25, 0.16),
    cable: mat(0x161a17, 0, 0.68),
    label: mat(0x9da88e, 0.2, 0.5),
  };
  function texture(size, draw) {
    const c = document.createElement('canvas');
    c.width = c.height = size;
    draw(c.getContext('2d'), size);
    const t = new T.CanvasTexture(c);
    t.colorSpace = T.SRGBColorSpace;
    t.anisotropy = Math.min(renderer.capabilities.getMaxAnisotropy(), 8);
    return t;
  }
  const rubberTex = texture(256, (c, n) => {
    c.fillStyle = '#222621';
    c.fillRect(0, 0, n, n);
    for (let y = 0; y < n; y += 8)
      for (let x = 0; x < n; x += 8) {
        c.fillStyle = (x + y) % 16 ? '#42473c' : '#32372e';
        c.fillRect(x, y, 3, 3);
      }
  });
  M.deck = mat(0xffffff, 0, 0.95, { map: rubberTex });
  const screenTex = texture(256, (c, n) => {
    c.fillStyle = '#17251f';
    c.fillRect(0, 0, n, n);
    c.fillStyle = '#b9d19a';
    c.font = 'bold 67px monospace';
    c.fillText('00', 29, 135);
    c.font = '20px monospace';
    c.fillText('km/h', 124, 130);
    c.strokeStyle = '#a4c687';
    c.lineWidth = 5;
    c.strokeRect(25, 30, 62, 16);
    c.fillStyle = '#8cba6c';
    c.fillRect(30, 35, 46, 7);
    c.font = '16px monospace';
    c.fillText('VOLT FORGE', 28, 208);
  });
  M.screenFace = mat(0xffffff, 0.05, 0.25, {
    map: screenTex,
    emissive: 0x31472d,
    emissiveIntensity: 0.15,
  });
  function mesh(geo, material, parent = model) {
    const m = new T.Mesh(geo, material);
    m.castShadow = true;
    m.receiveShadow = true;
    parent.add(m);
    return m;
  }
  function group(name, parent = model) {
    const g = new T.Group();
    g.name = name;
    parent.add(g);
    return g;
  }
  function box(w, h, d, material, pos = [0, 0, 0], parent = model, round = 0.008) {
    let geo;
    if (round > 0) {
      let r = Math.min(round, w / 2 - 0.00001, h / 2 - 0.00001, d / 2 - 0.00001),
        s = new T.Shape(),
        x = -w / 2 + r,
        y = -h / 2 + r,
        ww = w - 2 * r,
        hh = h - 2 * r;
      s.moveTo(x, y - r);
      s.lineTo(x + ww, y - r);
      s.quadraticCurveTo(x + ww + r, y - r, x + ww + r, y);
      s.lineTo(x + ww + r, y + hh);
      s.quadraticCurveTo(x + ww + r, y + hh + r, x + ww, y + hh + r);
      s.lineTo(x, y + hh + r);
      s.quadraticCurveTo(x - r, y + hh + r, x - r, y + hh);
      s.lineTo(x - r, y);
      s.quadraticCurveTo(x - r, y - r, x, y - r);
      geo = new T.ExtrudeGeometry(s, {
        depth: d - 2 * r,
        bevelEnabled: true,
        bevelSegments: 3,
        steps: 1,
        bevelSize: r,
        bevelThickness: r,
        curveSegments: 5,
      });
      geo.translate(0, 0, -d / 2 + r);
    } else geo = new T.BoxGeometry(w, h, d);
    let m = mesh(geo, material, parent);
    m.position.set(...pos);
    return m;
  }
  function cylinder(
    r1,
    r2,
    length,
    material,
    pos = [0, 0, 0],
    parent = model,
    axis = 'y',
    segments = 32,
  ) {
    const m = mesh(new T.CylinderGeometry(r1, r2, length, segments), material, parent);
    if (axis === 'z') m.rotation.x = Math.PI / 2;
    if (axis === 'x') m.rotation.z = Math.PI / 2;
    m.position.set(...pos);
    return m;
  }
  function tube(points, r, material, parent = model, segments = 32) {
    const curve = new T.CatmullRomCurve3(points.map((p) => new T.Vector3(...p)));
    return mesh(new T.TubeGeometry(curve, segments, r, 10, false), material, parent);
  }
  function rod(a, b, r, material, parent = model) {
    const v1 = new T.Vector3(...a),
      v2 = new T.Vector3(...b),
      m = mesh(new T.CylinderGeometry(r, r, v1.distanceTo(v2), 16), material, parent);
    m.position.copy(v1).lerp(v2, 0.5);
    m.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), v2.sub(v1).normalize());
    return m;
  }
  function torus(r, t, material, pos = [0, 0, 0], parent = model) {
    const m = mesh(new T.TorusGeometry(r, t, 10, 56), material, parent);
    m.position.set(...pos);
    return m;
  }
  function bolt(x, y, z, parent = model, r = 0.006) {
    cylinder(r * 1.45, r * 1.45, 0.0017, M.darkMetal, [x, y, z], parent, 'z', 20);
    cylinder(r, r, 0.004, M.silver, [x, y, z + 0.002], parent, 'z', 6);
    cylinder(r * 0.48, r * 0.48, 0.0045, M.black, [x, y, z + 0.003], parent, 'z', 6);
  }
  function lathe(profile, material, parent = model) {
    return mesh(
      new T.LatheGeometry(
        profile.map((p) => new T.Vector2(...p)),
        48,
      ),
      material,
      parent,
    );
  }
  function shock(a, b, r = 0.027, parent = model, springMaterial = M.accent) {
    const g = group('Coil-over shock', parent),
      start = new T.Vector3(...a),
      end = new T.Vector3(...b),
      length = start.distanceTo(end);
    g.position.copy(start);
    g.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), end.sub(start).normalize());
    cylinder(r * 0.62, r * 0.62, length, M.silver, [0, length / 2, 0], g);
    cylinder(r * 0.88, r * 0.88, length * 0.37, M.black, [0, length * 0.28, 0], g);
    for (let y of [length * 0.15, length * 0.83])
      cylinder(r * 1.2, r * 1.2, 0.012, M.darkMetal, [0, y, 0], g);
    const p = [];
    for (let i = 0; i <= 240; i++) {
      let t = i / 240,
        angle = t * Math.PI * 2 * 8;
      p.push([Math.cos(angle) * r, length * (0.18 + 0.6 * t), Math.sin(angle) * r]);
    }
    tube(p, 0.004, springMaterial, g, 240);
    for (let y of [0, length]) torus(0.012, 0.0045, M.darkMetal, [0, y, 0], g);
  }
  function wheel(x, y, r, width, motor, parent = model) {
    const g = group('Wheel — tread, rim, rotor and axle', parent);
    g.position.set(x, y, 0);
    const tire = torus(r - width * 0.46, width * 0.46, M.rubber, [0, 0, 0], g);
    tire.scale.z = 0.94;
    const ridgeR = r - width * 0.69;
    for (const z of [-width * 0.4, width * 0.4]) {
      torus(ridgeR, 0.0025, M.tread, [0, 0, z], g);
      torus(r - width * 0.88, 0.002, M.rubber, [0, 0, z * 1.01], g);
    }
    const treadGeo = new T.BoxGeometry(r * 0.095, 0.0035, width * 0.31),
      count = kind === 'bike' ? 62 : 46,
      instances = new T.InstancedMesh(treadGeo, M.tread, count * 3),
      dummy = new T.Object3D();
    for (let i = 0; i < count; i++)
      for (let row = 0; row < 3; row++) {
        let a = (i / count) * Math.PI * 2 + (row - 1) * 0.012;
        dummy.position.set(
          Math.cos(a) * (r - 0.001),
          Math.sin(a) * (r - 0.001),
          (row - 1) * width * 0.24,
        );
        dummy.rotation.set(0, 0, a - Math.PI / 2);
        dummy.rotateY((row - 1) * 0.28);
        dummy.updateMatrix();
        instances.setMatrixAt(i * 3 + row, dummy.matrix);
      }
    instances.castShadow = true;
    g.add(instances);
    const rimR = r - width * 0.91;
    for (const z of [-width * 0.31, width * 0.31]) torus(rimR, 0.007, M.alloy, [0, 0, z], g);
    cylinder(rimR * 0.25, rimR * 0.25, width * 0.8, M.darkMetal, [0, 0, 0], g, 'z');
    if (motor || kind === 'scooter') {
      const hubR = kind === 'scooter' ? rimR * 0.94 : rimR * 0.47;
      cylinder(hubR, hubR, width * 0.7, M.black, [0, 0, 0], g, 'z', 64);
      for (const side of [-1, 1]) {
        torus(hubR * 0.9, 0.003, M.alloy, [0, 0, side * width * 0.36], g);
        for (let i = 0; i < 12; i++) {
          let a = (i / 12) * Math.PI * 2;
          bolt(
            Math.cos(a) * hubR * 0.76,
            Math.sin(a) * hubR * 0.76,
            side * width * 0.365,
            g,
            0.0032,
          );
        }
        for (let i = 0; i < 6; i++) {
          let a = (i / 6) * Math.PI * 2;
          const fin = box(
            hubR * 0.6,
            0.006,
            0.003,
            M.darkMetal,
            [Math.cos(a) * hubR * 0.4, Math.sin(a) * hubR * 0.4, side * width * 0.37],
            g,
            0,
          );
          fin.rotation.z = a;
        }
      }
    }
    if (kind === 'bike') {
      const cast = /fiido m1 pro/.test(normalizeVehicleName(visual.name)),
        spokes = cast ? 5 : 32;
      for (let i = 0; i < spokes; i++) {
        let a = (i / spokes) * Math.PI * 2,
          z = i % 2 ? width * 0.27 : -width * 0.27,
          aa = a + 0.3;
        rod(
          [Math.cos(a) * rimR, Math.sin(a) * rimR, z],
          [Math.cos(aa) * rimR * 0.19, Math.sin(aa) * rimR * 0.19, -z * 0.6],
          cast ? 0.009 : 0.0009,
          cast ? M.black : M.silver,
          g,
        );
      }
    }
    const rotorR = kind === 'scooter' ? r * 0.58 : 0.085,
      z = width * 0.57,
      shape = new T.Shape();
    shape.absarc(0, 0, rotorR, 0, Math.PI * 2, false);
    const center = new T.Path();
    center.absarc(0, 0, rotorR * 0.48, 0, Math.PI * 2, true);
    shape.holes.push(center);
    for (let i = 0; i < 20; i++) {
      const a = (i / 20) * Math.PI * 2,
        hole = new T.Path();
      hole.absarc(
        Math.cos(a) * rotorR * 0.79,
        Math.sin(a) * rotorR * 0.79,
        rotorR * 0.065,
        0,
        Math.PI * 2,
        true,
      );
      shape.holes.push(hole);
    }
    const rotor = mesh(
      new T.ExtrudeGeometry(shape, { depth: 0.0018, bevelEnabled: false, curveSegments: 40 }),
      M.brake,
      g,
    );
    rotor.position.z = z;
    for (let i = 0; i < 6; i++) {
      let a = (i / 6) * Math.PI * 2;
      rod(
        [Math.cos(a) * rotorR * 0.15, Math.sin(a) * rotorR * 0.15, z],
        [Math.cos(a + 0.25) * rotorR * 0.62, Math.sin(a + 0.25) * rotorR * 0.62, z],
        0.004,
        M.darkMetal,
        g,
      );
      bolt(Math.cos(a) * rotorR * 0.35, Math.sin(a) * rotorR * 0.35, z + 0.002, g, 0.003);
    }
    cylinder(0.009, 0.009, width * 1.5, M.silver, [0, 0, 0], g, 'z', 16);
    bolt(0, 0, width * 0.78, g, 0.008);
    bolt(0, 0, -width * 0.79, g, 0.008);
    const caliper = box(
      0.035,
      0.05,
      0.025,
      M.black,
      [rotorR * 0.6, rotorR * 0.53, z + 0.011],
      g,
      0.006,
    );
    bolt(rotorR * 0.6, rotorR * 0.66, z + 0.026, g, 0.003);
    return g;
  }
  function fender(x, y, r, width, parent = model) {
    const s = new T.Shape(),
      start = 0.12 * Math.PI,
      end = 0.91 * Math.PI;
    s.absarc(x, y, r, start, end, false);
    s.absarc(x, y, r - 0.012, end, start, true);
    s.closePath();
    const m = mesh(
      new T.ExtrudeGeometry(s, {
        depth: width,
        bevelEnabled: true,
        bevelSize: 0.002,
        bevelThickness: 0.002,
        bevelSegments: 2,
        steps: 1,
        curveSegments: 32,
      }),
      M.black,
      parent,
    );
    m.position.z = -width / 2;
    return m;
  }
  function grips(barX, barY, halfWidth, parent = model) {
    for (let side of [-1, 1]) {
      const z = side * (halfWidth - 0.05);
      cylinder(0.017, 0.017, 0.11, M.rubber, [barX, barY, z], parent, 'z', 32);
      for (let i = 0; i < 23; i++) {
        const ring = torus(0.017, 0.0011, M.grip, [barX, barY, z - 0.05 + i * 0.0045], parent);
        ring.scale.x = 0.99;
      }
      for (let end of [-0.055, 0.055])
        cylinder(0.019, 0.019, 0.008, M.black, [barX, barY, z + end], parent, 'z');
      bolt(barX, barY, side * (halfWidth + 0.008), parent, 0.007);
      const clampZ = side * (halfWidth - 0.13);
      cylinder(0.016, 0.016, 0.021, M.darkMetal, [barX, barY, clampZ], parent, 'z');
      box(0.033, 0.022, 0.034, M.black, [barX - 0.015, barY - 0.012, clampZ], parent, 0.004);
      tube(
        [
          [barX - 0.01, barY, clampZ],
          [barX - 0.05, barY - 0.005, clampZ + side * 0.022],
          [barX - 0.055, barY - 0.028, clampZ + side * 0.08],
        ],
        0.004,
        M.black,
        parent,
      );
      tube(
        [
          [barX - 0.01, barY - 0.01, clampZ],
          [barX - 0.075, barY - 0.08, clampZ * 0.7],
          [barX - 0.02, barY - 0.19, clampZ * 0.45],
          [barX + 0.06, barY - 0.3, side * 0.03],
        ],
        0.003,
        M.cable,
        parent,
      );
    }
    const display = box(
      0.073,
      0.045,
      0.065,
      M.black,
      [barX - 0.02, barY + 0.035, 0],
      parent,
      0.006,
    );
    const screen = box(
      0.062,
      0.002,
      0.049,
      M.screenFace,
      [barX - 0.02, barY + 0.06, 0],
      parent,
      0.001,
    );
    screen.rotation.x = 0.04;
    box(
      0.025,
      0.024,
      0.034,
      M.black,
      [barX + 0.005, barY - 0.015, halfWidth - 0.165],
      parent,
      0.005,
    );
    cylinder(0.007, 0.007, 0.004, M.accent, [barX + 0.005, barY, halfWidth - 0.165], parent);
  }
  function decal(text, w, h, pos, rotation = [0, 0, 0], parent = model, color = '#b3c28d') {
    const tex = texture(512, (c) => {
      c.clearRect(0, 0, 512, 512);
      c.fillStyle = color;
      c.font = 'bold 66px Arial';
      c.textAlign = 'center';
      c.fillText(text, 256, 280);
    });
    const m = mesh(
      new T.PlaneGeometry(w, h),
      new T.MeshBasicMaterial({
        map: tex,
        transparent: true,
        depthWrite: false,
        polygonOffset: true,
        polygonOffsetFactor: -2,
      }),
      parent,
    );
    m.position.set(...pos);
    m.rotation.set(...rotation);
    return m;
  }
  let batteryGroup, controllerGroup;
  const modelContext = {
    T,
    M,
    group,
    box,
    rod,
    wheel,
    tube,
    cylinder,
    torus,
    bolt,
    shock,
    decal,
    mesh,
    lathe,
    fender,
    grips,
    mat,
    texture,
    panel,
    get model() {
      return model;
    },
    set model(value) {
      model = value;
    },
    get parts() {
      return parts;
    },
    set parts(value) {
      parts = value;
    },
    get visual() {
      return visual;
    },
    set visual(value) {
      visual = value;
    },
    get kind() {
      return kind;
    },
    set kind(value) {
      kind = value;
    },
    get batteryGroup() {
      return batteryGroup;
    },
    set batteryGroup(value) {
      batteryGroup = value;
    },
    get controllerGroup() {
      return controllerGroup;
    },
    set controllerGroup(value) {
      controllerGroup = value;
    },
  };
  function scooter() {
    return buildscooter(modelContext);
  }
  function bicycle() {
    return buildbicycle(modelContext);
  }
  // G4 silhouette and hardware placement traced by eye from the supplied product photo.
  // Proportions are visual estimates, never a dimensioned or load-bearing design.
  function panel(points, depth, material, z = 0, parent = model) {
    const s = new T.Shape();
    s.moveTo(...points[0]);
    points.slice(1).forEach((p) => s.lineTo(...p));
    s.closePath();
    const m = mesh(
      new T.ExtrudeGeometry(s, {
        depth,
        bevelEnabled: true,
        bevelSize: 0.003,
        bevelThickness: 0.003,
        bevelSegments: 2,
        curveSegments: 6,
      }),
      material,
      parent,
    );
    m.position.z = z - depth / 2;
    return m;
  }
  function g4Scooter() {
    return buildg4Scooter(modelContext);
  }
  function commuterScooter() {
    return buildcommuterScooter(modelContext);
  }

  // Photo-guided LBX silhouette. Proportions are visual approximations, not measured CAD.
  function lightBee() {
    return buildlightBee(modelContext);
  }

  function disposeModel() {
    assembly?.dispose();
    paintModel?.dispose();
    assembly = null;
    paintModel = null;
    swaps = {};
    disposeModelResources(model, new Set(Object.values(M)));
    scene.remove(model);
    model = new T.Group();
    scene.add(model);
    batteryGroup = controllerGroup = null;
    assembledFit = null;
    explodedFit = null;
    explodeButton.disabled = true;
    camera.clearViewOffset();
  }
  function positionParts(progress) {
    assembly?.setExploded(progress);
  }
  function mountParts() {
    assembly = createBlenderAssembly(model, (part) => PartPreviews.createModel(part, T));
    swaps = assembly.setSelection(parts, { motorCount });
    measureAssembly();
  }
  function fitGeometry() {
    model.updateMatrixWorld(true);
    const points = [];
    const bounds = new T.Box3();
    model.traverseVisible((mesh) => {
      if (!mesh.isMesh) return;
      if (!mesh.geometry.boundingBox) mesh.geometry.computeBoundingBox();
      const { min, max } = mesh.geometry.boundingBox;
      for (const x of [min.x, max.x])
        for (const y of [min.y, max.y])
          for (const z of [min.z, max.z]) {
            const point = new T.Vector3(x, y, z).applyMatrix4(mesh.matrixWorld);
            points.push(point);
            bounds.expandByPoint(point);
          }
    });
    return { bounds, points, center: bounds.getCenter(new T.Vector3()) };
  }
  function measureAssembly() {
    positionParts(0);
    assembledFit = fitGeometry();
    const { bounds, center } = assembledFit;
    assembledTargets.overall.copy(center);
    const size = bounds.getSize(new T.Vector3());
    assembledTargets.cockpit.set(center.x + size.x * 0.15, bounds.max.y - size.y * 0.08, center.z);
    assembledTargets.frame.set(center.x, center.y - size.y * 0.08, center.z);
    const wheel = model.getObjectByName('RearWheel') || model.getObjectByName('MotorMount');
    if (wheel) new T.Box3().setFromObject(wheel).getCenter(assembledTargets.drivetrain);
    else
      assembledTargets.drivetrain.set(
        bounds.min.x + size.x * 0.2,
        bounds.min.y + size.y * 0.2,
        center.z,
      );
    explodeButton.disabled = !assembly.canExplode;
    positionParts(1);
    explodedFit = fitGeometry();
    explodedCenter.copy(explodedFit.center);
    positionParts(explodeProgress);
    fitView();
  }
  function setExploded(next) {
    if (next && explodeButton.disabled) return;
    explode = next;
    explodeButton.setAttribute('aria-pressed', String(explode));
    const end = Number(explode);
    transition =
      !reduceMotion.matches && explodeProgress !== end
        ? { from: explodeProgress, end, start: performance.now() }
        : null;
    if (!transition) {
      explodeProgress = end;
      positionParts(end);
    }
    canvas.dataset.explodeState = transition ? 'moving' : explode ? 'exploded' : 'assembled';
    fitView({ keepDistance: true });
    requestDraw();
  }
  function build() {
    if (paintModel && requestedProfile === visual.profile) {
      swaps = assembly.setSelection(parts, { motorCount });
      measureAssembly();
      canvas.dispatchEvent(new CustomEvent('modelsourcechange'));
      requestDraw();
      return;
    }
    const loadingSameProfile =
      requestedProfile === visual.profile && canvas.dataset.modelState === 'loading';
    if (!loadingSameProfile) blenderLoader.cancel();
    requestedProfile = visual.profile;
    disposeModel();
    if (BLENDER_MODELS[visual.profile]) {
      model.visible = false;
      if (!loadingSameProfile) {
        modelState('loading', 'loading', 'Loading Blender 3D model…');
        void blenderLoader.load(visual.profile);
      }
    } else {
      buildProcedural();
      modelState('procedural', 'ready', '3D concept · approximate geometry');
    }
    requestDraw();
  }
  function buildProcedural() {
    M.frame.color.setHex(visual.frame);
    M.accent.color.setHex(visual.accent);
    if (kind === 'scooter') {
      if (visual.profile === 'kukirin-g4') g4Scooter();
      else if (visual.profile === 'commuter-scooter') commuterScooter();
      else scooter();
    } else if (visual.profile === 'surron-lbx') lightBee();
    else bicycle();
    if (batteryGroup) batteryGroup.name = 'BatteryMount';
    if (controllerGroup) controllerGroup.name = 'ControllerMount';
    mountParts();
  }
  function requestDraw() {
    if (pending || disposed) return;
    pending = true;
    frameId = requestAnimationFrame(render);
  }
  function render(now) {
    pending = false;
    if (disposed || canvas.hidden) return;
    if (transition) {
      const { from, end, start } = transition;
      const duration = Math.max(130, 920 * Math.abs(end - from));
      const t = T.MathUtils.clamp((now - start) / duration, 0, 1);
      explodeProgress = T.MathUtils.lerp(from, end, t);
      positionParts(explodeProgress);
      if (t === 1) {
        transition = null;
        canvas.dataset.explodeState = explode ? 'exploded' : 'assembled';
      }
    }
    const spread = T.MathUtils.smoothstep(explodeProgress, 0, 1);
    const d = T.MathUtils.lerp(distance / zoom, explodedDistance / zoom, spread);
    if (assembledFit) target.copy(assembledTargets[view]);
    else target.set(0, 0.62, 0);
    if (explodedFit) target.lerp(explodedCenter, spread);
    const yaw = azimuth + 0.22 * spread;
    const pitch = orbitPitch(spread);
    camera.position.set(
      target.x + Math.sin(yaw) * d,
      target.y + Math.sin(pitch) * d,
      target.z + Math.cos(yaw) * d,
    );
    camera.lookAt(target);
    const offset = (view === 'overall' ? 1 : spread) * (framing?.offset || 0);
    if (offset) {
      if (
        !camera.view?.enabled ||
        camera.view?.offsetY !== offset ||
        camera.view?.fullWidth !== framing.width ||
        camera.view?.fullHeight !== framing.height
      )
        camera.setViewOffset(
          framing.width,
          framing.height,
          0,
          offset,
          framing.width,
          framing.height,
        );
    } else if (!offset && camera.view?.enabled) camera.clearViewOffset();
    renderer.render(scene, camera);
    if (auto) {
      azimuth += 0.003;
    }
    if (auto || transition) requestDraw();
  }
  function resize() {
    if (disposed) return;
    const r = canvas.getBoundingClientRect();
    if (!r.width || !r.height) return;
    renderer.setSize(r.width, r.height, false);
    camera.aspect = r.width / r.height;
    camera.updateProjectionMatrix();
    fitView();
    requestDraw();
  }
  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(canvas);
  listen('pointerdown', (e) => {
    drag = [e.clientX, e.clientY];
    canvas.setPointerCapture(e.pointerId);
    auto = false;
    rotateButton.classList.remove('active');
  });
  listen('pointermove', (e) => {
    if (!drag) return;
    azimuth -= (e.clientX - drag[0]) * 0.009;
    elevation = Math.max(-0.12, Math.min(1.2, elevation + (e.clientY - drag[1]) * 0.006));
    drag = [e.clientX, e.clientY];
    requestDraw();
  });
  listen('pointerup', () => (drag = null));
  listen('pointercancel', () => (drag = null));
  listen('lostpointercapture', () => (drag = null));
  listen(
    'wheel',
    (e) => {
      e.preventDefault();
      zoom = Math.min(3, Math.max(0.6, zoom - e.deltaY * 0.001));
      requestDraw();
    },
    { passive: false },
  );
  listen('keydown', (e) => {
    if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', '+', '-'].includes(e.key)) {
      e.preventDefault();
      if (e.key === 'ArrowLeft') azimuth -= 0.14;
      if (e.key === 'ArrowRight') azimuth += 0.14;
      if (e.key === 'ArrowUp') elevation = Math.min(1.2, elevation + 0.1);
      if (e.key === 'ArrowDown') elevation = Math.max(-0.12, elevation - 0.1);
      if (e.key === '+') zoom = Math.min(3, zoom + 0.1);
      if (e.key === '-') zoom = Math.max(0.6, zoom - 0.1);
      requestDraw();
    }
  });
  document.querySelector('#zoomIn').onclick = () => {
    zoom = Math.min(3, zoom + 0.15);
    requestDraw();
  };
  document.querySelector('#zoomOut').onclick = () => {
    zoom = Math.max(0.6, zoom - 0.15);
    requestDraw();
  };
  document.querySelector('#resetView').onclick = () => setView('overall');
  rotateButton.onclick = (e) => {
    auto = !auto;
    e.currentTarget.classList.toggle('active', auto);
    requestDraw();
  };
  explodeButton.disabled = true;
  explodeButton.onclick = () => {
    auto = false;
    rotateButton.classList.remove('active');
    setExploded(!explode);
  };
  reduceMotion.addEventListener('change', () => setExploded(explode), {
    signal: listeners.signal,
  });
  listen('webglcontextlost', (e) => {
    e.preventDefault();
    auto = false;
  });
  listen('webglcontextrestored', () => location.reload());
  function orbitPitch(explodedFraction) {
    const coast = settingName === 'coast' && view === 'overall';
    const base = coast ? Math.max(-0.12, elevation - 0.13) : elevation;
    const inspectionPitch = coast ? 0.26 : 0.46;
    return base + Math.max(0, inspectionPitch - base) * explodedFraction;
  }
  function setEnvironment(name) {
    if (name === settingName) return;
    settingName = name;
    camera.far = name === 'coast' ? 155 : 50;
    camera.updateProjectionMatrix();
    fitView();
    return environment.set(name);
  }
  function fitView({ keepDistance = false } = {}) {
    const rect = canvas.getBoundingClientRect();
    const inspection = document.querySelector('.model-inspection').getBoundingClientRect();
    const controls = document.querySelector('.stage-controls').getBoundingClientRect();
    const top = Math.max(12, inspection.bottom - rect.top + 12);
    const bottom = Math.min(rect.height - 12, controls.top - rect.top - 12);
    // Fit in the portion of the canvas between the inspection and camera controls.
    framing =
      rect.width && bottom > top
        ? {
            width: rect.width,
            height: rect.height,
            heightFraction: (bottom - top) / rect.height,
            offset: rect.height / 2 - (top + bottom) / 2,
          }
        : null;
    if (!keepDistance && view === 'overall')
      distance = fitDistance(assembledFit, azimuth, orbitPitch(0));
    explodedDistance = Math.max(
      distance * 1.12,
      fitDistance(explodedFit, azimuth + 0.22, orbitPitch(1)),
    );
  }
  function fitDistance(geometry, yaw, pitch) {
    if (!geometry?.points.length) return kind === 'bike' ? 3.25 : 2.95;
    const { bounds, points, center } = geometry;
    const radius = bounds.getSize(new T.Vector3()).length() / 2;
    const vertical = T.MathUtils.degToRad(camera.fov / 2);
    const horizontal = Math.atan(Math.tan(vertical) * camera.aspect);
    const original = (radius / Math.sin(Math.min(vertical, horizontal))) * 1.04;
    if (!framing) return original;
    const direction = new T.Vector3(Math.sin(yaw), Math.sin(pitch), Math.cos(yaw));
    const orbitLength = direction.length();
    direction.normalize();
    const right = new T.Vector3().crossVectors(camera.up, direction).normalize();
    const up = new T.Vector3().crossVectors(direction, right);
    const tanX = Math.tan(horizontal) * Math.max(0.1, (framing.width - 32) / framing.width);
    const tanY = Math.tan(vertical) * framing.heightFraction;
    let fitted = 0;
    const corner = new T.Vector3();
    for (const point of points) {
      corner.copy(point).sub(center);
      const depth = corner.dot(direction);
      fitted = Math.max(
        fitted,
        (Math.abs(corner.dot(right)) * 1.04) / tanX + depth,
        (Math.abs(corner.dot(up)) * 1.04) / tanY + depth,
      );
    }
    return fitted / orbitLength;
  }
  function setView(v) {
    view = v;
    zoom = 1;
    camera.clearViewOffset();
    if (v === 'overall') {
      azimuth = 0.5;
      elevation = 0.22;
    }
    if (v === 'cockpit') {
      distance = 1.02;
      azimuth = 1.35;
      elevation = 0.46;
    }
    if (v === 'drivetrain') {
      distance = kind === 'bike' ? 1.45 : 0.78;
      azimuth = 0.2;
      elevation = 0.21;
    }
    if (v === 'frame') {
      distance = kind === 'bike' ? 1.7 : 1.35;
      azimuth = 0.5;
      elevation = 0.45;
    }
    document
      .querySelectorAll('[data-view]')
      .forEach((b) => b.setAttribute('aria-pressed', b.dataset.view === v));
    fitView();
    requestDraw();
  }
  document
    .querySelectorAll('[data-view]')
    .forEach((b) => (b.onclick = () => setView(b.dataset.view)));
  return {
    setEnvironment,
    getPaintZones: () => paintModel?.zones || [],
    getPaintColors: () => paintModel?.colors || {},
    getSwaps: () => swaps,
    setPaint(next) {
      paint = next;
      paintModel?.setPaint(paint);
      requestDraw();
    },
    resize,
    dispose() {
      if (disposed) return;
      disposed = true;
      blenderLoader.dispose();
      listeners.abort();
      document
        .querySelectorAll('#zoomIn,#zoomOut,#resetView,#rotate,#explode,[data-view]')
        .forEach((button) => {
          button.onclick = null;
        });
      resizeObserver.disconnect();
      cancelAnimationFrame(frameId);
      assembly?.dispose();
      paintModel?.dispose();
      disposeModelResources(model);
      const materialRoot = new T.Group();
      for (const material of Object.values(M)) {
        const object = new T.Object3D();
        object.material = material;
        materialRoot.add(object);
      }
      disposeModelResources(materialRoot);
      disposeModelResources(floor);
      disposeModelResources(grid);
      environment.dispose?.();
      studioEnvironment.dispose();
      renderer.dispose();
    },
    update(type, selection, category, vehicleName = '', nextPaint = {}, nextMotorCount) {
      if (disposed) return;
      if (paint !== nextPaint) this.setPaint(nextPaint);
      motorCount = nextMotorCount;
      const k = JSON.stringify([type, vehicleName, selection, motorCount]);
      visual = getVehicleVisual(vehicleName, type);
      const modelKey = blenderModelKey(vehicleName);
      visual.profile =
        modelKey ||
        (BLENDER_MODELS[visual.profile]
          ? type === 'scooter'
            ? 'performance-scooter'
            : 'mountain-bike'
          : visual.profile);
      if (k !== selectionKey) {
        if (requestedProfile !== visual.profile) {
          transition = null;
          explodeProgress = 0;
          setExploded(false);
        }
        if (kind !== type) {
          zoom = 1;
          view = 'overall';
          azimuth = 0.5;
          elevation = 0.22;
          distance = type === 'bike' ? 3.25 : 2.95;
          document
            .querySelectorAll('[data-view]')
            .forEach((b) => b.setAttribute('aria-pressed', b.dataset.view === 'overall'));
        }
        kind = type;
        parts = selection;
        selectionKey = k;
        build();
      } else requestDraw();
    },
  };
}
