# True 3D workshop

The shipped garage is generated from native Three.js mesh geometry in `apps/web/src/scene/garage.js`. It has finite concrete flooring, textured brick walls, cabinets, a workbench, pegboard tools, shelves, spare tires and practical lighting. The parked G4 Ultra and Sur-Ron LBX use the existing Blender GLBs at their authored scale, positioned behind the inspected build. No photograph is rendered as the garage backdrop.

`garage-desktop.png`, `garage-mobile.png` and `garage-orbit.png` show the actual browser rendering. `garage-concept.webp` is the earlier generated art-direction reference only; it is not requested by the web app.

The setting persists locally, with workshop/courtyard/studio alternatives. HDR lighting and parked vehicle loads can fail independently. Late loads cannot reinsert vehicles after leaving the room; separate resources are disposed on exit. Browser checks exercised desktop 1440 and phone 390 widths, rotation/zoom, setting persistence, failed HDR/one parked model, and leaving during a delayed load. Four garage/studio cycles showed stable buffer/texture/program counts after correcting an InstancedMesh cleanup issue. These observations are not a device-wide FPS guarantee.

Approximate final geometry budget with the original G4 inspected: 301k unique triangles including the two background vehicles; about 443k submitted with shadows, 173 desktop draw calls (158 phone). The scene renders on demand; parked vehicles do not each run their own animation loop.
