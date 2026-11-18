# Teverun and Segway performance remodels

The Blender project and GLB for each model use the catalog's existing paths. The
profile table records approximate photo dimensions and the exterior hardware
that distinguishes each scooter. The models use meters and face along positive
X before Blender's Y-up glTF conversion.

Rebuild with Blender 4.5 from the repository root.

```sh
blender -b -t 3 --python scripts/blender/remodel/teverun_performance/build.py -- --render
```

Pass one or more catalog keys after `--render` to rebuild selected models.
The script writes the comparison renders and revised manifest rows to
`/tmp/voltforge-performance` by default. `--output` selects a different directory.
The script reads the catalog manifests without modifying them.

- The Segway P, GT and ZT families have different deck sections, steering
  castings and suspensions. The GT1 rear drive and GT2 driven axles are modeled
  separately.
- The Teverun Fighter and Blade scooters use separate cast arm profiles,
  battery tray contours, heel braces and projector positions.
- Stock electrical parts, wheels and cockpit geometry have the named groups
  used by the configurator. Their finish material names follow the existing
  paint conventions.
- The Blade GT reference is the first-generation model from the Teverun
  manual. The Fighter Supreme reference shows the original 2023 model.
  Segway GT3 and ZT3 photos are the original clean product images over a
  neutral background.

Product photos are guides for the exterior artwork. Hidden parts and dimensions
are visual approximations. Check the model's manual for service specifications.
