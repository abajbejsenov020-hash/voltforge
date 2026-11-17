# Vehicle appearance audit

The indexed name catalog is unchanged. The appearance library combines the original 60 references with three separately audited expansion manifests:

| Batch                                       | Assigned names | Manifest                                            |
| ------------------------------------------- | -------------: | --------------------------------------------------- |
| Commuter scooters                           |             89 | `apps/web/src/data/vehicle-expansion-commuter.json` |
| Premium scooters                            |             99 | `apps/web/src/data/vehicle-expansion-premium.json`  |
| Remaining bicycles and electric motorcycles |             97 | `apps/web/src/data/vehicle-expansion-bikes.json`    |

Each completed entry includes a local product photo, its source page and image URL, the identified trim, actual image dimensions, and an individually exported GLB with an editable BLEND source. Named front/rear wheel, motor, battery and controller assemblies preserve the viewer's component and exploded-view controls. Exterior construction follows the selected reference's frame, suspension, wheel covers, tires, seat, body panels and accessories. Hidden mechanisms and dimensions remain approximate; these are appearance reconstructions, not manufacturer CAD or fitment measurements.

Family names without a generation suffix identify the particular trim in their visible reference note. Explicitly different named models require their own reference or documented exterior alias. An unresolved source audit does not mean a product does not exist: the original name remains searchable, with its retrieval/identity limitation shown instead of borrowing an adjacent variant's image or geometry. Photo copyright stays with the credited owner; the manifests do not assert an open image license.

`apps/web/src/data/vehicle-artwork.js` merges completed entries for the finder, photo view and exact-name Blender loader. `apps/web/public/assets/vehicles/unresolved.json` records coverage and unresolved reasons. Run the complete gate from the repository root:

```sh
node scripts/catalog/verify-artwork.mjs --complete --write-status
npm run check
PLAYWRIGHT_CHANNEL=chrome npm run test:browser -- tests/browser/expanded-artwork.spec.js
```

The complete gate requires every previously unpictured name to have either completed assets or an actual source audit. Node tests parse every public GLB through the browser's Three.js loader, verify semantic assemblies, finite geometry, ground placement and manifest sizes, and exercise component replacements. Browser journeys cover each expansion batch, exact finder thumbnails, decoded photos, loading, camera controls, exploded views, restoration and an unresolved original variant.

Blender 4.5 LTS construction and reference-selection scripts are under `scripts/blender/expansion/{commuter,premium,bikes}/`. Native sources are under `assets/blender/expansion/`; final renders, photo/model contact sheets, source records and independent reopen audits are under `artifacts/blender/expansion/`. The batch READMEs describe their authoring/finalization steps. A changed native source must be re-exported, reviewed against its exact photo, and have its manifest statistics regenerated before it is considered complete.

Downloaded research HTML, full vendor PDF catalogs and sitemap snapshots are excluded from Git. Their source URLs and the selected asset provenance remain in the manifests/audit records; rebuilding completed geometry uses the curated inputs and local reference photos.
