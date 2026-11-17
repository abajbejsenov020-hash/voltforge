export function buildComponentModel(p, T, describe) {
  if (!describe(p).model) throw new Error('Exact product reference required for a 3D model');
  const root = new T.Group(),
    materials = [],
    geometries = [];
  const make = (color, metal = 0.2, rough = 0.5) => {
    const m = new T.MeshStandardMaterial({ color, metalness: metal, roughness: rough });
    materials.push(m);
    return m;
  };
  const black = make(0x22262b, 0.25),
    silver = make(0xadb4b7, 0.8, 0.3),
    dark = make(0x4b5158, 0.7),
    rubber = make(0x161b1d, 0, 0.86),
    gold = make(0xc2a04d, 0.7),
    green = make(0x64a83e, 0.12, 0.58),
    white = make(0xe6e7dc, 0),
    red = make(0xb94337, 0.1),
    blue = make(0x387b9f, 0.1);
  const info = describe(p);
  function add(geo, mat, pos = [0, 0, 0], parent = root) {
    geometries.push(geo);
    const o = new T.Mesh(geo, mat);
    o.position.set(...pos);
    parent.add(o);
    return o;
  }
  function box(w, h, d, mat, pos = [0, 0, 0], round = 0.035) {
    if (!round) return add(new T.BoxGeometry(w, h, d), mat, pos);
    const r = Math.min(round, w * 0.2, h * 0.2, d * 0.2),
      s = new T.Shape(),
      x = -w / 2,
      y = -h / 2;
    s.moveTo(x + r, y);
    s.lineTo(x + w - r, y);
    s.quadraticCurveTo(x + w, y, x + w, y + r);
    s.lineTo(x + w, y + h - r);
    s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    s.lineTo(x + r, y + h);
    s.quadraticCurveTo(x, y + h, x, y + h - r);
    s.lineTo(x, y + r);
    s.quadraticCurveTo(x, y, x + r, y);
    const g = new T.ExtrudeGeometry(s, {
      depth: d - 2 * r,
      steps: 1,
      bevelEnabled: true,
      bevelSize: r,
      bevelThickness: r,
      bevelSegments: 3,
      curveSegments: 6,
    });
    g.translate(0, 0, -d / 2 + r);
    return add(g, mat, pos);
  }
  function cyl(r, len, mat, pos = [0, 0, 0], axis = 'z', r2 = r, n = 32) {
    const o = add(new T.CylinderGeometry(r, r2, len, n), mat, pos);
    if (axis === 'z') o.rotation.x = Math.PI / 2;
    if (axis === 'x') o.rotation.z = Math.PI / 2;
    return o;
  }
  function torus(r, t, mat, pos = [0, 0, 0]) {
    return add(new T.TorusGeometry(r, t, 8, 48), mat, pos);
  }
  function rod(a, b, r, mat) {
    const from = new T.Vector3(...a),
      to = new T.Vector3(...b),
      o = cyl(r, from.distanceTo(to), mat, [0, 0, 0], 'y');
    o.position.copy(from).lerp(to, 0.5);
    o.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), to.sub(from).normalize());
    return o;
  }
  function tube(points, r, mat) {
    return add(
      new T.TubeGeometry(
        new T.CatmullRomCurve3(points.map((x) => new T.Vector3(...x))),
        36,
        r,
        7,
        false,
      ),
      mat,
    );
  }
  function bolt(x, y, z) {
    cyl(0.025, 0.014, silver, [x, y, z]);
    cyl(0.011, 0.017, black, [x, y, z + 0.008], 'z', 0.011, 6);
  }
  function connector(x, y, z, w = 0.16) {
    box(w, 0.11, 0.13, black, [x, y, z], 0.012);
    for (let i = 0; i < 3; i++)
      cyl(0.008, 0.012, gold, [x - w * 0.28 + i * w * 0.28, y, z + 0.074]);
  }
  function fins(w, h, d, mat = silver) {
    box(w, h, d, black);
    for (let i = 0; i < 12; i++)
      box(w * 0.92, h * 0.13, 0.014, mat, [0, h * 0.56, -d * 0.43 + i * d * 0.078], 0.002);
  }
  function rotor(r = 0.53, z = 0) {
    const shape = new T.Shape();
    shape.absarc(0, 0, r, 0, Math.PI * 2, false);
    const center = new T.Path();
    center.absarc(0, 0, r * 0.57, 0, Math.PI * 2, true);
    shape.holes.push(center);
    for (let i = 0; i < 24; i++) {
      const a = (i / 24) * Math.PI * 2,
        hole = new T.Path();
      hole.absarc(Math.cos(a) * r * 0.81, Math.sin(a) * r * 0.81, r * 0.037, 0, Math.PI * 2, true);
      shape.holes.push(hole);
    }
    add(
      new T.ExtrudeGeometry(shape, { depth: 0.017, bevelEnabled: false, curveSegments: 24 }),
      silver,
      [0, 0, z],
    );
    for (let i = 0; i < 6; i++) {
      const a = (i / 6) * Math.PI * 2;
      rod(
        [Math.cos(a) * r * 0.16, Math.sin(a) * r * 0.16, z],
        [Math.cos(a + 0.12) * r * 0.62, Math.sin(a + 0.12) * r * 0.62, z],
        0.022,
        dark,
      );
    }
    torus(r * 0.18, 0.014, dark, [0, 0, z]);
  }
  switch (info.family) {
    case 'reference-hub': {
      const q = info.model,
        depth = q.depth,
        r = 0.46,
        metal = q.rim === 'gray' ? make(0x747e75, 0.7) : silver;
      cyl(r, depth, black);
      for (const side of [-1, 1]) {
        const z = side * (depth / 2 + 0.012);
        cyl(r * 0.91, 0.018, q.rim === 'gray' ? metal : black, [0, 0, z]);
        torus(r * 0.91, 0.014, q.rim === 'silver' ? silver : dark, [0, 0, z]);
        for (let i = 0; i < q.bolts; i++) {
          const a = (i / q.bolts) * Math.PI * 2;
          bolt(Math.cos(a) * r * 0.81, Math.sin(a) * r * 0.81, z);
        }
      }
      if (q.radial)
        for (let i = 0; i < q.radial; i++) {
          const a = (i / q.radial) * Math.PI * 2;
          const fin = box(
            0.16,
            0.013,
            depth * 0.88,
            dark,
            [Math.cos(a) * r, Math.sin(a) * r, 0],
            0.002,
          );
          fin.rotation.z = a;
        }
      if (q.spokes) {
        cyl(0.31, depth + 0.05, black);
        for (let i = 0; i < q.spokes; i++) {
          const a = (i / q.spokes) * Math.PI * 2;
          const spoke = box(
            0.25,
            0.055,
            0.028,
            q.rim === 'silver' ? silver : dark,
            [Math.cos(a) * 0.33, Math.sin(a) * 0.33, depth / 2 + 0.027],
            0.015,
          );
          spoke.rotation.z = a + 0.27;
        }
        torus(0.48, 0.029, q.rim === 'silver' ? silver : black, [0, 0, 0]);
      }
      if (q.tire !== 'none') {
        const color = q.rim === 'orange' ? make(0xdd9b24, 0.05, 0.85) : rubber;
        if (q.tire === 'perforated') {
          const ring = new T.Shape();
          ring.absarc(0, 0, 0.61, 0, Math.PI * 2, false);
          const hole = new T.Path();
          hole.absarc(0, 0, 0.46, 0, Math.PI * 2, true);
          ring.holes.push(hole);
          for (let i = 0; i < 24; i++) {
            const a = (i / 24) * Math.PI * 2,
              h = new T.Path();
            h.absarc(Math.cos(a) * 0.537, Math.sin(a) * 0.537, 0.033, 0, Math.PI * 2, true);
            ring.holes.push(h);
          }
          add(
            new T.ExtrudeGeometry(ring, {
              depth: depth * 0.72,
              bevelEnabled: true,
              bevelSize: 0.006,
              bevelThickness: 0.006,
              bevelSegments: 2,
              curveSegments: 24,
            }),
            rubber,
            [0, 0, -depth * 0.36],
          );
        } else {
          torus(0.52, 0.104, color);
          if (q.tire === 'knobby')
            for (let i = 0; i < 38; i++)
              for (const z of [-0.065, 0, 0.065]) {
                const a = (i / 38) * Math.PI * 2 + (z === 0 ? 0.03 : 0),
                  block = box(
                    0.038,
                    0.017,
                    0.048,
                    rubber,
                    [Math.cos(a) * 0.622, Math.sin(a) * 0.622, z],
                    0.004,
                  );
                block.rotation.z = a - Math.PI / 2;
              }
          else
            for (let i = 0; i < 30; i++) {
              const a = (i / 30) * Math.PI * 2;
              const groove = box(
                0.06,
                0.008,
                0.14,
                dark,
                [Math.cos(a) * 0.619, Math.sin(a) * 0.619, 0],
                0.001,
              );
              groove.rotation.z = a + 0.42;
            }
        }
      }
      const length = q.axle === 'single' ? 0.27 : depth + 0.35;
      cyl(0.035, length, silver, [0, 0, q.axle === 'single' ? depth / 2 + 0.1 : 0]);
      cyl(0.075, 0.05, silver, [0, 0, depth / 2 + 0.1], 'z', 0.065, 6);
      for (let i = 0; i < 3; i++)
        tube(
          [
            [0, 0, -depth / 2 - 0.15],
            [0.14, -0.14, -depth / 2 - 0.24],
            [0.46, -0.26, -depth / 2 - 0.18],
          ],
          0.011,
          [gold, blue, black][i],
        );
      break;
    }
    case 'reference-mid': {
      const q = info.model,
        face = make(q.color, 0.58, 0.35);
      cyl(q.radius, q.depth, black);
      for (let i = 0; i < q.fins; i++) {
        const a = (i / q.fins) * Math.PI * 2,
          fin = box(
            0.11,
            0.012,
            q.depth * 0.86,
            dark,
            [Math.cos(a) * q.radius, Math.sin(a) * q.radius, 0],
            0.002,
          );
        fin.rotation.z = a;
      }
      cyl(q.radius * 0.85, 0.032, q.cover === 'round' ? silver : face, [0, 0, q.depth / 2 + 0.016]);
      cyl(q.radius * 0.56, 0.04, q.cover === 'round' ? face : black, [0, 0, q.depth / 2 + 0.045]);
      if (q.cover !== 'round')
        for (let i = 0; i < (q.cover === 'ultra' ? 10 : 7); i++) {
          const a = (i / (q.cover === 'ultra' ? 10 : 7)) * Math.PI * 2,
            spoke = box(
              q.radius * 0.55,
              0.035,
              0.025,
              face,
              [Math.cos(a) * q.radius * 0.58, Math.sin(a) * q.radius * 0.58, q.depth / 2 + 0.05],
              0.012,
            );
          spoke.rotation.z = a;
        }
      for (let i = 0; i < 8; i++) {
        const a = (i / 8) * Math.PI * 2;
        bolt(Math.cos(a) * q.radius * 0.73, Math.sin(a) * q.radius * 0.73, q.depth / 2 + 0.075);
      }
      cyl(0.055, 0.18, silver, [0, 0, q.depth / 2 + 0.15]);
      for (const x of [-q.radius * 0.76, q.radius * 0.76])
        box(0.13, 0.14, 0.14, black, [x, -q.radius * 0.75, 0], 0.02);
      for (let i = 0; i < 3; i++) {
        cyl(0.034, 0.055, gold, [-0.12 + i * 0.12, q.radius * 0.91, -q.depth * 0.25], 'y');
        tube(
          [
            [-0.12 + i * 0.12, q.radius, -q.depth * 0.25],
            [-0.16 + i * 0.13, q.radius + 0.2, -0.14],
            [-0.26 + i * 0.15, q.radius + 0.29, -0.17],
          ],
          0.014,
          black,
        );
      }
      break;
    }
    case 'reference-controller': {
      const q = info.model,
        color = make(q.color, 0.45, 0.43),
        w = q.width,
        h = q.height,
        d = q.depth;
      box(w, h, d, color, [0, 0, 0], 0.045);
      if (q.style === 'flipsky') {
        box(w, h, 0.025, silver, [0, 0, -d / 2], 0.007);
        for (let i = 0; i < q.capacitors; i++) {
          const cols = q.capacitors === 9 ? 3 : 3,
            rows = q.capacitors / cols,
            x = ((i % cols) - 1) * w * 0.24,
            y = h * 0.36 - Math.floor(i / cols) * 0.1;
          cyl(0.045, 0.09, black, [x, y, d / 2 + 0.04]);
          cyl(0.033, 0.003, make(0xc9ca6c, 0.2), [x, y, d / 2 + 0.087]);
        }
        for (let i = 0; i < 2; i++)
          tube(
            [
              [-w * 0.25 + i * w * 0.5, h * 0.48, 0],
              [-w * 0.25 + i * w * 0.5, h * 0.8, 0],
              [-w * 0.22 + i * w * 0.45, h * 0.98, 0.02],
            ],
            0.018,
            i ? red : black,
          );
        for (let i = 0; i < 3; i++) {
          const x = -w * 0.25 + i * w * 0.25;
          tube(
            [
              [x, -h * 0.48, 0],
              [x, -h * 0.75, 0.025],
              [x + 0.035, -h * 0.93, 0.025],
            ],
            0.019,
            [gold, green, blue][i],
          );
        }
        for (let i = 0; i < 5; i++)
          box(0.065, 0.055, 0.03, silver, [w * 0.28, h * 0.1 - i * 0.12, d / 2 + 0.02], 0.006);
        connector(-w * 0.15, -h * 0.3, d / 2 + 0.02, w * 0.36);
      } else if (q.style === 'ubox') {
        box(w, h, 0.035, dark, [0, 0, -d / 2], 0.02);
        for (let i = 0; i < 4; i++) {
          box(0.18, 0.055, 0.008, silver, [-0.4 + i * 0.25, h * 0.32, d / 2 + 0.01], 0.004);
          box(0.14, 0.027, 0.014, black, [-0.4 + i * 0.25, h * 0.32, d / 2 + 0.02], 0.002);
        }
        box(0.05, 0.12, 0.01, silver, [-w * 0.31, -0.03, d / 2 + 0.01], 0.004);
        box(0.13, 0.05, 0.01, silver, [w * 0.22, -h * 0.21, d / 2 + 0.01], 0.004);
        for (let i = 0; i < 3; i++)
          tube(
            [
              [-0.23 + i * 0.23, -h * 0.48, 0],
              [-0.23 + i * 0.23, -h * 0.75, 0.01],
              [-0.19 + i * 0.24, -h * 0.93, 0.01],
            ],
            0.033,
            black,
          );
        for (let i = 0; i < 2; i++)
          tube(
            [
              [-w * 0.49, h * 0.28 - i * h * 0.45, 0],
              [-w * 0.72, h * 0.29 - i * h * 0.47, 0],
              [-w * 0.88, h * 0.26 - i * h * 0.5, 0],
            ],
            0.028,
            i ? red : black,
          );
        for (const x of [-w * 0.4, w * 0.4]) {
          box(0.19, 0.12, 0.05, black, [x, -h * 0.55, -d * 0.2], 0.015);
          cyl(0.025, 0.06, silver, [x, -h * 0.55, -d * 0.2]);
        }
      } else if (q.style === 'fardriver-blue') {
        box(w + 0.09, h + 0.07, 0.07, silver, [0, 0, -d / 2], 0.025);
        for (let i = 0; i < 5; i++) {
          const x = -w * 0.35 + i * w * 0.175;
          cyl(0.047, 0.07, gold, [x, h * 0.25, d / 2 + 0.045]);
          torus(0.059, 0.013, [gold, red, blue, green, black][i], [x, h * 0.25, d / 2 + 0.07]);
        }
        connector(0, -h * 0.3, d / 2 + 0.015, w * 0.48);
        for (let i = 0; i < 9; i++)
          box(0.018, h * 0.86, 0.02, dark, [-w * 0.4 + i * w * 0.1, 0, -d / 2 - 0.035], 0.002);
      } else if (q.style === 'asi') {
        box(w + 0.1, h + 0.08, 0.055, silver, [0, 0, -d / 2], 0.025);
        for (const side of [-1, 1]) box(0.08, h, 0.21, blue, [side * w * 0.47, 0, 0.03], 0.018);
        for (let i = 0; i < 4; i++) {
          cyl(0.045, 0.055, gold, [-w * 0.26 + i * w * 0.17, h * 0.18, d / 2 + 0.045]);
          cyl(0.021, 0.06, silver, [-w * 0.26 + i * w * 0.17, h * 0.18, d / 2 + 0.075]);
        }
        connector(0, -h * 0.29, d / 2 + 0.01, w * 0.5);
      } else if (q.style === 'pcb') {
        box(w + 0.07, h + 0.06, 0.025, silver, [0, 0, -d / 2], 0.01);
        for (let i = 0; i < 3; i++)
          cyl(0.053, 0.11, dark, [-w * 0.27 + i * w * 0.24, h * 0.22, d / 2 + 0.06]);
        box(w * 0.4, h * 0.15, 0.035, blue, [w * 0.13, -h * 0.12, d / 2 + 0.02], 0.004);
        for (let i = 0; i < 10; i++)
          box(0.032, 0.06, 0.025, gold, [-w * 0.4 + i * w * 0.08, h * 0.42, d / 2 + 0.035], 0.002);
        for (let i = 0; i < 5; i++)
          tube(
            [
              [-w * 0.32 + i * w * 0.15, h * 0.4, 0.04],
              [-w * 0.25 + i * w * 0.13, h * 0.85, 0.08],
              [-w * 0.15 + i * w * 0.1, h * 1.07, 0.1],
            ],
            0.015,
            [red, black, blue, gold, green][i],
          );
      } else if (q.style.startsWith('oem')) {
        const isBlack = q.style === 'oem-black';
        box(w + 0.1, h + 0.1, 0.04, silver, [0, 0, -d / 2], 0.01);
        if (isBlack)
          for (let i = 0; i < 8; i++)
            box(w * 0.95, 0.025, 0.024, dark, [0, -h * 0.45 + i * h * 0.125, d / 2 + 0.012], 0.004);
        box(w * 0.5, h * 0.42, 0.003, white, [0, h * 0.06, d / 2 + 0.028], 0.002);
        for (let i = 0; i < 8; i++)
          tube(
            [
              [-w * 0.48, -h * 0.25 + i * h * 0.06, 0],
              [-w * 0.78, -h * 0.34 + i * h * 0.1, 0.04],
              [-w * 0.9, -h * 0.49 + i * h * 0.12, 0.08],
            ],
            0.012,
            [red, black, gold, blue, green, white, black, red][i],
          );
      } else {
        const fins =
          q.style === 'nano' ? 8 : q.style === 'nucular' ? 7 : q.style === 'ebmx' ? 14 : 10;
        for (let i = 0; i < fins; i++) {
          const x = -w * 0.4 + (i * w * 0.8) / (fins - 1),
            fin = box(
              0.018,
              h * 0.82,
              0.025,
              q.style === 'nucular' ? dark : color,
              [x, 0, d / 2 + 0.015],
              0.004,
            );
          if (['nucular', 'torp500', 'torp1000', 'ko-pro', 'ebmx'].includes(q.style))
            fin.rotation.z = x > 0 ? -0.16 : 0.16;
        }
        for (const side of [-1, 1])
          box(0.06, h * 0.95, 0.07, dark, [side * (w / 2 + 0.018), 0, -d * 0.1], 0.018);
        for (let i = 0; i < 3; i++)
          cyl(0.035, 0.05, gold, [-w * 0.28 + i * w * 0.28, h / 2 + 0.03, 0], 'y');
        connector(0, -h / 2 - 0.01, 0.02, w * 0.61);
        if (q.style === 'nano') box(0.12, h * 0.72, 0.006, white, [0, 0, d / 2 + 0.035], 0.002);
        else
          box(
            w * 0.37,
            h * 0.12,
            0.004,
            q.style.startsWith('torp') ? white : dark,
            [0, 0, d / 2 + 0.035],
            0.003,
          );
      }
      for (const x of [-w * 0.43, w * 0.43])
        for (const y of [-h * 0.42, h * 0.42]) bolt(x, y, d / 2 + 0.03);
      break;
    }
    case 'reference-battery': {
      const q = info.model,
        w = 0.59,
        h = q.height,
        d = q.depth;
      box(w, h, d, make(0x24272a, 0.37, 0.65), [0, 0, 0], q.shape === 'titan' ? 0.045 : 0.01);
      box(w + 0.01, 0.04, d + 0.01, black, [0, h / 2 - 0.035, 0], 0.015);
      if (q.shape === 'titan')
        tube(
          [
            [-0.2, h / 2, 0.02],
            [-0.2, h / 2 + 0.17, 0.02],
            [0.2, h / 2 + 0.17, 0.02],
            [0.2, h / 2, 0.02],
          ],
          0.023,
          rubber,
        );
      else
        tube(
          [
            [-0.14, h / 2, 0.05],
            [-0.12, h / 2 + 0.11, 0.04],
            [0.13, h / 2 + 0.11, 0.04],
            [0.15, h / 2, 0.04],
          ],
          0.019,
          black,
        );
      connector(0.12, h / 2 + 0.02, 0.08, 0.14);
      box(0.19, 0.2, 0.002, white, [0, h * 0.22, d / 2 + 0.004], 0.001);
      box(0.13, 0.16, 0.004, black, [0, h * 0.22, d / 2 + 0.007], 0.001);
      for (let i = 0; i < 4; i++)
        box(0.12, 0.005, 0.003, dark, [0, h * 0.27 - i * 0.029, d / 2 + 0.01], 0);
      break;
    }
    case 'reference-display': {
      const portrait = p.brand === 'Nucular',
        w = portrait ? 0.59 : 0.86,
        h = portrait ? 0.83 : 0.68;
      box(w, h, 0.14, black, [0, 0, 0], 0.05);
      box(w * 0.79, h * 0.65, 0.012, make(0x244339, 0.03, 0.23), [0, h * 0.08, 0.08], 0.025);
      box(w * 0.68, h * 0.13, 0.013, silver, [0, -h * 0.35, 0.082], 0.012);
      if (!portrait)
        for (const x of [-0.28, 0.28]) {
          rod([x, -0.3, 0], [x, -0.5, -0.1], 0.027, dark);
          torus(0.09, 0.02, black, [x, -0.49, -0.1]);
        }
      break;
    }
    case 'reference-bluetooth':
      box(0.85, 0.16, 0.055, white);
      box(0.39, 0.17, 0.065, black, [0, 0, 0.018], 0.01);
      cyl(0.025, 0.017, gold, [0.09, 0, 0.06]);
      box(0.07, 0.05, 0.025, blue, [-0.07, 0.03, 0.065], 0.003);
      break;
    case 'reference-throttle':
      cyl(0.13, 0.19, black);
      torus(0.09, 0.017, dark, [0, 0, 0.11]);
      rod([0, -0.1, 0], [0, -0.39, 0.03], 0.047, black);
      box(0.27, 0.11, 0.16, rubber, [0, -0.42, 0.03], 0.025);
      tube(
        [
          [0, 0.1, 0],
          [0, 0.53, 0],
          [0.05, 0.7, 0.02],
        ],
        0.014,
        black,
      );
      break;
    case 'reference-pads':
      for (const side of [-1, 1]) {
        const x = side * 0.25;
        box(0.37, 0.42, 0.045, make(0xb27c6e, 0.55), [x, 0, 0], 0.07);
        box(0.29, 0.29, 0.014, rubber, [x, -0.035, 0.036], 0.04);
        torus(0.038, 0.016, silver, [x, 0.245, 0]);
      }
      break;
    case 'reference-jackshaft':
      cyl(0.095, 1.12, black, [0, 0, 0], 'x');
      for (const x of [-0.4, 0.12]) cyl(0.2, 0.09, dark, [x, 0, 0], 'x');
      cyl(0.27, 0.08, silver, [0.43, 0, 0], 'x');
      for (let i = 0; i < 25; i++) {
        const a = (i / 25) * Math.PI * 2,
          block = box(
            0.07,
            0.035,
            0.045,
            dark,
            [0.43, Math.cos(a) * 0.28, Math.sin(a) * 0.28],
            0.002,
          );
        block.rotation.x = a;
      }
      box(0.17, 0.29, 0.24, black, [-0.48, 0, 0], 0.03);
      break;
    case 'reference-linkage': {
      const shape = new T.Shape();
      shape.moveTo(-0.48, -0.31);
      shape.lineTo(0.48, -0.31);
      shape.lineTo(0.19, 0.47);
      shape.lineTo(-0.19, 0.47);
      shape.closePath();
      const hole = new T.Path();
      hole.moveTo(-0.28, -0.14);
      hole.lineTo(0.28, -0.14);
      hole.lineTo(0.1, 0.24);
      hole.lineTo(-0.1, 0.24);
      hole.closePath();
      shape.holes.push(hole);
      add(
        new T.ExtrudeGeometry(shape, {
          depth: 0.055,
          bevelEnabled: true,
          bevelSize: 0.01,
          bevelThickness: 0.01,
          bevelSegments: 2,
        }),
        black,
      );
      for (const x of [-0.44, 0.44]) torus(0.028, 0.013, silver, [x, -0.25, 0.065]);
      box(0.14, 0.82, 0.055, black, [-0.68, 0, 0], 0.025);
      break;
    }
    case 'reference-mount':
      box(0.65, 1.02, 0.055, black, [0, 0, 0], 0.025);
      for (const x of [-0.3, 0.3]) {
        const side = new T.Shape();
        side.moveTo(0, -0.51);
        side.lineTo(0.32, -0.51);
        side.lineTo(0, 0.51);
        side.closePath();
        const obj = add(new T.ExtrudeGeometry(side, { depth: 0.03, bevelEnabled: false }), dark, [
          x,
          0,
          0,
        ]);
        obj.rotation.y = Math.PI / 2;
      }
      for (const x of [-0.25, 0.25]) for (const y of [-0.4, 0.4]) bolt(x, y, 0.035);
      break;

    case 'chosen-brake': {
      const accent = make(info.model.accent, 0.25),
        caliperX = 0.32,
        caliperY = -0.2;
      box(0.45, 0.25, 0.17, black, [caliperX, caliperY, 0], 0.055);
      box(0.32, 0.29, 0.12, black, [caliperX, caliperY + 0.015, 0.05], 0.04);
      for (const x of [-0.12, 0.12]) {
        cyl(0.072, 0.025, accent, [caliperX + x, caliperY, 0.12]);
        cyl(0.048, 0.03, black, [caliperX + x, caliperY, 0.135]);
      }
      for (const x of [-0.17, 0.17]) bolt(caliperX + x, caliperY + 0.1, 0.1);
      torus(0.09, 0.026, black, [-0.32, 0.3, 0]);
      box(0.24, 0.13, 0.13, black, [-0.22, 0.29, 0.04], 0.03);
      const hc = info.model.lever === 'hc';
      tube(
        [
          [-0.23, 0.23, 0.12],
          [-0.43, 0.15, 0.13],
          [-0.57, 0.04, 0.13],
          [-0.6, hc ? -0.1 : -0.18, 0.13],
        ],
        0.028,
        black,
      );
      box(0.19, 0.07, 0.03, accent, [-0.21, 0.3, 0.12], 0.012);
      tube(
        [
          [-0.12, 0.32, 0],
          [0.14, 0.6, -0.02],
          [0.67, 0.43, -0.06],
          [0.61, -0.07, 0],
          [0.43, -0.11, 0.04],
        ],
        0.012,
        black,
      );
      break;
    }
    case 'chosen-rotor': {
      const r = info.model.diameter / 360,
        shape = new T.Shape();
      for (let i = 0; i <= 144; i++) {
        const a = (i / 144) * Math.PI * 2,
          rr = r * (1 + 0.012 * Math.sin(a * 24));
        if (i === 0) shape.moveTo(Math.cos(a) * rr, Math.sin(a) * rr);
        else shape.lineTo(Math.cos(a) * rr, Math.sin(a) * rr);
      }
      shape.closePath();
      const center = new T.Path();
      center.absarc(0, 0, r * 0.19, 0, Math.PI * 2, true);
      shape.holes.push(center);
      for (let i = 0; i < 6; i++) {
        const a = (i / 6) * Math.PI * 2,
          h = new T.Path(),
          pt = (radius, angle) => [Math.cos(angle) * radius, Math.sin(angle) * radius];
        h.moveTo(...pt(r * 0.32, a));
        h.bezierCurveTo(
          ...pt(r * 0.5, a + 0.05),
          ...pt(r * 0.74, a + 0.2),
          ...pt(r * 0.78, a + 0.4),
        );
        h.lineTo(...pt(r * 0.72, a + 0.73));
        h.bezierCurveTo(
          ...pt(r * 0.48, a + 0.54),
          ...pt(r * 0.37, a + 0.39),
          ...pt(r * 0.32, a + 0.25),
        );
        h.closePath();
        shape.holes.push(h);
        const boltHole = new T.Path();
        boltHole.absarc(
          Math.cos(a) * r * 0.25,
          Math.sin(a) * r * 0.25,
          r * 0.026,
          0,
          Math.PI * 2,
          true,
        );
        shape.holes.push(boltHole);
      }
      for (let i = 0; i < 36; i++) {
        const a = (i / 36) * Math.PI * 2,
          h = new T.Path();
        h.absarc(Math.cos(a) * r * 0.91, Math.sin(a) * r * 0.91, r * 0.025, 0, Math.PI * 2, true);
        shape.holes.push(h);
      }
      add(
        new T.ExtrudeGeometry(shape, { depth: 0.014, bevelEnabled: false, curveSegments: 24 }),
        silver,
      );
      break;
    }
    case 'chosen-tire': {
      const q = info.model,
        tire = torus(0.48, 0.105, rubber);
      tire.scale.z = q.width / 0.16;
      for (const side of [-1, 1]) {
        torus(0.39, 0.009, dark, [0, 0, side * q.width * 0.45]);
        torus(0.42, 0.004, black, [0, 0, side * q.width * 0.59]);
      }
      if (q.pattern === 'road')
        for (let i = 0; i < 34; i++) {
          const a = (i / 34) * Math.PI * 2,
            groove = box(
              0.06,
              0.006,
              q.width * 0.95,
              dark,
              [Math.cos(a) * 0.583, Math.sin(a) * 0.583, 0],
              0.001,
            );
          groove.rotation.z = a + 0.5;
        }
      else
        for (let i = 0; i < 40; i++)
          for (let row = -1; row <= 1; row++) {
            const a = (i / 40) * Math.PI * 2 + (row === 0 ? 0.025 : 0),
              knob = box(
                q.pattern === 'trials' ? 0.042 : 0.055,
                0.018,
                q.width * 0.28,
                rubber,
                [Math.cos(a) * 0.585, Math.sin(a) * 0.585, row * q.width * 0.32],
                0.004,
              );
            knob.rotation.z = a - Math.PI / 2;
          }
      break;
    }
    case 'chosen-fork': {
      for (const x of [-0.23, 0.23]) {
        cyl(0.047, 1.0, gold, [x, 0.23, 0], 'y');
        cyl(0.073, 0.72, black, [x, -0.42, 0], 'y');
        cyl(0.082, 0.045, silver, [x, -0.04, 0], 'y');
        box(0.16, 0.1, 0.17, black, [x, -0.8, 0], 0.026);
        bolt(x, -0.8, 0.1);
        box(0.082, 0.25, 0.004, white, [x, -0.39, 0.074], 0.005);
      }
      for (const y of [0.56, 0.78]) box(0.65, 0.056, 0.19, black, [0, y, 0], 0.02);
      cyl(0.035, 0.32, black, [0, 0.93, 0], 'y');
      rod([-0.23, -0.8, 0], [0.23, -0.8, 0], 0.025, silver);
      tube(
        [
          [-0.23, -0.1, 0.04],
          [-0.17, 0.02, 0.08],
          [0.17, 0.02, 0.08],
          [0.23, -0.1, 0.04],
        ],
        0.047,
        black,
      );
      break;
    }
    case 'chosen-coil': {
      cyl(0.034, 0.95, silver, [0, 0, 0], 'y');
      cyl(0.085, 0.37, black, [0, 0.25, 0], 'y');
      for (const y of [-0.58, 0.58]) torus(0.063, 0.025, dark, [0, y, 0]);
      for (const y of [-0.4, 0.4]) cyl(0.135, 0.033, dark, [0, y, 0], 'y');
      const pts = [];
      for (let i = 0; i < 220; i++) {
        const t = i / 219,
          a = t * Math.PI * 2 * 8;
        pts.push([Math.cos(a) * 0.11, -0.38 + t * 0.76, Math.sin(a) * 0.11]);
      }
      tube(pts, 0.022, black);
      cyl(0.078, 0.35, dark, [0.19, 0.24, 0], 'y');
      box(0.13, 0.22, 0.003, silver, [0.19, 0.23, 0.079], 0.003);
      cyl(0.055, 0.07, blue, [0.19, 0.46, 0], 'y');
      rod([0, 0.43, 0], [0.19, 0.43, 0], 0.04, black);
      break;
    }
    case 'chosen-grips': {
      const color = make(info.model.color, 0.05, 0.85);
      for (const side of [-1, 1]) {
        const shape = new T.Shape();
        shape.absarc(0, 0, 0.09, 0, Math.PI * 2, false);
        const hole = new T.Path();
        hole.absarc(0, 0, 0.041, 0, Math.PI * 2, true);
        shape.holes.push(hole);
        const grip = add(
          new T.ExtrudeGeometry(shape, {
            depth: 0.54,
            bevelEnabled: true,
            bevelSize: 0.005,
            bevelThickness: 0.005,
            bevelSegments: 2,
            curveSegments: 30,
          }),
          color,
          [side * 0.35 - 0.27, 0, 0],
        );
        grip.rotation.y = Math.PI / 2;
        for (let i = 0; i < 10; i++)
          for (let row = 0; row < 10; row++) {
            const a = (row / 10) * Math.PI * 2,
              block = box(
                0.039,
                0.014,
                0.039,
                color,
                [side * 0.35 - 0.24 + i * 0.052, Math.cos(a) * 0.091, Math.sin(a) * 0.091],
                0.006,
              );
            block.rotation.x = a;
          }
        for (const x of [side * 0.35 - 0.27, side * 0.35 + 0.27]) {
          const ring = torus(0.091, 0.009, color, [x, 0, 0]);
          ring.rotation.y = Math.PI / 2;
        }
      }
      break;
    }
    case 'chosen-charger': {
      box(1.2, 0.52, 0.45, black, [0, 0, 0], 0.025);
      for (let i = 0; i < 15; i++) box(0.025, 0.51, 0.48, dark, [-0.55 + i * 0.078, 0, 0], 0.003);
      box(0.24, 0.18, 0.015, make(0x244f65, 0.05), [0.37, 0.06, 0.25], 0.012);
      for (let i = 0; i < 3; i++) {
        cyl(0.033, 0.03, gold, [0.22 + i * 0.12, -0.15, 0.25]);
        cyl(0.017, 0.032, black, [0.22 + i * 0.12, -0.15, 0.267]);
      }
      tube(
        [
          [-0.6, 0, 0],
          [-0.78, -0.13, 0.04],
          [-0.69, -0.44, 0.08],
          [-0.33, -0.42, 0.1],
        ],
        0.018,
        black,
      );
      box(0.14, 0.07, 0.1, gold, [-0.24, -0.42, 0.1], 0.015);
      break;
    }
    case 'chosen-connector': {
      for (const side of [-1, 1]) {
        const x = side * 0.31;
        box(0.34, 0.32, 0.25, black, [x, 0, 0], 0.035);
        for (const dx of [-0.075, 0.075]) {
          cyl(0.045, 0.033, gold, [x + dx, -0.045, 0.14]);
          cyl(0.026, 0.04, dark, [x + dx, -0.045, 0.162]);
        }
        box(0.15, 0.035, 0.02, red, [x, 0.09, 0.14], 0.003);
        for (let i = 0; i < 2; i++)
          tube(
            [
              [x - 0.07 + i * 0.14, 0.15, 0],
              [x - 0.07 + i * 0.14, 0.48, 0],
              [x - 0.02 + i * 0.14, 0.7, 0.05],
            ],
            0.021,
            black,
          );
      }
      break;
    }
    case 'chosen-scooter-pack': {
      const layout = info.model.layout,
        isG4 = layout === 'G4',
        isG2 = layout === 'G2',
        isMaster = layout === 'G2 Master',
        w = isG4 ? 1.38 : isG2 ? 1.04 : 1.2,
        h = isG4 ? 0.46 : isG2 ? 0.46 : 0.43,
        d = isG4 ? 0.16 : isG2 ? 0.32 : 0.27;
      box(w, h, d, isMaster ? blue : black, [0, 0, 0], isG4 ? 0.008 : 0.025);
      box(0.22, 0.13, 0.003, white, [0, 0, d / 2 + 0.003], 0.004);
      if (isG2)
        for (const x of [-w * 0.27, w * 0.27])
          box(0.055, h + 0.01, d + 0.01, dark, [x, 0, 0], 0.008);
      for (let i = 0; i < 2; i++) {
        tube(
          [
            [-w / 2, 0.06 - i * 0.14, 0],
            [-w * 0.63, 0.09 - i * 0.12, 0.04],
            [-w * 0.77, 0.12 - i * 0.12, 0.07],
          ],
          0.017,
          i ? black : red,
        );
        box(0.1, 0.06, 0.09, gold, [-w * 0.81, -0.02, 0.07], 0.009);
      }
      break;
    }
    case 'chosen-dashboard': {
      const basic = ['G2', 'G4'].includes(info.model.layout),
        shape = new T.Shape(),
        points = basic
          ? [
              [-0.5, -0.24],
              [0.5, -0.24],
              [0.45, 0.12],
              [0.25, 0.3],
              [-0.25, 0.3],
              [-0.45, 0.12],
            ]
          : [
              [-0.58, -0.17],
              [-0.38, -0.39],
              [0.38, -0.39],
              [0.58, -0.17],
              [0.42, 0.36],
              [-0.42, 0.36],
            ];
      shape.moveTo(...points[0]);
      for (const p of points.slice(1)) shape.lineTo(...p);
      shape.closePath();
      add(
        new T.ExtrudeGeometry(shape, {
          depth: 0.16,
          bevelEnabled: true,
          bevelSize: 0.035,
          bevelThickness: 0.025,
          bevelSegments: 4,
        }),
        black,
        [0, 0, -0.08],
      );
      if (basic) {
        box(0.74, 0.085, 0.008, silver, [0, -0.08, 0.113], 0.015);
        for (let i = 0; i < 5; i++)
          box(0.08, 0.04, 0.012, white, [-0.25 + i * 0.125, -0.08, 0.12], 0.006);
        box(0.34, 0.1, 0.015, dark, [0, 0.12, 0.105], 0.012);
      } else {
        const screen = meshScreen();
        function meshScreen() {
          const s = new T.Shape();
          s.moveTo(-0.47, -0.13);
          s.lineTo(-0.31, -0.28);
          s.lineTo(0.31, -0.28);
          s.lineTo(0.47, -0.13);
          s.lineTo(0.34, 0.25);
          s.lineTo(-0.34, 0.25);
          s.closePath();
          return add(
            new T.ExtrudeGeometry(s, { depth: 0.006, bevelEnabled: false }),
            make(0x14251f, 0.05, 0.24),
            [0, 0, 0.115],
          );
        }
        for (const x of [-0.32, 0.32]) {
          rod([x, 0.32, 0], [x, 0.57, -0.08], 0.032, black);
          torus(0.08, 0.023, black, [x, 0.59, -0.08]);
        }
        box(0.22, 0.04, 0.006, white, [0, 0.31, 0.12], 0.003);
      }
      tube(
        [
          [0, -0.21, -0.09],
          [0.14, -0.53, -0.14],
          [0.36, -0.58, -0.1],
        ],
        0.014,
        black,
      );
      break;
    }

    case 'nd72260': {
      root.name = 'ND72260 — green cover, metal base and recessed multi-pin socket';
      box(1.42, 0.8, 0.12, silver, [0, 0, -0.12], 0.055);
      box(1.36, 0.75, 0.22, green, [0, 0.025, 0], 0.075);
      box(1.26, 0.41, 0.045, green, [0, -0.095, 0.133], 0.035);
      // Raised corner shoulders and a recessed black connector cavity on the top edge.
      for (const x of [-0.5, 0.5]) box(0.32, 0.18, 0.22, green, [x, 0.39, 0], 0.05);
      box(0.52, 0.13, 0.09, dark, [0, 0.34, 0.07], 0.018);
      box(0.46, 0.09, 0.015, black, [0, 0.34, 0.126], 0.006);
      for (let row = 0; row < 2; row++)
        for (let i = 0; i < 10; i++)
          cyl(0.007, 0.02, gold, [-0.19 + i * 0.042, 0.32 + row * 0.037, 0.145]);
      for (const x of [-0.64, 0.64])
        for (const y of [-0.33, 0.33]) {
          cyl(0.043, 0.015, dark, [x, y, -0.044]);
          cyl(0.023, 0.018, black, [x, y, -0.032]);
        }
      bolt(-0.17, -0.04, 0.164);
      bolt(0.17, -0.04, 0.164);
      // Small product label, seam, underside heat sink and detachable harness silhouette.
      box(0.29, 0.12, 0.003, white, [0.44, 0.24, 0.122], 0.004);
      for (let i = 0; i < 6; i++)
        box(0.19, 0.003, 0.003, dark, [0.43, 0.275 - i * 0.012, 0.125], 0);
      for (let i = 0; i < 15; i++)
        box(0.025, 0.06, 0.12, dark, [-0.58 + i * 0.083, -0.416, -0.11], 0.002);
      for (let i = 0; i < 7; i++) {
        const x = -0.14 + i * 0.044,
          material = [red, blue, gold, black, white, green, red][i];
        tube(
          [
            [x, 0.34, 0.16],
            [x, 0.26, 0.35],
            [x - 0.05, -0.17, 0.44],
            [x + 0.18, -0.6, 0.34],
          ],
          0.009,
          material,
        );
        box(0.043, 0.065, 0.07, i % 2 ? white : red, [x + 0.18, -0.63, 0.34], 0.007);
      }
      break;
    }
  }

  root.userData = { family: info.family, fidelity: info.label };
  return {
    root,
    dispose() {
      for (const g of geometries) g.dispose();
      for (const m of materials) m.dispose();
    },
  };
}
