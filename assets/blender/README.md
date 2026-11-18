# Blender vehicle sources

The G4 and Light Bee X previews are built in Blender from the product reference images already recorded in `apps/web/src/data/vehicle-references.json`. They are independently modeled appearance studies; their dimensions and hidden mechanisms are not manufacturer CAD or fitment evidence.

The editable sources are `kukirin-g4.blend` and `surron-lbx.blend`. Web exports are in `apps/web/public/models/`. The construction scripts are in `scripts/blender/`; run them from the repository root with Blender's bundled Python:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --threads 4 --python scripts/blender/g4.py
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --threads 4 --python scripts/blender/surron_lbx.py
```

Use Blender 4.5 LTS. On this machine Blender 4.5.16 was installed from the official Apple Silicon download, after verifying the release's published SHA-256 checksum. Blender itself is installed separately and is not bundled into the repository or needed to run the web app.

Each model uses physical meter units, with the front along +X and Blender Z up. GLB export converts to glTF Y up. Named battery, controller and motor mount groups allow inspection and component changes. The viewer retains the original image as an appearance reference.

The render previews in `artifacts/blender/` are produced for visual checks. Source edits should be re-exported and inspected in the web viewer because browser materials and lighting differ from Blender's renderer.

The [appearance audit](../../docs/vehicle-artwork.md) covers 292 native sources under `expansion/{commuter,premium,bikes}/`, alongside the original 60 models. The three expansion manifests record exact photos, source URLs, visible trim notes, public GLBs, and actual export statistics. All 355 indexed names are audited, with three unresolved variants using explicitly labeled concepts. Batch construction, native reopen audits, and photo comparisons are documented in the corresponding scripts and artifacts directories.
