# Commuter and adjacent scooter expansion

Assigned: 89 exact scooter names, excluding the existing accepted references. Authoring scope is limited to the commuter expansion paths. Product photos retain brand ownership; no open image license is asserted.

`selected.json` records downloaded exact product photographs and primary source URLs. Regional trim is disclosed explicitly, including Segway E/P/D and Joyor ABE. Ausom Gosoul 2 Pro and K20 Pro use the EU Single Motor option, distinct from the existing Dual Motor names.

`build.py` authors Blender geometry in meters, +X forward and Z up. Each asset has separate functional assemblies, a compressed native BLEND with packed reference, studio-free GLB, and 640px proof. These are approximate photo-guided visual reconstructions, not measured CAD; hidden faces and internal battery/controller geometry are inferred.

Wheel casting overrides distinguish the E2/E2 Plus rear vented castings, E2 Pro/KQi1 Pro front drums with narrow rim vents, ES1/ES2/ES4 three-rib rear wheels, and P65/P100S/GT1/GT3 enclosed front castings. Nonmotor housings stay in their wheel assemblies; they do not create additional motors. The exact-name/source review is retained in `wheel-reference-review.json`.

`unresolved-audit.json` preserves the remaining exact legacy-name audits with checked source URLs. These products are not declared nonexistent. The unresolved issue is exact full-product photography or revision identity; related current variants were rejected rather than renamed.

Run Blender 4.5 with `--background --threads 2 --python scripts/blender/expansion/commuter/build.py`. Explicit canonical keys after `--` rebuild those assets; `COMMUTER_REBUILD=1` rebuilds every selected asset. `validate.py` independently reopens every BLEND and imports every GLB, checking packed references, metric units, nonempty required groups, bounds, triangle/mesh counts and actual file sizes. `qa_sheets.py` creates reference/render contact sheets and an HTML gallery.

The public manifest is written atomically only after exports and review; entries contain completed assets. Parent owns central integration and application tests.

`finish_assets.py` applies the final native finish and source-specific corrections (ES internal battery housing, nonmotor front drum covers, GT/P fairings, ZT3 low X lamp, S1 Pro open honeycomb tires, M5 Pro teal wheel accents) and re-exports with measured file statistics. Run it once after the build; it is a finalization stage rather than an idempotent authoring script.

## Reproducing the reviewed pipeline

The production scripts (`build.py`, `finish_assets.py`, `validate.py`, `assemble.py`, `sheets.py`, and `qa_sheets.py`) derive the repository root from `Path(__file__).resolve().parents[4]`. `build.py` loads its sibling `primitives.py` through that root; the helper has no independent filesystem paths. Existing selected references and audit artifacts are inputs, and the output locations remain unchanged. Python needs Pillow for the contact sheets; Blender supplies `bpy`, `bmesh`, and `mathutils`. No dependency installation is part of this pipeline.

From the repository root, with Blender 4.5 and a Python interpreter containing Pillow available:

```sh
BLENDER=blender
PYTHON=python3
COMMUTER_REBUILD=1 "$BLENDER" --background --threads 2 --python scripts/blender/expansion/commuter/build.py
"$BLENDER" --background --threads 2 --python scripts/blender/expansion/commuter/finish_assets.py
"$BLENDER" --background --threads 2 --python scripts/blender/expansion/commuter/validate.py
"$PYTHON" scripts/blender/expansion/commuter/sheets.py
"$PYTHON" scripts/blender/expansion/commuter/qa_sheets.py
```

Review `artifacts/blender/expansion/commuter/verification.json`, every reference/render pair in `qa-gallery.html`, and `unresolved-audit.json`. After that review, publish the completed entries atomically:

```sh
"$PYTHON" scripts/blender/expansion/commuter/assemble.py
```

Set `BLENDER` to the installed executable path if it is not on PATH. To rebuild a subset, pass the same canonical keys after `--` to both `build.py` and `finish_assets.py`; omit `COMMUTER_REBUILD=1` in that case. Start from a fresh build before applying the non-idempotent finish pass. These commands regenerate assets and the last command writes the public manifest; they are documentation, not part of the path-only cleanup verification.

The remaining Python files are local research/recovery helpers, not production stages. Some retain the original workspace path, depend on the repository working directory, consume cached network responses, or patch authoring inputs/scripts. They document the source-recovery session and should not be run as a portable batch pipeline.
