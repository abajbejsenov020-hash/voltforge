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
  const rear = -0.66,
    front = 0.67,
    r = context.visual.profile === 'folding-fat-bike' ? 0.265 : 0.337,
    wy = r;
  wheel(
    rear,
    wy,
    r,
    context.visual.profile === 'folding-fat-bike' ? 0.09 : 0.049,
    !!context.parts.Motors && !/Mid-drive|Front Hub/.test(context.parts.Motors.name),
  );
  wheel(
    front,
    wy,
    r,
    context.visual.profile === 'folding-fat-bike' ? 0.09 : 0.049,
    !!context.parts.Motors && /Front Hub/.test(context.parts.Motors.name),
  );
  const bb = [-0.19, 0.33, 0],
    seat = [-0.37, context.visual.profile === 'folding-fat-bike' ? 0.73 : 0.88, 0],
    head = [0.39, 0.95, 0];
  // Hydroformed frame: a curved down tube, arcing top tube, tapered stays.
  tube([bb, [0.02, 0.48, 0], [0.3, 0.68, 0], [0.4, 0.83, 0]], 0.037, M.frame);
  if (context.visual.profile === 'step-through-bike')
    tube([seat, [-0.24, 0.48, 0], [0.1, 0.43, 0], head], 0.026, M.paint);
  else if (context.visual.profile === 'folding-fat-bike') {
    panel(
      [
        [-0.4, 0.74],
        [0.4, 0.96],
        [0.4, 0.86],
        [-0.4, 0.65],
      ],
      0.068,
      M.frame,
    );
    shock([-0.4, 0.64, 0], [-0.56, 0.48, 0], 0.017, context.model, M.red);
  } else
    tube(
      [seat, [-0.1, 0.91, 0], [0.17, 0.92, 0], head],
      context.visual.profile === 'electric-moto' ? 0.036 : 0.024,
      M.paint,
    );
  if (context.visual.profile === 'folding-fat-bike') {
    box(0.07, 0.09, 0.08, M.darkMetal, [-0.02, 0.8, 0], context.model, 0.006);
    tube(
      [
        [0.01, 0.82, 0.046],
        [0.04, 0.8, 0.046],
        [0.04, 0.77, 0.046],
      ],
      0.005,
      M.alloy,
    );
  }
  if (context.visual.profile === 'step-through-bike') {
    box(0.38, 0.015, 0.135, M.black, [-0.61, 0.735, 0], context.model, 0.004);
    for (const z of [-0.055, 0.055]) {
      rod([-0.77, 0.73, z], [-0.66, 0.34, z], 0.006, M.darkMetal);
      rod([-0.44, 0.73, z], [-0.66, 0.34, z], 0.006, M.darkMetal);
    }
  }
  if (context.visual.profile === 'electric-moto') {
    panel(
      [
        [-0.3, 0.83],
        [0.18, 0.84],
        [0.23, 0.52],
        [-0.16, 0.36],
        [-0.31, 0.5],
      ],
      0.15,
      M.black,
    );
    box(0.4, 0.07, 0.17, M.rubber, [-0.42, 0.99, 0], context.model, 0.018);
  }
  rod(bb, [-0.39, 0.95, 0], 0.026, M.frame);
  rod([0.39, 0.8, 0], [0.42, 0.98, 0], 0.028, M.paint);
  for (let side of [-1, 1]) {
    const z = side * 0.037;
    tube(
      [
        [rear, wy, z],
        [-0.51, 0.58, z],
        [-0.37, 0.88, z * 0.4],
      ],
      0.011,
      M.paint,
    );
    tube(
      [
        [rear, wy, z],
        [-0.48, 0.31, side * 0.055],
        [-0.19, 0.33, z],
      ],
      0.014,
      M.frame,
    );
    bolt(rear, wy, z * 1.5, context.model, 0.006);
  }
  decal('V O L T F O R G E', 0.35, 0.053, [0.078, 0.588, 0.038], [0, 0, 0.66]);
  // Suspension fork: crown, polished stanchions, dust seals, lowers and bridge.
  for (let side of [-1, 1]) {
    const z = side * 0.05;
    rod([0.42, 0.91, z], [0.51, 0.64, z], 0.017, M.silver);
    rod([0.51, 0.64, z], [front, wy, z], 0.023, M.black);
    rod([0.505, 0.66, z], [0.52, 0.615, z], 0.024, M.rubber);
    cylinder(0.02, 0.02, 0.015, M.black, [0.42, 0.93, z]);
    bolt(front, wy, z * 1.3, context.model, 0.007);
  }
  tube(
    [
      [0.53, 0.62, -0.055],
      [0.53, 0.67, -0.045],
      [0.53, 0.69, 0],
      [0.53, 0.67, 0.045],
      [0.53, 0.62, 0.055],
    ],
    0.013,
    M.black,
  );
  box(0.086, 0.025, 0.14, M.paint, [0.43, 0.9, 0], context.model, 0.004);
  rod([0.42, 0.97, 0], [0.38, 1.04, 0], 0.018, M.darkMetal);
  box(0.093, 0.025, 0.041, M.black, [0.36, 1.04, 0], context.model, 0.004);
  tube(
    [
      [0.35, 1.05, -0.34],
      [0.32, 1.08, -0.2],
      [0.34, 1.05, 0],
      [0.32, 1.08, 0.2],
      [0.35, 1.05, 0.34],
    ],
    0.0125,
    M.paint,
  );
  grips(0.35, 1.05, 0.34);
  // Sculpted saddle with raised rear shoulders, narrow nose and curved support rails.
  rod(
    [-0.38, context.visual.profile === 'folding-fat-bike' ? 0.73 : 0.9, 0],
    [-0.415, 1.08, 0],
    0.015,
    M.darkMetal,
  );
  cylinder(0.025, 0.025, 0.024, M.black, [-0.395, 0.973, 0]);
  for (let side of [-1, 1])
    tube(
      [
        [-0.49, 1.055, side * 0.035],
        [-0.46, 1.04, side * 0.035],
        [-0.39, 1.048, side * 0.028],
        [-0.31, 1.08, side * 0.018],
      ],
      0.003,
      M.silver,
    );
  const saddleShape = new T.Shape();
  saddleShape.moveTo(-0.13, -0.065);
  saddleShape.bezierCurveTo(-0.17, -0.04, -0.15, 0.06, -0.11, 0.073);
  saddleShape.bezierCurveTo(-0.07, 0.08, -0.02, 0.04, 0.025, 0.024);
  saddleShape.bezierCurveTo(0.1, 0.023, 0.13, 0.018, 0.13, 0);
  saddleShape.bezierCurveTo(0.13, -0.018, 0.08, -0.026, 0.025, -0.026);
  saddleShape.bezierCurveTo(-0.02, -0.035, -0.07, -0.08, -0.13, -0.065);
  const saddle = mesh(
    new T.ExtrudeGeometry(saddleShape, {
      depth: 0.026,
      bevelEnabled: true,
      bevelSegments: 5,
      bevelSize: 0.009,
      bevelThickness: 0.008,
      curveSegments: 20,
    }),
    M.rubber,
  );
  saddle.rotation.x = -Math.PI / 2;
  saddle.position.set(-0.42, 1.085, 0);
  tube(
    [
      [-0.55, 1.12, -0.048],
      [-0.48, 1.125, -0.06],
      [-0.4, 1.12, -0.035],
      [-0.32, 1.12, -0.018],
    ],
    0.001,
    M.darkMetal,
  );
  // Crank, chainring teeth, cassette cluster, chain and rear derailleur.
  cylinder(0.037, 0.037, 0.11, M.black, bb, context.model, 'z');
  if (context.parts.Motors && /Mid-drive/.test(context.parts.Motors.name)) {
    cylinder(0.066, 0.061, 0.12, M.paint, [-0.14, 0.31, 0], context.model, 'z', 40);
    for (let i = 0; i < 9; i++)
      torus(0.061, 0.0025, M.darkMetal, [-0.14, 0.31, -0.047 + i * 0.012]);
  }
  const chainZ = 0.085,
    crankR = 0.084;
  torus(crankR, 0.004, M.darkMetal, [bb[0], bb[1], chainZ]);
  for (let i = 0; i < 42; i++) {
    let a = (i / 42) * Math.PI * 2;
    const tooth = box(
      0.006,
      0.009,
      0.003,
      M.alloy,
      [bb[0] + Math.cos(a) * crankR, bb[1] + Math.sin(a) * crankR, chainZ],
      context.model,
      0,
    );
    tooth.rotation.z = a - Math.PI / 2;
  }
  for (let i = 0; i < 5; i++) {
    let a = (i / 5) * Math.PI * 2;
    rod(
      [bb[0], bb[1], chainZ],
      [bb[0] + Math.cos(a) * crankR, bb[1] + Math.sin(a) * crankR, chainZ],
      0.005,
      M.darkMetal,
    );
  }
  for (let i = 0; i < 7; i++)
    cylinder(
      0.058 - i * 0.004,
      0.058 - i * 0.004,
      0.003,
      M.darkMetal,
      [rear, wy, 0.052 + i * 0.004],
      context.model,
      'z',
      32,
    );
  tube(
    [
      [bb[0], bb[1] + crankR, chainZ],
      [-0.43, 0.405, chainZ],
      [rear, wy + 0.059, chainZ],
    ],
    0.003,
    M.darkMetal,
  );
  tube(
    [
      [rear, wy - 0.05, chainZ],
      [-0.49, 0.25, chainZ],
      [bb[0], bb[1] - crankR, chainZ],
    ],
    0.003,
    M.darkMetal,
  );
  tube(
    [
      [rear, wy, 0.095],
      [-0.7, 0.25, 0.095],
      [-0.62, 0.19, 0.095],
    ],
    0.008,
    M.black,
  );
  torus(0.019, 0.004, M.darkMetal, [-0.62, 0.19, 0.095]);
  for (let side of [-1, 1]) {
    const angle = side === 1 ? -0.75 : Math.PI - 0.75,
      end = [bb[0] + Math.cos(angle) * 0.16, bb[1] + Math.sin(angle) * 0.16, side * 0.105];
    rod([bb[0], bb[1], side * 0.105], end, 0.009, M.alloy);
    const pedal = box(
      0.087,
      0.016,
      0.075,
      M.black,
      [end[0], end[1], end[2] + side * 0.025],
      context.model,
      0.003,
    );
    for (let i = 0; i < 5; i++)
      box(
        0.004,
        0.002,
        0.06,
        M.alloy,
        [end[0] - 0.03 + i * 0.014, end[1] + 0.009, end[2] + side * 0.025],
        context.model,
        0.0005,
      );
  }
  const chainCurve = new T.CatmullRomCurve3(
    [
      new T.Vector3(bb[0], bb[1] + crankR, chainZ),
      new T.Vector3(rear, wy + 0.059, chainZ),
      new T.Vector3(rear - 0.055, wy, chainZ),
      new T.Vector3(rear, wy - 0.05, chainZ),
      new T.Vector3(bb[0], bb[1] - crankR, chainZ),
      new T.Vector3(bb[0] + crankR, bb[1], chainZ),
    ],
    true,
    'centripetal',
  );
  const links = new T.InstancedMesh(new T.TorusGeometry(0.0028, 0.0008, 5, 10), M.alloy, 130),
    linkDummy = new T.Object3D();
  for (let i = 0; i < 130; i++) {
    const t = i / 130,
      pos = chainCurve.getPointAt(t),
      tangent = chainCurve.getTangentAt(t);
    linkDummy.position.copy(pos);
    linkDummy.rotation.set(0, 0, Math.atan2(tangent.y, tangent.x));
    linkDummy.scale.set(1.65, 1, 1);
    linkDummy.updateMatrix();
    links.setMatrixAt(i, linkDummy.matrix);
  }
  context.model.add(links);
  // Hydraulic hoses follow frame and fork; bottle bosses, reflectors and stand.
  tube(
    [
      [0.35, 1.035, -0.15],
      [0.25, 0.95, -0.13],
      [0.4, 0.81, -0.07],
      [0.54, 0.6, -0.055],
      [0.72, 0.39, -0.055],
    ],
    0.0025,
    M.cable,
  );
  tube(
    [
      [0.34, 1.04, 0.14],
      [0.2, 0.94, 0.13],
      [-0.02, 0.88, 0.04],
      [-0.36, 0.8, 0.035],
      [-0.57, 0.45, 0.05],
    ],
    0.0025,
    M.cable,
  );
  for (let x of [-0.08, 0.02]) bolt(x, 0.6 + x * 0.7, 0.042, context.model, 0.003);
  for (let x of [-0.66, 0.67])
    box(0.027, 0.08, 0.006, M.label, [x + 0.15, 0.34, 0.025], context.model, 0.003);
  rod([-0.35, 0.3, -0.04], [-0.43, 0.04, -0.13], 0.008, M.black);
  context.batteryGroup = group('Integrated down-tube battery');
  context.batteryGroup.position.set(0.065, 0.579, 0);
  const battery = box(0.41, 0.065, 0.079, M.black, [0, 0, 0], context.batteryGroup, 0.012);
  battery.rotation.z = 0.64;
  box(0.025, 0.025, 0.08, M.darkMetal, [-0.155, -0.11, 0], context.batteryGroup, 0.005);
  context.controllerGroup = group('Controller integrated above bottom bracket');
  context.controllerGroup.position.set(-0.21, 0.403, 0);
  box(0.085, 0.06, 0.075, M.black, [0, 0, 0], context.controllerGroup, 0.005);
  for (let i = 0; i < 7; i++)
    box(
      0.067,
      0.004,
      0.003,
      M.darkMetal,
      [0, 0.033, -0.027 + i * 0.009],
      context.controllerGroup,
      0.001,
    );
}
