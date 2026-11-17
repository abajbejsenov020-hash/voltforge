# KuKirin and Ausom reference-guided Blender catalog

Run from repository root, with Blender 4.5 LTS:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --threads 2 --python scripts/blender/batches/scooters/build.py
```

Pass canonical keys after `--` to rebuild selected vehicles. No external Python modules or downloads are required for regeneration. The manifest and reference images are repository inputs. Every asset starts with factory-empty Blender data and purges construction orphans before compressed save.

Outputs: `apps/web/public/models/catalog/scooters/<key>.glb`, `assets/blender/catalog/scooters/<key>.blend`, and `artifacts/blender/catalog/scooters/<key>.png` plus a JSON asset note. The catalog manifest is `apps/web/src/data/blender-scooters.json`.

The generator authors family-specific cast necks, front suspension types, rear arms, hub motors/spoked wheels, battery deck cross sections, stem sections, lamp placements, grips, cables, coil springs, brake discs and trim. Related regional G2 Pro variants intentionally share their verified base platform; the photographed standard G2 Pro has a modeled seat. K20 Pro and Laluz 2 Pro are a manufacturer-confirmed physical alias and intentionally share their physical configuration.

## Source provenance

All models are visual reconstructions from exact catalog photographs. Proportions approximate the photographs in real metres; they are not measured CAD. Hidden faces and internal battery/controller assemblies are inferred. Actual reference and manufacturer page are stored in every native root and asset report. References are packed into each native file and excluded from GLB. Procedural microscopic rubber texture remains editable in Blender; GLB retains PBR material color, metallic and roughness values.

The previous Laluz image was a corrupt/cropped 40×40 thumbnail. A full 1000×1000 manufacturer image was fetched, visually inspected, and stored at `apps/web/public/models/catalog/scooters/references/ausom-laluz-2-pro-primary.jpg`; both canonical aliases now reference this complete photo in the Blender and central vehicle-reference manifests. Source: [official K20 Pro (Laluz 2 Pro) product page](https://ausomstore.com/products/ausom-k20-pro-dual-motor-e-scooter). The source image URL is recorded in the manifests.

For F1 Max, the exact catalog photo contains a rider obscuring the chassis. The clean manufacturer three-quarter photo at `references/ausom-f1-max-primary.jpg` supplements it and confirms twin front coil shocks, twin circular lower headlamps, long ribbed deck, shaped suspension arms and radial motor covers. Source: [official F1 Max product page](https://ausomstore.com/products/ausom-f1-max-electric-scooter). Full manufacturer product JSON is saved with QA artifacts for traceability.

## Coordinates and service groups

Front is +X, axles are Y, vertical is +Z, scene origin is at the floor, glTF exports with +Y up. Named assemblies `FrontWheel`, `RearWheel`, `BatteryMount`, `ControllerMount`, and `MotorMount` are preserved. Battery and controller are modeled inside the opaque deck. Root metadata identifies the exact model key and observed reference features. Studio camera, lights, floor and packed reference objects are excluded from GLB.

Export checks enforce fewer than 160,000 triangles, 70 mesh objects and 20 MB per GLB; current files target 1–5 MB. Each compressed native file contains only its own vehicle and studio. Render checks are 640×640 Cycles, 32 samples, denoised, two render threads. These are photo-based visual QA proofs, not dimensional certification.
