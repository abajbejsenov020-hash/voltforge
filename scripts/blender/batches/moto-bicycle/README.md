# Arctic Leopard, Stark and Fiido photo reconstruction batch

19 individually catalogued vehicles. Source pages and exact local reference images are recorded in `apps/web/src/data/blender-moto-bicycle.json`. Each native `.blend` packs its original reference image. This is a visual reconstruction from those references, not manufacturer CAD or dimensional certification.

Regenerate from repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 --python scripts/blender/batches/moto-bicycle/build.py
/Applications/Blender.app/Contents/MacOS/Blender -b -t 3 --python scripts/blender/batches/moto-bicycle/audit_native.py
python3 scripts/blender/batches/moto-bicycle/validate.py > artifacts/blender/catalog/moto-bicycle/coverage.json
```

Append `-- <key> ...` to regenerate selected entries. The script constructs the manifest directly from the existing approved reference catalog, builds editable objects and named semantic mounts, exports GLB with Y up, and produces a 640 × 640 Cycles render at 32 samples with three CPU threads. Blender coordinates use metres, X forward, Z up, ground origin.

## Reference-driven geometry

- **Arctic XF / XE Pro:** rounded open perimeter chassis and removable battery, slim external black finned controller integrated into the front frame edge, round lower motor, open seat rails, rear coil, chain drive. XF Pro follows the lime reference; MX is graphite; Super is pink with road tyres. XE Pro R and S Enduro have taller front wheel proportions/gold fork; base S and L1E have black fork. XE trims include the visible rear hugger. L1E has a front LED and rear road equipment.
- **Arctic full-size E-XE:** wider compound curved radiator and rear plastics, shaped integrated battery, diagonal chassis braces, white fork guards and long silver swingarm. 880 Enduro and L3E use red/white reference colours; 880 Super and 800 Enduro use dark grey/black. Super has broad smooth road wheels. L3E includes mirrors and road equipment.
- **Stark Varg:** long contoured black seat, compound curved red radiator/rear plastics, tapered cooling case and visible diagonal frame spar. Base MX has a dark motor face; MX 1.2 and Factory have the revised silver casting. EX has handguards and headlamp. SM has road tyres and road equipment. Skoll follows the black body and shorter rear blade. Factory has white rear number fields.
- **Fiido M1 Pro:** teal broad hinged folding main beam, six-spoke cast wheels, fat tan-wall tyres, gold fork, separate rear triangle/red coil, bicycle saddle, crank/pedals, chain and derailleur.
- **Fiido C11:** low open step-through frame, dark downtube battery insert and small threaded mounts, narrow spoked commuter wheels, telescopic fork, full mudguards, elevated headlamp and rear cargo rack. The supplied photograph shows a rack without a basket; no basket was invented.

All wheels have separate rims/hubs, spokes or cast spokes, disc rotors/calipers. Motos include rear coil, chain/sprockets, pegs, fork clamps, ribbed grips, levers, cables and dash. Meshes aggregate by semantic group/material with baked world-coordinate vertices to keep draw calls bounded.

## Visual checks and limits

All 19 original reference images were opened before construction. Initial family renders were compared to the original images; this prompted replacing flat Stark shrouds with compound curved shells, rounding the battery belly, rounding Arctic frame corners, moving/darkening the controller, improving curved seats/fenders/cables, and correcting the C11 battery insert and lamp position. A native-file reload audit also verifies persisted packed image datablocks and metric display settings. The final render set is checked per model, and GLB validation reports binary integrity, semantic nodes, actual exported triangle/mesh/byte totals, ground bounds, native files and 640px renders.

Unseen opposite-side detail is inferred with symmetry. Dimensions and wheelbase are visually estimated. Small brand lettering, decals, casting fasteners and tyre patterns are simplified rather than pixel-identical photographic textures. Photos cannot verify internal construction, absolute dimensions or engineered component clearances. Studio floor/camera/lights are included only in `.blend`, excluded from GLB.
