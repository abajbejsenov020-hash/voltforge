# Joyor catalog models

Build the 14 photo-guided Joyor models from the repository root with Blender 4.5.

```sh
blender -b -t 3 --python scripts/blender/remodel/joyor/build.py -- --render
```

Pass one or more keys from `models.py` after `--` to regenerate only those models. Omit `--render` to skip the side and three-quarter comparisons. Renders and the updated catalog metadata are written to temporary paths, which can be set with `--evidence` and `--metadata`.

`references.json` lists the photographed configuration and source for each model. The original S10-S uses the side image from Joyor’s pre-Z manual. The S5 and Y8-S show the German ABE variants. Joyor's Y10 appearance illustration also covers the shared Y-series chassis. The standard C10 uses the shared C10/C10 DGT body photo.

The files use metre-scale exterior estimates based on the photographs and published dimensions. Battery, controller and motor groups provide independent mounts for viewer controls. The render camera, studio lights and packed reference are included in the editable Blender source. The GLB contains only the vehicle geometry.
