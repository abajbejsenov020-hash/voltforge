# Photo and render comparison notes

Scope: 17 exact catalog entries, inspected against all 17 supplied images, with complete manufacturer replacements/supplements where the catalog image was insufficient. Individual 640×640 three-quarter proofs are `<canonical-key>.png`; five `comparison-*.jpg` sheets place each reference beside its render.

These are editable photographic reconstructions at approximately real-world scale. They preserve visible platform differences; they do not assert factory dimensions, hidden engineering detail, exact paint calibration, or CAD identity. Internal battery/controller boxes are inferred and concealed inside the deck.

| Reference                     | Features used for reconstruction and comparison                                                                                                                                                       |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| KuKirin G2 Max                | Long rectangular telescopic mast, orange solid swinglinks, open front spokes, single rear hub motor, low round headlight, orange deck lines.                                                          |
| KuKirin G2 Master             | Two hub motors, dark cast swinglinks with triangular orange inserts, visible orange front/rear coils, broader deck, low square lamp.                                                                  |
| KuKirin G2                    | Smaller gray deck/chassis, real open triangular neck, gray arms with orange checker trim, open front wheel, console lamp.                                                                             |
| KuKirin G4 Ultra              | Larger/wider platform, wide road tires, dual closed hub motors, broad gray open neck and long mast, orange geometric trim.                                                                            |
| KuKirin M4 Max                | Silver deck and rear arms, conventional twin telescopic front fork, red rear shock and red stem clamp, low square headlight.                                                                          |
| KuKirin T4                    | Long low deck, gray flat cast arms with actual through-openings and thin orange inserts, angular fenders, gray mast panel.                                                                            |
| KuKirin G2 Pro ABE            | Seatless compact Pro platform, orange links, front spokes/rear motor, amber side reflector, low square lamp. Regional unseen differences are not invented.                                            |
| KuKirin G3 Pro                | Broad deck with removable battery side rail/fasteners, orange flat cast arms with real windows, broad orange mast panel, dual motors.                                                                 |
| KuKirin G2 Pro VMP            | Same photographed compact Pro base platform, seatless configuration, slotted rear kick support, orange links and low square lamp. Different photograph angle is not treated as different engineering. |
| KuKirin G2 Pro                | Exact supplied seated configuration: slotted seat pedestal, telescopic sprung post, orange quick clamp, padded saddle; Pro orange suspension.                                                         |
| Ausom DT2 Pro                 | Wide faceted deck, swept enclosed headstock, two closed hub motors, dark sculpted arms, angular canopy fenders.                                                                                       |
| Ausom L2 Max Dual Motor       | Slimmer deep gray deck with pointed end panels, shallow V swinglinks, dual hub motors, fender-level front light, detailed mast panel.                                                                 |
| Ausom Gosoul 2 Pro Dual Motor | Leading swingarm front suspension, dual hubs, knobby tread, purple deck side channel and high separate lamp.                                                                                          |
| Ausom K20 Pro Dual Motor      | Conventional front telescopic fork, gold rim pinstripes, dual hubs, purple side channel, swept swallow handlebar and rear adjustable coil.                                                            |
| Ausom Laluz 2 Pro Dual Motor  | Official manufacturer alias of K20 Pro; intentionally same physical configuration. Corrupt 40×40 supplied thumbnail replaced with complete 1000×1000 primary manufacturer image.                      |
| Ausom F1 Max                  | Rider-obscured supplied image supplemented with clean manufacturer photo; twin front coils, two round low lamps, shaped arms, radial hub covers, ribbed deck and rounded guards.                      |
| Ausom Gosoul 2                | Single rear motor and open-spoke front wheel, angular solid fork plates, diagonal side ribs, separate high lamp, dark rear swingarm.                                                                  |

The first integration bounds check identified an export AABB issue: consolidated meshes inherited rotated rod/text local axes, producing loose transformed accessor bounds below the floor despite all actual vertices being above it. Baking consolidated object transforms preserves the shape while giving correctly aligned export bounds. `normalize_exports.py` records actual minimum vertex height and verifies the aligned bound agrees within 0.01 mm. `verify.py` independently checks the exported GLB structure/counts and transformed bounds.

Rendering uses neutral studio lighting and AgX; painted parts can appear lighter than the outdoor or white-background product photos. Fine rubber bump nodes remain in Blender; GLB has the corresponding PBR scalar material properties and modeled tire/deck/grip relief. Small printed decals, exact tire lettering, unseen cable routes and hidden mechanical parts are approximations.

## Completed checks

All 17 final render/reference pairs were visually reviewed, including the manufacturer replacement for Laluz and clean supplemental F1 Max photo. Artifact verification passed for all 17 GLBs. Three.js `GLTFLoader.parseAsync` integration checks passed for all 17 scooter keys in `tests/blender-models.test.js`; log: `threejs-test.log`.

Final measured ranges: 59,600–75,392 triangles; 35–40 mesh objects; 1,697,688–2,257,520 GLB bytes; largest compressed native file 1,159,163 bytes. The transformed exported floor bound is between 0 and 0.000239 m for all 17. `verification.json` contains each individual result.

Central reference metadata has been updated alongside application integration. The catalog QA report records the final browser and integration checks.
