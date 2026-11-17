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
    front = 0.55,
    r = 0.163,
    wy = r,
    body = M.frame,
    orange = M.accent;
  wheel(rear, wy, r, 0.102, true);
  wheel(front, wy, r, 0.102, false);
  box(0.72, 0.105, 0.235, body, [-0.12, 0.245, 0], context.model, 0.012);
  box(0.705, 0.013, 0.226, M.black, [-0.12, 0.302, 0], context.model, 0.006);
  box(0.68, 0.004, 0.212, M.deck, [-0.12, 0.311, 0], context.model, 0.004);
  // The G4 has a substantial angular headstock and flat-sided stem.
  panel(
    [
      [0.19, 0.2],
      [0.31, 0.205],
      [0.38, 0.435],
      [0.3, 0.515],
      [0.25, 0.5],
    ],
    0.15,
    body,
  );
  panel(
    [
      [0.275, 0.485],
      [0.344, 0.477],
      [0.174, 1.226],
      [0.108, 1.238],
    ],
    0.057,
    M.black,
  );
  for (const side of [-1, 1]) {
    const z = side * 0.081;
    panel(
      [
        [0.27, 0.253],
        [0.33, 0.235],
        [0.575, 0.177],
        [0.586, 0.145],
        [0.525, 0.131],
        [0.3, 0.188],
      ],
      0.019,
      body,
      z,
    );
    panel(
      [
        [-0.42, 0.259],
        [-0.39, 0.224],
        [-0.555, 0.147],
        [-0.6, 0.164],
        [-0.57, 0.192],
      ],
      0.022,
      body,
      z,
    );
    bolt(front, wy, z + side * 0.015, context.model, 0.012);
    bolt(rear, wy, z + side * 0.015, context.model, 0.012);
    bolt(0.295, 0.224, z + side * 0.015, context.model, 0.008);
    for (let i = 0; i < 4; i++)
      for (let j = 0; j < 2; j++)
        box(
          0.007,
          0.007,
          0.002,
          orange,
          [0.35 + i * 0.012, 0.234 + j * 0.012, z + side * 0.014],
          context.model,
          0,
        );
    for (let i = 0; i < 4; i++)
      box(
        0.006,
        0.006,
        0.002,
        orange,
        [-0.36 + i * 0.011, 0.257, z + side * 0.014],
        context.model,
        0,
      );
  }
  shock([0.345, 0.343, 0], [0.45, 0.224, 0], 0.023);
  shock([-0.36, 0.32, 0], [-0.49, 0.219, 0], 0.025);
  fender(front, wy, 0.183, 0.107);
  fender(rear, wy, 0.187, 0.11);
  const foot = box(0.19, 0.022, 0.215, M.black, [-0.43, 0.395, 0], context.model, 0.006);
  foot.rotation.z = -0.22;
  for (let x of [-0.47, -0.36])
    for (let z of [-0.085, 0.085])
      cylinder(0.004, 0.004, 0.003, M.silver, [x, 0.411, z], context.model, 'y', 6);
  rod([-0.46, 0.375, -0.067], [-0.43, 0.3, -0.067], 0.012, M.darkMetal);
  rod([-0.46, 0.375, 0.067], [-0.43, 0.3, 0.067], 0.012, M.darkMetal);
  box(0.055, 0.018, 0.04, M.red, [-0.63, 0.294, 0], context.model, 0.004);
  box(0.038, 0.029, 0.11, M.black, [-0.61, 0.27, 0], context.model, 0.004);
  // Folding hinge and its multi-bolt locking plates.
  box(0.078, 0.095, 0.075, body, [0.286, 0.51, 0], context.model, 0.006);
  cylinder(0.022, 0.022, 0.1, M.darkMetal, [0.302, 0.49, 0], context.model, 'z');
  for (const side of [-1, 1]) {
    for (let y of [0.475, 0.515, 0.55])
      bolt(0.3 - (y - 0.475) * 0.28, y, side * 0.047, context.model, 0.005);
    tube(
      [
        [0.28, 0.54, side * 0.048],
        [0.26, 0.6, side * 0.048],
        [0.28, 0.625, side * 0.048],
      ],
      0.006,
      M.black,
    );
  }
  // Console/headlight pod and swept bars, rather than generic low-mounted lamps.
  rod([0.14, 1.2, 0], [0.12, 1.26, 0], 0.017, M.black);
  tube(
    [
      [0.12, 1.25, -0.33],
      [0.13, 1.265, -0.19],
      [0.12, 1.245, 0],
      [0.13, 1.265, 0.19],
      [0.12, 1.25, 0.33],
    ],
    0.013,
    M.paint,
  );
  grips(0.12, 1.25, 0.33);
  panel(
    [
      [0.093, 1.253],
      [0.102, 1.303],
      [0.142, 1.323],
      [0.197, 1.283],
      [0.185, 1.237],
    ],
    0.115,
    M.black,
  );
  box(0.004, 0.022, 0.112, M.lens, [0.195, 1.271, 0], context.model, 0.002);
  for (let z of [-0.042, -0.014, 0.014, 0.042])
    box(0.005, 0.02, 0.002, M.darkMetal, [0.199, 1.271, z], context.model, 0.0005);
  tube(
    [
      [0.11, 1.24, -0.15],
      [0.045, 1.16, -0.12],
      [0.12, 1.04, -0.047],
      [0.24, 0.65, -0.042],
      [0.31, 0.48, -0.04],
    ],
    0.003,
    M.cable,
  );
  tube(
    [
      [0.12, 1.245, 0.16],
      [0.06, 1.14, 0.11],
      [0.15, 0.99, 0.046],
      [0.28, 0.52, 0.042],
    ],
    0.003,
    M.cable,
  );
  tube(
    [
      [0.15, 1.23, -0.04],
      [0.22, 1.16, -0.04],
      [0.19, 1.08, -0.04],
    ],
    0.004,
    M.cable,
  );
  decal('KuKirin G4', 0.18, 0.035, [0.224, 0.836, 0.032], [0, 0, 1.35], context.model, '#eb8c22');
  decal('KuKirin', 0.18, 0.032, [-0.16, 0.251, 0.121], [0, 0, 0], context.model, '#e5871c');
  for (let i = 0; i < 5; i++)
    box(
      0.008,
      0.008,
      0.002,
      orange,
      [-0.3 + i * 0.012, 0.245 + (i % 2) * 0.012, 0.121],
      context.model,
      0,
    );
  rod([-0.3, 0.194, -0.12], [-0.37, 0.035, -0.23], 0.008, M.darkMetal);
  box(0.045, 0.008, 0.025, M.black, [-0.37, 0.03, -0.23]);
  context.batteryGroup = group('G4 battery envelope — approximate');
  context.batteryGroup.position.set(-0.12, 0.245, 0);
  box(0.48, 0.065, 0.18, M.black, [0, 0, 0], context.batteryGroup, 0.005);
  context.controllerGroup = group('G4 controller envelope — approximate');
  context.controllerGroup.position.set(0.16, 0.245, 0);
  box(0.14, 0.065, 0.17, M.alloy, [0, 0, 0], context.controllerGroup, 0.004);
  for (let i = 0; i < 10; i++)
    box(
      0.11,
      0.005,
      0.004,
      M.darkMetal,
      [0, 0.035, -0.065 + i * 0.014],
      context.controllerGroup,
      0.001,
    );
}
