# Factory defaults and 3D garage verification

## Behavior

Rebuilds resolve all eight categories as effective hardware. Saved `selected` contains only explicit catalog IDs; factory placeholders and inferred ratings are transient. Each replacement overrides its category, while unselected motor/controller/battery remain available to the performance engine. New builds receive no factory hardware. Factory references, measured observations and planning scenarios retain separate labels.

Factory data contains 60 exact model names, 57 with at least one verified numerical specification. Missing or conflicting ratings stay null, and exact variants do not borrow another indexed model's profile. Published battery energy supplies range without inventing source Ah; any energy/voltage capacity equivalent used for current planning is explicitly an assumption. Named OEM replacement motors use the documented factory-family rating with version caveats.

A same-model OEM motor or controller replacement preserves the factory speed and peak references when the rest of the powertrain remains stock. G4 with its matching replacement motor therefore stays at the 70 km/h and 2.4 kW factory references, rather than switching to a 53 km/h generic scenario. A different controller, battery, motor count, configured limits or model disables that baseline. Supplier requests remain unverified rather than being treated as confirmed stock replacements.

Returning a category to stock clears its obsolete hardware overrides. Restoring the whole powertrain retains other upgrades. A motor-count conversion clears old GPS/trip observations; its explicit count survives API validation and saving. Changing cruising speed does not materialize inferred vehicle mass or wheel size as saved measurements. Unknown wheel diameter is optional for saving observations, and source mass/wheel decimals do not fail browser input-step validation.

The default garage is actual room geometry with the existing Blender G4 Ultra and LBX parked behind the foreground build. `artifacts/garage/README.md` records visual and loading/disposal verification.

## Checks actually run

- Final `npm run check`: formatting, 142 Node tests and production build passed.
- The complete 20-test browser run found three issues: factory-derived fractional mass blocked two performance form submissions, and an older test expected Workshop instead of the new Garage default. The form precision and expected default were corrected.
- Final affected browser rerun: all 11 stock/workbench journeys passed, including matching G4 replacement, changed controller, retained factory battery, stock restore, legacy dual-to-single conversion, optional unknown wheel, observations, garage desktop/mobile, saving, offline tabs and migration. The other 9 browser journeys passed in the preceding complete run.
- Independent review: 240 profile/configuration probes; source/API/lifecycle review; same-OEM identity boundaries; no unresolved supported functional findings. An unconditional factory-reference sentence was made conditional in meaning to account for a different selected controller.
- Garage-specific browser checks: loading errors, delayed/stale loads, saved setting, rotation/zoom, desktop 1440 / phone 390 and stable GPU resource counts across four garage/studio cycles.

Figures remain factory claims or explicitly labeled planning scenarios, not measured performance or fitment certification. Geometry is visual reconstruction rather than manufacturer CAD.
