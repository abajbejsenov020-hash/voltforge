export function build(context) {
  const {
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
  } = context;

  const rear = -0.69,
    front = 0.72,
    wr = 0.318,
    wy = wr;
  const gold = M.lbxGold || mat(0xb9973c, 0.88, 0.25),
    graphic = M.lbxGraphic || mat(0xd0dc38, 0.12, 0.56),
    body = M.lbxBody || mat(0x25282a, 0.48, 0.39);
  // Keep materials in the shared set so rebuilding does not dispose them per mesh.
  M.lbxGold = gold;
  M.lbxGraphic = graphic;
  M.lbxBody = body;
  wheel(rear, wy, wr, 0.083, false);
  wheel(front, wy, wr, 0.073, false);
  for (const [x, width] of [
    [rear, 0.083],
    [front, 0.073],
  ]) {
    const knobs = group('LBX staggered off-road tread blocks');
    for (let i = 0; i < 40; i++)
      for (const side of [-1, 0, 1]) {
        const a = (i / 40) * Math.PI * 2 + (side === 0 ? 0.035 : 0);
        const block = box(
          0.025,
          0.013,
          0.021,
          M.tread,
          [x + Math.cos(a) * wr, wy + Math.sin(a) * wr, side * width * 0.31],
          knobs,
          0.002,
        );
        block.rotation.z = a - Math.PI / 2;
      }
  }
  const shell = (points, depth, material, z = 0, parent = context.model) => {
    const shape = new T.Shape();
    shape.moveTo(...points[0]);
    for (const point of points.slice(1)) shape.lineTo(...point);
    shape.closePath();
    const geo = new T.ExtrudeGeometry(shape, {
      depth,
      bevelEnabled: true,
      bevelSize: 0.006,
      bevelThickness: 0.005,
      bevelSegments: 3,
      curveSegments: 12,
    });
    geo.translate(0, 0, -depth / 2);
    const m = mesh(geo, material, parent);
    m.position.z = z;
    return m;
  };
  // Cast frame spars surround an open rear triangle and a tall central battery.
  for (const side of [-1, 1]) {
    const z = side * 0.088;
    shell(
      [
        [0.34, 0.91],
        [0.22, 0.84],
        [0.04, 0.43],
        [-0.12, 0.34],
        [-0.24, 0.37],
        [-0.12, 0.45],
        [0.1, 0.88],
        [0.29, 0.97],
      ],
      0.028,
      M.frame,
      z,
    );
    shell(
      [
        [-0.13, 0.38],
        [-0.28, 0.43],
        [-0.43, 0.91],
        [-0.37, 0.96],
        [-0.2, 0.85],
        [-0.15, 0.49],
      ],
      0.026,
      M.frame,
      z,
    );
    tube(
      [
        [0.29, 0.94, z],
        [-0.02, 1.005, z * 0.8],
        [-0.34, 0.985, z],
        [-0.41, 0.91, z],
      ],
      0.025,
      body,
    );
    // Box-section swingarm, axle adjusters, and angular seat supports.
    shell(
      [
        [-0.19, 0.43],
        [-0.4, 0.4],
        [-0.73, 0.34],
        [-0.74, 0.29],
        [-0.53, 0.31],
        [-0.18, 0.36],
      ],
      0.026,
      body,
      side * 0.067,
    );
    rod([-0.19, 0.41, side * 0.067], [rear, 0.32, side * 0.067], 0.016, M.darkMetal);
    rod([-0.16, 0.48, z], [-0.49, 0.89, z * 0.8], 0.016, M.frame);
    rod([-0.49, 0.89, z * 0.8], [-0.7, 1.035, side * 0.06], 0.014, M.frame);
    for (const [x, y] of [
      [-0.19, 0.405],
      [-0.29, 0.46],
      [-0.39, 0.91],
      [0.28, 0.93],
      [rear, 0.32],
    ])
      bolt(x, y, side * 0.112, context.model, 0.007);
    box(0.044, 0.019, 0.008, M.alloy, [rear + 0.025, wy, side * 0.09], context.model, 0.003);
    // Asymmetric yellow-green wrap panels mimic the supplied style without using a flat photo as geometry.
    shell(
      [
        [-0.33, 0.84],
        [-0.22, 0.81],
        [-0.17, 0.5],
        [-0.25, 0.48],
      ],
      0.003,
      graphic,
      side * 0.107,
    );
    shell(
      [
        [0.08, 0.82],
        [0.14, 0.84],
        [0.01, 0.53],
        [-0.04, 0.48],
      ],
      0.003,
      graphic,
      side * 0.108,
    );
    shell(
      [
        [-0.32, 0.76],
        [-0.16, 0.7],
        [-0.15, 0.67],
        [-0.31, 0.71],
      ],
      0.004,
      M.black,
      side * 0.111,
    );
  }
  // Battery and controller lift separately in the inspection view.
  context.batteryGroup = group('LBX removable battery — visual envelope');
  context.batteryGroup.position.set(-0.1, 0.7, 0);
  box(0.245, 0.37, 0.145, M.black, [0, 0, 0], context.batteryGroup, 0.018);
  box(0.26, 0.026, 0.155, body, [0, 0.19, 0], context.batteryGroup, 0.008);
  box(0.12, 0.018, 0.06, M.black, [0, 0.212, 0], context.batteryGroup, 0.006);
  for (const z of [-0.077, 0.077])
    for (let i = 0; i < 3; i++)
      box(0.16, 0.004, 0.003, M.darkMetal, [0, -0.11 + i * 0.07, z], context.batteryGroup, 0.001);
  context.controllerGroup = group('LBX finned controller — visual envelope');
  context.controllerGroup.position.set(0.18, 0.665, 0);
  const control = box(0.082, 0.265, 0.145, M.black, [0, 0, 0], context.controllerGroup, 0.008);
  control.rotation.z = 0.19;
  for (let i = 0; i < 12; i++) {
    const fin = box(
      0.01,
      0.2,
      0.003,
      M.darkMetal,
      [0.045, 0, -0.061 + i * 0.011],
      context.controllerGroup,
      0.001,
    );
    fin.rotation.z = 0.19;
  }
  // Compact mid-drive, primary drive cover, skid plate and footpegs. No bicycle crank or pedals.
  const drive = group('LBX compact mid-drive and primary belt cover');
  cylinder(0.096, 0.096, 0.17, M.black, [-0.18, 0.383, 0], drive, 'z', 48);
  for (const side of [-1, 1]) {
    cylinder(0.071, 0.071, 0.008, body, [-0.18, 0.383, side * 0.091], drive, 'z', 48);
    torus(0.057, 0.005, M.darkMetal, [-0.18, 0.383, side * 0.099], drive);
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * Math.PI * 2;
      bolt(-0.18 + Math.cos(a) * 0.08, 0.383 + Math.sin(a) * 0.08, side * 0.101, drive, 0.0035);
    }
    rod([-0.28, 0.39, side * 0.1], [-0.31, 0.37, side * 0.17], 0.011, M.alloy);
    const peg = box(0.07, 0.014, 0.063, M.darkMetal, [-0.31, 0.37, side * 0.18], drive, 0.003);
    for (let i = 0; i < 5; i++)
      cylinder(0.002, 0.002, 0.004, M.silver, [-0.337 + i * 0.014, 0.38, side * 0.201], drive);
  }
  shell(
    [
      [-0.29, 0.31],
      [-0.17, 0.276],
      [0.0, 0.335],
      [0.045, 0.39],
      [-0.07, 0.37],
    ],
    0.19,
    body,
  );
  // Rear sprocket, chain runs and a small chain guide on the drive side.
  const driveZ = -0.108;
  cylinder(0.083, 0.083, 0.004, M.darkMetal, [rear, wy, driveZ], context.model, 'z', 48);
  torus(0.077, 0.003, M.alloy, [rear, wy, driveZ - 0.005]);
  for (let i = 0; i < 44; i++) {
    const a = (i / 44) * Math.PI * 2;
    box(
      0.007,
      0.008,
      0.006,
      M.alloy,
      [rear + Math.cos(a) * 0.084, wy + Math.sin(a) * 0.084, driveZ],
      context.model,
      0.001,
    );
  }
  tube(
    [
      [rear, 0.402, driveZ],
      [-0.42, 0.438, driveZ],
      [-0.23, 0.451, driveZ],
    ],
    0.0045,
    M.darkMetal,
  );
  tube(
    [
      [rear, 0.236, driveZ],
      [-0.42, 0.303, driveZ],
      [-0.23, 0.332, driveZ],
    ],
    0.0045,
    M.darkMetal,
  );
  for (let i = 0; i < 38; i++) {
    const t = i / 37;
    cylinder(
      0.0022,
      0.0022,
      0.008,
      M.alloy,
      [rear + t * 0.46, 0.402 + t * 0.049, driveZ],
      context.model,
      'z',
      8,
    );
  }
  box(0.063, 0.037, 0.032, M.black, [-0.52, 0.287, driveZ], context.model, 0.004);
  shock([-0.44, 0.84, 0], [-0.23, 0.48, 0], 0.026, context.model, M.black);
  rod([-0.23, 0.48, 0], [-0.4, 0.4, 0], 0.013, M.darkMetal);
  cylinder(0.024, 0.024, 0.09, gold, [-0.4, 0.79, 0.049], context.model, 'z');
  // Sculpted long moto saddle with rising tail, stitched seam and rear fender.
  const saddle = new T.Shape();
  saddle.moveTo(-0.85, 1.06);
  saddle.bezierCurveTo(-0.68, 1.09, -0.55, 1.08, -0.42, 1.035);
  saddle.bezierCurveTo(-0.29, 1.004, -0.2, 1.015, -0.12, 1.018);
  saddle.lineTo(-0.14, 0.978);
  saddle.bezierCurveTo(-0.4, 0.958, -0.63, 0.996, -0.83, 1.017);
  saddle.closePath();
  const saddleGeo = new T.ExtrudeGeometry(saddle, {
    depth: 0.165,
    bevelEnabled: true,
    bevelSize: 0.013,
    bevelThickness: 0.01,
    bevelSegments: 5,
    curveSegments: 24,
  });
  saddleGeo.translate(0, 0, -0.0825);
  mesh(saddleGeo, M.rubber).name = 'LBX long sculpted moto seat';
  for (const side of [-1, 1])
    tube(
      [
        [-0.81, 1.055, side * 0.087],
        [-0.62, 1.059, side * 0.091],
        [-0.42, 1.016, side * 0.091],
        [-0.17, 1.009, side * 0.083],
      ],
      0.0015,
      M.grip,
    );
  shell(
    [
      [-0.79, 1.028],
      [-0.99, 1.087],
      [-1.005, 1.072],
      [-0.86, 1.0],
    ],
    0.105,
    M.black,
  );
  box(0.018, 0.022, 0.043, M.red, [-0.76, 0.971, 0], context.model, 0.003);
  // Long inverted fork with gold uppers, silver collars, triple clamps and guards.
  for (const side of [-1, 1]) {
    const z = side * 0.068;
    rod([front, wy, z], [0.36, 1.075, z], 0.021, gold);
    rod([front, wy, z], [0.52, 0.745, z], 0.025, M.black);
    rod([0.39, 0.985, z], [0.415, 0.928, z], 0.029, M.alloy);
    rod([0.365, 1.045, z], [0.382, 1.01, z], 0.029, M.black);
    rod([0.7, 0.36, z * 1.2], [0.56, 0.66, z * 1.2], 0.028, body);
    bolt(front, wy, z * 1.4, context.model, 0.009);
    tube(
      [
        [0.34, 1.08, z],
        [0.41, 0.92, z * 1.7],
        [0.58, 0.68, z * 1.4],
        [0.69, 0.38, z * 1.5],
      ],
      0.003,
      M.cable,
    );
  }
  for (const y of [0.95, 1.065]) {
    const clamp = box(
      0.065,
      0.022,
      0.2,
      M.black,
      [0.4 - (y - 0.95) * 0.45, y, 0],
      context.model,
      0.005,
    );
    clamp.rotation.z = 0.4;
  }
  rod([0.37, 1.04, 0], [0.34, 1.16, 0], 0.017, M.darkMetal);
  tube(
    [
      [0.34, 1.16, -0.36],
      [0.3, 1.18, -0.2],
      [0.33, 1.14, 0],
      [0.3, 1.18, 0.2],
      [0.34, 1.16, 0.36],
    ],
    0.012,
    M.black,
  );
  grips(0.34, 1.16, 0.36);
  for (const side of [-1, 1])
    box(0.025, 0.019, 0.04, M.black, [0.31, 1.181, side * 0.22], context.model, 0.004);
  // High front mudguard, number plate and round projector headlight.
  shell(
    [
      [0.43, 0.815],
      [0.6, 0.845],
      [0.96, 0.842],
      [1.02, 0.824],
      [0.75, 0.818],
      [0.52, 0.788],
    ],
    0.11,
    M.black,
  );
  const plate = box(0.03, 0.18, 0.12, body, [0.39, 1.002, 0], context.model, 0.008);
  plate.rotation.z = 0.15;
  cylinder(0.041, 0.041, 0.04, M.black, [0.455, 1.103, 0], context.model, 'x', 48);
  cylinder(0.031, 0.031, 0.003, M.lens, [0.477, 1.103, 0], context.model, 'x', 48);
  tube(
    [
      [0.3, 1.16, -0.2],
      [0.4, 1.19, -0.16],
      [0.43, 1.03, -0.11],
      [0.29, 0.86, -0.1],
    ],
    0.004,
    M.cable,
  );
  shell(
    [
      [-0.57, 0.61],
      [-0.67, 0.7],
      [-0.73, 0.7],
      [-0.66, 0.54],
    ],
    0.085,
    M.black,
  );
  rod([-0.28, 0.35, -0.08], [-0.45, 0.04, -0.22], 0.009, M.black);
  box(0.055, 0.008, 0.029, M.darkMetal, [-0.45, 0.035, -0.22]);
}
