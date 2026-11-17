# Photo-derived lightweight motorcycle catalog

Build with Blender 4.5 LTS, no add-ons or external packages:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --threads 2 --python scripts/blender/batches/lightmoto/build.py
# Rebuild one entry:
/Applications/Blender.app/Contents/MacOS/Blender --background --threads 2 --python scripts/blender/batches/lightmoto/build.py -- --key sur-ron-hyper-bee
python3 scripts/blender/batches/lightmoto/validate.py
```

`build.py` reconstructs the visible chassis, pack, forks, suspension, wheels, brake rotors, motor, drive chain, controls, lamps, fairings and principal graphics from the catalog photographs. `primitives.py` adapts the accepted Light Bee X mesh construction; the donor asset/source remain unchanged. All exported models face +X in Blender, use metres and rest on Z=0. GLB uses glTF Y-up conversion. Semantic `FrontWheel`, `RearWheel`, `BatteryMount`, `ControllerMount`, `MotorMount` nodes remain separate.

Distinct geometry families: Talaria Sting / Sting Pro / Komodo / XXX / Junior ET01; E Ride SS 2.0 / SS 3.0 / SR / S / 4.0 / Mini R; Sur-Ron Ultra Bee / Storm Bee / Hyper Bee; Altis Sigma / Delta / Omega. Wheelbase, wheel radii, tyre width, seat height, cockpit height, frame width, body panels and equipment follow each reference. The homologated Talarias add mirrors, plate brackets and reflectors. Genuine Talaria source aliases retain separate catalog names and file paths while sharing reconstructed physical geometry.

Each native file includes its packed reference photograph and studio rig. Each GLB contains only the motorcycle. Files are compressed on native save and unused data are purged between models. Each entry has a 640×640 Cycles render at 32 samples / 2 CPU threads and a JSON measurement record in `artifacts/blender/catalog/lightmoto/`.

Limitations: these are visual reconstructions, not manufacturer CAD. Dimensions, hidden structures and fitment interfaces are approximate. Tiny warning labels, full exact brand typography, mould texture and internally hidden fasteners are simplified. The XXX/XXX MX reference is an action photograph with a rider, so some underseat/central details are obscured; the visible long battery/frame layout is preserved. The stock photograph licenses are not asserted as open; the existing source and credit metadata remain authoritative.
