# Premium scooter catalog expansion

Scope: 99 assigned names, excluding the 60 already finished reference entries. All outputs remain approximate, photographic exterior reconstructions, not measured CAD or fitment claims.

`artifacts/blender/expansion/premium/references.json` stores audited exact images, product URLs and explicit trim/generation notes. `configs.json` is the canonical geometry configuration. Research helper scripts and downloaded public catalogs retain the source audit; they are not required to rebuild approved outputs.

Build using Blender4.5.16, metres, +X front and Z up. Two disjoint batches may run concurrently:

```
/Applications/Blender.app/Contents/MacOS/Blender --background --threads 2 --python scripts/blender/expansion/premium/render_revision.py -- 0
/Applications/Blender.app/Contents/MacOS/Blender --background --threads 2 --python scripts/blender/expansion/premium/render_revision.py -- 1
```

Reopen native files and verify packed exact photos, named nonempty assemblies, axes, transforms and bounds:

```
/Applications/Blender.app/Contents/MacOS/Blender --background --threads 2 --python scripts/blender/expansion/premium/audit_native.py
```

`audit.py` checks GLB structure, triangles, meshes, sizes, bounds and preview/proof metadata, and produces numbered photo/render comparison sheets. After those sheets have been visually inspected, `audit.py --publish` writes the parent integration manifest. It refuses incomplete revision2 builds or failed structural checks.

Distinct identities: original RS5 uses the manufacturer's launch reference and revised neck/lamp/flank geometry; RS5 PRO and MAX share an exterior only because the manufacturer's comparison documents a battery-only distinction. Original Cruiser uses a pre-S 2022 orange distributor photo; CruiserS uses its own manufacturer product photo. City uses the single-motor2022 reference, CityPro the dual-motor2023 reference. Hawk4000W and HawkProWide6000W have separate manufacturer references and visibly different tyres. BladeGT explicitly discloses GTII2024, the second generation documented in the manufacturer's catalog.

Hiley Tiger8 and Tiger9 base variants remain unresolved: the manufacturer's combined base/Pro catalog photos do not establish a standalone base motor configuration, and current retail photos identify Pro variants. No Pro look is silently assigned to those base names.

Final paths: manifest `apps/web/src/data/vehicle-expansion-premium.json`; GLBs `apps/web/public/models/expansion/premium/`; packed native files `assets/blender/expansion/premium/`; 640px renders, audits and comparison sheets `artifacts/blender/expansion/premium/`.
