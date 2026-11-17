const positive = (value) =>
  Number.isFinite(Number(value)) && Number(value) > 0 ? Number(value) : 0;

/** Steady shaft demand; acceleration and accessories are handled by the energy scenario. */
export function steadyRoadPower(kmh, { mass, cda, rolling, wind = 0, grade = 0 }) {
  const velocity = Math.max(0, kmh) / 3.6;
  const air = Math.max(0, velocity + wind / 3.6);
  return (0.5 * 1.225 * cda * air ** 2 + mass * 9.81 * (rolling + grade / 100)) * velocity;
}

/** Relative planning anchor, not a measured aerodynamic calibration or a speed guarantee. */
export function factorySpeedComparison(profile, type) {
  const speed = positive(profile?.advertisedSpeed);
  const motors = positive(profile?.motors);
  const rated = positive(profile?.ratedMotorW) * motors;
  const estimatedRated = !rated && positive(profile?.peakMotorW) * 0.5;
  const referencePower = (rated || estimatedRated) * 0.78;
  if (!speed || !referencePower) return null;
  const referenceLoad = steadyRoadPower(speed, {
    mass: 80 + (positive(profile.vehicleMass) || (type === 'bike' ? 25 : 30)),
    cda: type === 'bike' ? 0.55 : 0.65,
    rolling: type === 'bike' ? 0.009 : 0.018,
  });
  return {
    referenceSpeed: speed,
    referencePower,
    factor: referencePower / referenceLoad,
    estimatedRated: Boolean(estimatedRated),
    basis: `${profile.name}: ${speed} km/h factory claim and ${Math.round(rated || estimatedRated)} W ${estimatedRated ? 'assumed continuous input (50% of published peak)' : 'rated motor input'}; 78% reference efficiency, 80 kg rider, calm level road. This comparison is not GPS validation or a measured motor curve.`,
  };
}

export function solvePowerSpeed(power, road, comparison = null) {
  if (!(power > 0)) return null;
  let lower = 0;
  let upper = 360;
  for (let i = 0; i < 60; i++) {
    const middle = (lower + upper) / 2;
    if (steadyRoadPower(middle, road) * (comparison?.factor || 1) > power) upper = middle;
    else lower = middle;
  }
  return lower;
}
