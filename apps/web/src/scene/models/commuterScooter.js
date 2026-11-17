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
  const r = 0.134,
    wy = r,
    rear = -0.48,
    front = 0.48;
  wheel(rear, wy, r, 0.061, true);
  wheel(front, wy, r, 0.061, false);
  box(0.69, 0.055, 0.155, M.frame, [-0.08, 0.19, 0], context.model, 0.018);
  box(0.67, 0.007, 0.15, M.deck, [-0.08, 0.222, 0], context.model, 0.008);
  tube(
    [
      [0.22, 0.185, 0],
      [0.34, 0.23, 0],
      [0.39, 0.38, 0],
    ],
    0.031,
    M.frame,
  );
  rod([0.38, 0.31, 0], [0.2, 1.16, 0], 0.023, M.frame);
  rod([0.37, 0.27, 0], [front, wy, 0], 0.026, M.darkMetal);
  for (const z of [-0.036, 0.036]) rod([0.39, 0.25, z], [0.48, 0.135, z], 0.018, M.frame);
  cylinder(0.033, 0.033, 0.023, M.black, [0.35, 0.34, 0]);
  tube(
    [
      [0.2, 1.16, -0.24],
      [0.2, 1.165, 0],
      [0.2, 1.16, 0.24],
    ],
    0.011,
    M.paint,
  );
  grips(0.2, 1.16, 0.24);
  box(0.035, 0.028, 0.037, M.black, [0.22, 1.105, 0]);
  box(0.003, 0.018, 0.029, M.lens, [0.239, 1.105, 0], context.model, 0.002);
  fender(rear, wy, 0.149, 0.068);
  fender(front, wy, 0.146, 0.064);
  box(0.034, 0.014, 0.038, M.red, [-0.61, 0.2, 0]);
  for (let x of [rear, front])
    for (let z of [-0.048, 0.048])
      cylinder(0.016, 0.016, 0.002, M.accent, [x, wy, z], context.model, 'z', 24);
  tube(
    [
      [0.2, 1.13, 0.06],
      [0.16, 1.05, 0.1],
      [0.25, 0.78, 0.027],
      [0.36, 0.34, 0.024],
    ],
    0.0028,
    M.cable,
  );
  rod([-0.28, 0.16, -0.07], [-0.34, 0.025, -0.14], 0.006, M.black);
  decal(context.visual.name.split(' ')[0], 0.25, 0.03, [-0.08, 0.19, 0.081]);
  context.batteryGroup = group('Integrated commuter battery');
  context.batteryGroup.position.set(-0.1, 0.19, 0);
  box(0.45, 0.035, 0.11, M.black, [0, 0, 0], context.batteryGroup);
  context.controllerGroup = group('Commuter controller envelope');
  context.controllerGroup.position.set(0.19, 0.19, 0);
  box(0.12, 0.035, 0.11, M.alloy, [0, 0, 0], context.controllerGroup);
}
