# Remaining bicycle catalog

97 model-specific references and editable exterior reconstructions. The authoritative input is `artifacts/blender/expansion/bikes/ready-references.json`; parameters are in `specs.py` and named silhouette/component branches in `build.py`. Sources are retained in the manifest and research snapshots. Dimensions are approximate visual proportions, not manufacturer CAD or fitment data.

Run from the repository root with Blender 4.5 LTS and Python 3:

```sh
blender --background --threads 2 --python scripts/blender/expansion/bikes/build.py
blender --background --threads 2 --python scripts/blender/expansion/bikes/clean_native.py
blender --background --threads 2 --python scripts/blender/expansion/bikes/verify_native.py
python3 scripts/blender/expansion/bikes/audit.py
python3 scripts/blender/expansion/bikes/pairs.py
```

The first command resumes missing validation files. To deliberately rebuild a reviewed model, pass its key after `--`, e.g. `-- trek-marlin trek-marlin-plus`. Remove only that model's generated validation file to include it in a full resume. `clean_native.py` repacks the current model reference and removes unrelated packed images; `audit.py` checks every assigned name, actual GLB triangle/mesh/byte counts, finite accessor bounds, required populated semantic groups, floor grounding and exclusion of studio objects. It atomically writes `apps/web/src/data/vehicle-expansion-bikes.json` only when all 97 pass. `pairs.py` needs Pillow already available in the task Python runtime and generates 13 comparison sheets.

`build.py` reuses the accepted geometry primitives in `scripts/blender/batches/moto-bicycle/build.py` and `scripts/blender/batches/lightmoto/` without changing those generators or their outputs. All production paths derive from `__file__`; source collection and iterative patch helpers are retained as local research history and are not reproduction steps.

Each GLB is metric, +X forward in Blender / glTF Y-up on export, grounded, and contains only vehicle geometry. A neutral 640px Cycles 16-sample proof and compressed editable `.blend` accompany each model. Five viewer groups are always populated: FrontWheel, RearWheel, BatteryMount, ControllerMount, MotorMount. For Marlin, Talon and Rockhopper pedal bases, the last three are explicitly marked bottle/cable/crank service anchors; no electric equipment is asserted.

Reference identities distinguish Marlin / Marlin+ and the original EP-2 Pro, Fiido T1, XP 2.0 and XP Lite generations. The bare Sigma family uses the manufacturer-documented Sigma MX trim. XPedition and XPeak use their original generations. The XE Pro S Super source is a manufacturer product illustration and is marked accordingly. Photo licenses remain with their owners; no open license is asserted.

Proof: `artifacts/blender/expansion/bikes/audit.json`, `native-audit.json`, `native-proof.json`, `visual-review.json` and `pairs-*.jpg`. Browser integration and central catalog tests belong to the parent task.
