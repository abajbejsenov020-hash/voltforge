# Expanded Blender catalog QA

Scope: 58 new photo-based models plus the existing KuKirin G4 and Sur-Ron Light Bee X, for 60 pictured catalog entries. The other 285 indexed names have no matching Blender asset and retain an explicitly labeled concept.

## Final integration results

- `npm run check`: formatting, 122 Node tests and production build passed.
- `PLAYWRIGHT_CHANNEL=chrome npm run test:browser`: 16 browser tests passed. The new journeys exercise 27 representative vehicles across all three modeling batches, camera/cockpit/reset, exploded view, original-photo switching, exact model selection and reload. Existing G4/LBX, mobile, performance, saving, offline and migration journeys also pass.
- After repairing an empty Talaria Junior ET01 controller mount, the complete 122-test suite and production build passed again; the 11-vehicle lightmoto browser journey passed again against the repaired export.
- Every GLB parses through Three.js, has finite geometry and nonempty wheel, battery, controller and motor groups. Replacement and exploded-view checks preserve usable bounds. All 60 manifest byte sizes match the files and native sources exist.
- Exact catalog names select their own asset. Aliases resolve without borrowing geometry for the other unpictured indexed variants. Failed model requests display an explicit concept fallback and retain the build results.
- Independent runtime review found no unresolved issues: all 60 final GLBs parsed with valid indices and unique nonempty service groups; all 180 battery/controller/motor replacement checks fit their authored envelopes. A reverse-completion stress check of 60 concurrent loads retained only the newest model and disposed the 59 stale loads. This review checks runtime behavior, not measured physical accuracy.

## Visual review

All 58 final reference/render pairs were inspected. Each family contains `comparison-*.jpg` sheets with the reference on the left and reconstructed model on the right. Per-model PNGs are 640px studio proofs. The moto/bicycle family also includes `qa-gallery.html`. The actual browser presentation was reviewed for scooters, bicycles and the Hyper/Ultra Bee material colors.

Changes following review include shaped Stark plastics, Arctic perimeter frames, Fiido lamps and battery detail, scooter suspension arms and lamp arrangements, Sur-Ron frame/livery corrections, and transform baking to remove loose below-floor export bounds. A corrupt Laluz thumbnail was replaced by a complete primary manufacturer image; its documented K20 alias shares the physical model.

Family-specific geometry measurements and native verification are recorded in `scooters/verification.json`, `lightmoto/validation-summary.json`, `lightmoto/native-validation.json`, `moto-bicycle/coverage.json` and `moto-bicycle/native-coverage.json`.

These are exterior photo reconstructions, not measured manufacturer CAD. Dimensions, hidden mechanisms, tiny decals, material calibration and some obscured details remain approximate. Component previews within the model envelopes do not certify real-world fit.
