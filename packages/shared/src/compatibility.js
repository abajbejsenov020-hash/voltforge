import { selectParts } from './build.js';
import { canonicalVehicleName, normalizeVehicleName } from './vehicles/index.js';
export function checkCompatibility(state) {
  const p = selectParts(state),
    issues = [];
  const batteryV = Number(state.specs.fullV) || p.Batteries?.fullV || 0,
    limit = p.Controllers?.maxV,
    dropout = Number(state.specs.dropout),
    bms = Number(state.specs.bms),
    current = Number(state.specs.batteryLimit);
  function add(kind, text) {
    issues.push({ kind, text });
  }
  if (p.Controllers && p.Batteries) {
    if (batteryV && limit) {
      if (batteryV >= limit)
        add(
          'conflict',
          `Battery full-charge voltage (${batteryV}V) ${batteryV === limit ? 'equals' : 'exceeds'} the controller’s published ${limit}V ceiling. Choose a lower-voltage pack or a controller with adequate operating and regeneration headroom.`,
        );
      else
        add(
          'pass',
          `${batteryV}V full charge is below the controller’s published ${limit}V ceiling. This only checks the upper voltage limit; verify operating range and regeneration headroom.`,
        );
    } else
      add(
        'unknown',
        'Controller operating voltage is unverified. Check the exact hardware revision and its operating envelope before choosing a pack.',
      );
  } else add('unknown', 'Add a battery and controller to compare full-charge voltage.');
  if (p.Motors) {
    if (p.Motors.type !== state.type && p.Motors.type !== 'both')
      add(
        'conflict',
        'The selected motor is cataloged for a different vehicle type. Confirm a suitable drivetrain before proceeding.',
      );
    if (dropout && p.Motors.dropout) {
      if (dropout !== p.Motors.dropout)
        add(
          'conflict',
          `Your measured ${dropout}mm dropout differs from the motor’s listed ${p.Motors.dropout}mm opening. Review motor or frame selection.`,
        );
      else
        add(
          'pass',
          `The entered dropout matches the listed ${dropout}mm opening. Axle flats, thread length, torque retention, brake offset and clearances still need checking.`,
        );
    } else
      add(
        'unknown',
        'Motor fitment needs measured dropout width, axle details, brake alignment and tire clearance.',
      );
    if (p.Motors.ratedV && p.Batteries && p.Batteries.nominal !== p.Motors.ratedV)
      add(
        'unknown',
        `Motor is rated ${p.Motors.ratedV}V; this pack is listed ${p.Batteries.nominal}V nominal. Confirm winding, speed and thermal limits with the motor supplier.`,
      );
  }
  if (p.Controllers && Number(state.specs.motorCount) > p.Controllers.channels)
    add(
      'conflict',
      `This is a ${p.Controllers.channels}-channel controller and the plan uses ${state.specs.motorCount} motors. Each independently driven motor needs a controller channel. Select a dual controller or revise the controller quantity.`,
    );
  if (
    p.Displays &&
    p.Controllers &&
    p.Displays.platform &&
    p.Controllers.platform &&
    p.Displays.platform !== p.Controllers.platform
  )
    add(
      'conflict',
      `${p.Displays.platform} display and ${p.Controllers.platform} controller use different platforms. Select a matching display and verify the exact protocol.`,
    );
  if (p.Displays && p.Controllers && (!p.Displays.platform || !p.Controllers.platform))
    add(
      'unknown',
      'Display/controller protocol is unverified. Confirm the exact communications protocol and harness.',
    );
  if (bms && current) {
    if (current > bms)
      add(
        'conflict',
        `Planned battery current (${current}A) exceeds the entered BMS continuous rating (${bms}A). Reduce the planned limit or revise the pack.`,
      );
    else
      add(
        'pass',
        'Entered battery current is within the entered BMS continuous rating. Cells, fuse, wiring and connectors need independent ratings checks.',
      );
  } else
    add(
      'unknown',
      'Enter the pack BMS continuous current rating and planned battery current. Phase current is a different value.',
    );
  if (state.mode === 'rebuild') {
    const canonical = canonicalVehicleName(state.vehicle);
    for (const item of Object.values(p)) {
      if (
        item.models &&
        !item.models.some((name) => normalizeVehicleName(name) === normalizeVehicleName(canonical))
      )
        add(
          'unknown',
          item.brand +
            ' ' +
            item.name +
            ' is listed for ' +
            item.models.join(', ') +
            ', while your rebuild is ' +
            canonical +
            '. Cross-model adaptation is unverified.',
        );
    }
  }
  if (p.Controllers?.nominalV && p.Batteries && p.Controllers.nominalV !== p.Batteries.nominal)
    add(
      'unknown',
      'Selected OEM controller has a ' +
        p.Controllers.nominalV +
        'V nominal system reference, while the pack template is ' +
        p.Batteries.nominal +
        'V nominal. Confirm the exact operating envelope; nominal voltage is not the maximum input rating.',
    );
  if (state.mode === 'rebuild')
    add(
      'unknown',
      `${state.vehicle}: name-only starting point. Verify model year, battery label, frame dimensions, stock harness and installed component variants.`,
    );
  if (Object.values(p).some((x) => x.request || x.variant))
    add(
      'unknown',
      'One or more parts require an exact supplier variant. Catalog names are insufficient to confirm fitment.',
    );
  add(
    'unknown',
    'Physical battery/controller envelopes, wiring pinouts, cooling, brakes and structural suitability remain unverified. The 3D model is illustrative.',
  );
  return issues;
}
