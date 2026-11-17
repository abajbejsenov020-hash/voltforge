# Blender vehicle library

This batch extends the two original Blender models with the remaining 58 vehicles that have product-image references. The catalog is divided by modeling family:

| Family                                 | Build script                                    | Web models                                     | Editable sources                       |
| -------------------------------------- | ----------------------------------------------- | ---------------------------------------------- | -------------------------------------- |
| KuKirin / Ausom scooters               | `scripts/blender/batches/scooters/build.py`     | `apps/web/public/models/catalog/scooters/`     | `assets/blender/catalog/scooters/`     |
| Sur-Ron / Talaria / E Ride Pro / Altis | `scripts/blender/batches/lightmoto/build.py`    | `apps/web/public/models/catalog/lightmoto/`    | `assets/blender/catalog/lightmoto/`    |
| Arctic Leopard / Stark / Fiido         | `scripts/blender/batches/moto-bicycle/build.py` | `apps/web/public/models/catalog/moto-bicycle/` | `assets/blender/catalog/moto-bicycle/` |

The three `apps/web/src/data/blender-*.json` manifests bind exact catalog names to their model, native source, reference image and source page. Their statistics describe the generated GLB. Different model names are kept distinct; physically identical aliases are documented in the manifest notes.

Run a family script with Blender 4.5 LTS from the repository root, for example:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --threads 2 --python scripts/blender/batches/lightmoto/build.py
```

Each family script supplies model-specific parameters and geometry for its references. Regeneration also produces proof renders and validation notes under `artifacts/blender/catalog/`. Inspect those renders against the reference images before publishing an updated model.

The models use meters and Blender Z up, with the front facing +X. GLB export converts to glTF Y up. `FrontWheel`, `RearWheel`, `BatteryMount`, `ControllerMount` and `MotorMount` are retained for camera inspection, exploded view and visual component substitutions. Substituting a component into the stock visual envelope does not establish physical fit.

These are photo-based appearance reconstructions. Hidden/internal geometry, small branding and some regional details are approximate. The remaining name-only entries in the larger vehicle index have no Blender model assigned; their conceptual fallback stays explicitly labeled.
