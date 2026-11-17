/** Human-readable source-backed factory specifications; absent ratings stay absent. */
export function factorySummary(profile) {
  if (!profile) return '';
  const items = [];
  if (profile.motors > 0)
    items.push(
      profile.motors +
        (profile.motors === 1 ? ' motor' : ' motors') +
        (profile.ratedMotorW > 0
          ? ' × ' + profile.ratedMotorW.toLocaleString('en') + ' W rated'
          : ''),
    );
  if (profile.nominal > 0 && profile.ah > 0)
    items.push(
      profile.nominal +
        ' V · ' +
        profile.ah +
        ' Ah · ' +
        Math.round(profile.nominal * profile.ah).toLocaleString('en') +
        ' Wh',
    );
  if (!(profile.nominal > 0 && profile.ah > 0) && profile.energyWh > 0)
    items.push(Math.round(profile.energyWh).toLocaleString('en') + ' Wh battery');
  if (profile.peakMotorW > 0)
    items.push((profile.peakMotorW / 1000).toLocaleString('en') + ' kW published peak');
  return items.join(' · ') || 'Factory specifications not yet verified for this exact model.';
}
export function componentName(part) {
  return part
    ? part.stock
      ? 'Stock · ' + part.name
      : [part.brand, part.name].filter(Boolean).join(' ')
    : 'Not selected';
}
