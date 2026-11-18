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
  const rear = -0.55,
    front = 0.52,
    wr =
      context.visual.profile === 'kukirin-sport'
        ? 0.142
        : context.visual.profile === 'nami-sport'
          ? 0.16
          : 0.15,
    ww =
      context.visual.profile === 'nami-sport'
        ? 0.105
        : context.visual.profile === 'ausom-sport'
          ? 0.095
          : 0.085,
    wy = wr;
  wheel(rear, wy, wr, ww, !!context.parts.Motors);
  wheel(front, wy, wr, ww, false);
  box(
    0.79,
    0.082,
    context.visual.profile === 'nami-sport'
      ? 0.27
      : context.visual.profile === 'dualtron-sport'
        ? 0.25
        : 0.237,
    M.paint,
    [-0.13, 0.224, 0],
  );
  box(0.76, 0.012, 0.226, M.alloy, [-0.13, 0.271, 0], context.model, 0.008);
  box(0.738, 0.006, 0.21, M.deck, [-0.13, 0.281, 0], context.model, 0.007);
  for (let x of [-0.46, 0.2])
    for (let z of [-0.093, 0.093]) {
      const b = bolt(x, 0.281, z, context.model, 0.004);
      /* deck screws face upward */ cylinder(
        0.005,
        0.005,
        0.003,
        M.silver,
        [x, 0.286, z],
        context.model,
        'y',
        6,
      );
    }
  for (let z of [-0.12, 0.12]) {
    box(0.62, 0.013, 0.003, M.accent, [-0.13, 0.232, z], context.model, 0.001);
    box(0.035, 0.024, 0.003, M.red, [-0.4, 0.246, z], context.model, 0.002);
  }
  decal(
    context.visual.name.startsWith('Custom') ? 'VOLTMODD' : context.visual.name.split(' ')[0],
    0.43,
    0.06,
    [-0.13, 0.226, 0.121],
  );
  for (const side of [-1, 1]) {
    const z = side * 0.065;
    tube(
      [
        [0.21, 0.213, z],
        [0.33, 0.16, z],
        [0.52, 0.153, z],
      ],
      0.024,
      M.frame,
      context.model,
      12,
    );
    tube(
      [
        [-0.45, 0.22, z],
        [-0.48, 0.14, z],
        [-0.55, 0.153, z],
      ],
      0.024,
      M.frame,
      context.model,
      12,
    );
    bolt(0.52, 0.153, z + side * 0.016, context.model, 0.009);
    bolt(-0.55, 0.153, z + side * 0.016, context.model, 0.009);
    box(0.042, 0.056, 0.048, M.paint, [0.31, 0.235, z], context.model, 0.008);
  }
  shock([0.26, 0.29, 0], [0.45, 0.21, 0], 0.025);
  shock([-0.43, 0.32, 0], [-0.56, 0.22, 0], 0.023);
  fender(rear, wy, 0.168, 0.094);
  fender(front, wy, 0.168, 0.094);
  box(0.1, 0.02, 0.095, M.black, [-0.49, 0.34, 0], context.model, 0.004);
  const kick = box(0.17, 0.022, 0.22, M.deck, [-0.49, 0.31, 0]);
  kick.rotation.z = -0.32;
  box(0.055, 0.016, 0.024, M.red, [-0.66, 0.26, 0], context.model, 0.005);
  // Stem base and folding mechanism: side plates, pivot, locking lever and collar.
  box(0.095, 0.12, 0.13, M.paint, [0.245, 0.32, 0], context.model, 0.015);
  cylinder(0.029, 0.029, 0.16, M.darkMetal, [0.25, 0.33, 0], context.model, 'z');
  for (let side of [-1, 1]) {
    bolt(0.25, 0.33, side * 0.085, context.model, 0.012);
    box(0.035, 0.1, 0.012, M.alloy, [0.205, 0.365, side * 0.066], context.model, 0.004);
  }
  tube(
    [
      [0.2, 0.33, 0.083],
      [0.18, 0.39, 0.083],
      [0.21, 0.44, 0.083],
    ],
    0.009,
    M.black,
  );
  bolt(0.21, 0.405, 0.086, context.model, 0.007);
  const bottom = [0.28, 0.38, 0],
    top = [0.19, 1.115, 0];
  if (context.visual.profile === 'ausom-sport') {
    panel(
      [
        [0.255, 0.38],
        [0.31, 0.39],
        [0.22, 1.13],
        [0.16, 1.13],
      ],
      0.048,
      M.paint,
    );
  } else rod(bottom, top, 0.029, M.paint);
  rod([0.19, 1.05, 0], [0.18, 1.18, 0], 0.021, M.alloy);
  rod([0.19, 1.1, 0], [0.18, 1.145, 0], 0.033, M.black);
  for (let side of [-1, 1])
    rod([0.264, 0.41, side * 0.018], [0.194, 1.09, side * 0.018], 0.0035, M.accent);
  decal('VM', 0.037, 0.12, [0.231, 0.76, 0.03], [0, 0, 0.12]);
  cylinder(0.035, 0.035, 0.018, M.black, [0.18, 1.15, 0]);
  tube(
    [
      [0.18, 1.17, -0.31],
      [0.18, 1.18, -0.16],
      [0.18, 1.155, 0],
      [0.18, 1.18, 0.16],
      [0.18, 1.17, 0.31],
    ],
    0.012,
    M.paint,
  );
  grips(0.18, 1.17, 0.31);
  // Dual LED headlamp, mounting bracket and ribbed back housing.
  rod([0.23, 0.5, 0], [0.34, 0.51, 0], 0.012, M.black);
  for (let z of [-0.031, 0.031]) {
    const lamp = cylinder(0.027, 0.025, 0.035, M.black, [0.34, 0.51, z], context.model, 'x', 40);
    const lens = cylinder(0.021, 0.021, 0.003, M.lens, [0.36, 0.51, z], context.model, 'x', 40);
    for (let j = 0; j < 4; j++)
      torus(0.026, 0.0015, M.darkMetal, [0.334 - j * 0.006, 0.51, z]).rotation.y = Math.PI / 2;
  }
  tube(
    [
      [0.17, 1.12, -0.08],
      [0.15, 1.01, -0.08],
      [0.22, 0.72, -0.045],
      [0.29, 0.38, -0.035],
      [0.48, 0.21, -0.042],
    ],
    0.0033,
    M.cable,
  );
  tube(
    [
      [0.17, 1.13, 0.08],
      [0.13, 0.98, 0.1],
      [0.22, 0.63, 0.047],
      [0.1, 0.3, 0.04],
      [-0.31, 0.29, 0.055],
      [-0.53, 0.24, 0.065],
    ],
    0.0032,
    M.cable,
  );
  rod([-0.3, 0.19, -0.12], [-0.35, 0.035, -0.22], 0.008, M.darkMetal);
  box(0.042, 0.009, 0.026, M.black, [-0.35, 0.031, -0.22]);
  context.batteryGroup = group('Battery — exposed in exploded view');
  context.batteryGroup.position.set(-0.14, 0.225, 0);
  box(0.49, 0.055, 0.17, M.black, [0, 0, 0], context.batteryGroup, 0.005);
  for (let i = 0; i < 4; i++)
    box(0.011, 0.058, 0.174, M.darkMetal, [-0.18 + i * 0.12, 0, 0], context.batteryGroup, 0.001);
  decal('Li-ion', 0.13, 0.04, [0, 0.03, 0], [-Math.PI / 2, 0, 0], context.batteryGroup);
  context.controllerGroup = group('Controller — exposed in exploded view');
  context.controllerGroup.position.set(0.18, 0.224, 0);
  box(0.13, 0.05, 0.15, M.alloy, [0, 0, 0], context.controllerGroup, 0.003);
  for (let i = 0; i < 10; i++)
    box(
      0.115,
      0.006,
      0.004,
      M.darkMetal,
      [0, 0.029, -0.06 + i * 0.013],
      context.controllerGroup,
      0.001,
    );
  tube(
    [
      [0.06, 0, 0.02],
      [0.11, -0.02, 0.03],
      [0.15, -0.02, 0.05],
    ],
    0.004,
    M.red,
    context.controllerGroup,
  );
}
