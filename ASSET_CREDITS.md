# Asset credits

Product images remain the property of their respective manufacturers, retailers and creators. Their inclusion as model references does not assert an open license or imply manufacturer affiliation. The repository's MIT license covers the application code, not third-party photography, branding or product renders.

## Vehicles

`apps/web/src/data/vehicle-references.json` records each reviewed model's local image, original image URL, source page, credit, variant note and dimensions. It includes manufacturer references from KuKirin, Ausom, Sur-Ron, Talaria, Stark Future, Arctic Leopard, E Ride Pro, Altis and Fiido. Some images are manufacturer renders rather than camera photographs.

The KuKirin G4 and Sur-Ron Light Bee X references include the images explicitly provided by the user. The LBX reference is credited to MXWraps and may show graphics that differ from stock. Older source references remain in `packages/shared/src/vehicles/featured.json`.

## Components

`packages/shared/src/catalog/appearances.json` records sources, image URLs, physical appearance notes and approximate model parameters for 94 product references. Product names identify examples, not live availability or verified fitment. Custom specification templates and OEM requests have no invented product image.

## Environments

Environment images and HDRIs are [Poly Haven CC0 assets](https://polyhaven.com/license), with source URLs and checksums in `apps/web/public/environments/environments.json`:

- [Auto Service](https://polyhaven.com/a/auto_service), Sergej Majboroda / Poly Haven — HDR panorama and workshop backplate.
- [Courtyard](https://polyhaven.com/a/courtyard), Greg Zaal / Poly Haven — HDR panorama.

## Libraries and fonts

Three.js is distributed under its MIT license in `node_modules/three/LICENSE`; npm includes it with the dependency. Procedural concept geometry is application code, not manufacturer CAD. DM Sans and Manrope are requested from Google Fonts with system font fallbacks; their upstream licenses are the SIL Open Font License.
