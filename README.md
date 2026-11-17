# Voltforge

An electric scooter, e-bike and e-moto build studio. Select your existing model or start a new build, inspect components, record measurements, and compare performance scenarios.

## Run locally

Requires **Node.js 24 or newer** and npm.

```sh
npm ci
npm run dev
```

Open **http://127.0.0.1:5173**. The development server forwards `/api` to the Node server on port 3001.

For the production build:

```sh
npm run build
npm start
```

Open **http://127.0.0.1:3001**. Node serves both the compiled frontend and API. This is a server application; opening `index.html` directly will not run it.

Optionally copy `.env.example` to `.env`. The root scripts load it automatically. Defaults bind to the local machine. Deployment requires a persistent writable directory for SQLite, HTTPS at the proxy, and `APP_ORIGIN` set to the public origin. No hosting service is provisioned by this repository.

## Structure

```text
apps/
  web/
    index.html             Application shell
    src/
      app/                 Controller and event bindings
      features/            Setup, catalog, review and performance UI
      state/               Local cache, migration and revision-aware sync
      services/            HTTP client
      scene/               Vehicle viewer, environments and 3D models
      data/                Reviewed vehicle reference manifest
      styles/              Interface and viewer styles
    public/                Product images and HDR environments
  api/
    src/                   Routes, validation, SQLite storage and static serving
packages/shared/
  src/
    catalog/               Parts, categories and component references
    vehicles/              Model index, aliases and conceptual visual profiles
    performance/           Shared performance calculations
    build.js               Build creation and part selection
    compatibility.js       Rules-based fitment checks
tests/                     Domain, geometry, persistence and HTTP tests
tests/browser/             Real browser journeys
```

The frontend uses Vite and Three.js. The backend uses Node's HTTP server and built-in SQLite. Domain calculations and stable part IDs are shared by the client and server; UI code does not live in the backend.

KuKirin G4 and Sur-Ron Light Bee X use Blender-authored GLB models as their default 3D view, with named component groups and the original product reference available beside it. Editable `.blend` files and reconstruction scripts are included; see [Blender vehicle sources](assets/blender/README.md). These are reference-based appearance models. Other vehicles retain their product references and conceptual geometry.

## Current coverage

- **345 indexed vehicle names** with brand, model and alias search.
- **60 reviewed vehicle references**, covering Sur-Ron, Talaria, Stark, Arctic Leopard, E Ride Pro, Altis, KuKirin, Ausom and Fiido. Exact references open by default. The remaining indexed names are still selectable with an explicit missing-image state.
- **315 planning catalog entries** across eight categories; **94 components have product imagery and distinct photo-guided 3D approximations**. The default catalog shows photographed products. Templates and supplier requests remain available in the complete catalog.
- Workshop and courtyard HDR environments, plus a neutral studio. Product references preserve original appearance; 3D concepts illustrate changes using approximate geometry. No procedural model is represented as measured manufacturer CAD.

An original product reference does **not** render your selected modifications. The parts list records those changes, and the separate 3D concept illustrates them. Images can show regional variants, accessories, graphics or factory renders; the manifest preserves those notes and sources. Unverified variants are listed in `apps/web/public/assets/vehicles/unresolved.json`.

## Saved builds

The old `voltforge-v1` browser record (`{ active, builds }`) is retained for migration. Builds save locally and sync through a serialized, revision-checked outbox. Local edits survive server outages; conflicting edits are preserved instead of silently overwriting newer data.

SQLite is stored in `data/voltforge.sqlite` by default. The server assigns an anonymous HttpOnly session cookie and stores its hash. That browser cookie identifies the private workspace; this version has no account login or cross-device account recovery. Clearing browser data can remove access to that workspace. Export important plans. Back up the database using a SQLite-aware backup or stop the server before copying the database and associated WAL files.

## Performance estimates

Speed, range, ride time and peak motor output distinguish measured inputs, factory references and modeled ceilings. Range is calculated at the selected riding speed using battery energy, drag, rolling load, mass, grade, wind and stops. Trip energy and distance can calibrate consumption.

The stock KuKirin G4 profile uses **one rear 2,000 W motor**, 60 V × 20 Ah (1,200 Wh), and a separately labeled factory reference. The owner's **90 km/h display reading is not treated as a GPS measurement**. Powertrain changes invalidate the stock baseline and previous measurements.

Selecting a motor, controller and battery now produces automatic speed and peak-power planning scenarios. Manufacturer ratings are recorded with sources in `packages/shared/src/catalog/performance-ratings.json`; ranges preserve winding and power variants. Unknown essential motor or pack ratings are requested directly below the results.

Automatic assumptions are visible in **Assumptions & quick inputs**: a pack without a known discharge rating uses a 2C continuous / up-to-3C burst scenario, loaded voltage is assumed at 90% of nominal, and a motor without a published peak uses a 1.5× rated-power burst scenario. Advertised motor watts with an unspecified measurement basis are treated as electrical input with the displayed efficiency assumption. These are editable modeling assumptions, not verified hardware ratings or recommended controller settings. A displayed range represents catalog variants, not a statistical confidence interval. Automatic values are recalculated from selected parts and never saved as measured inputs.

Peak output is bounded by motor peak output and loaded pack voltage × the lower of controller battery current or battery burst current × efficiency. Phase current is not battery current. GPS observations and entered ratings take priority; published controller maxima still bound the calculation. Partial information can produce a clearly labeled ceiling. Winding, gearing, temperature and actual configured limits can reduce achievable performance. These calculations do not certify fitment or road performance.

## API

All responses are JSON. Build routes are scoped to the session cookie.

| Method | Route                    | Purpose                                                             |
| ------ | ------------------------ | ------------------------------------------------------------------- |
| GET    | `/api/health`            | Health check                                                        |
| GET    | `/api/catalog`           | Shared parts and categories                                         |
| GET    | `/api/vehicles?q=&type=` | Alias-aware vehicle search                                          |
| POST   | `/api/performance`       | Estimate `{ build }`                                                |
| GET    | `/api/builds`            | List this session's builds                                          |
| PUT    | `/api/builds/:id`        | Save `{ build, expectedRevision }`; use 0 to create                 |
| POST   | `/api/builds/import`     | Idempotent import `{ builds }` without overwriting existing records |
| DELETE | `/api/builds/:id`        | Delete a stored build                                               |

Conflicting revisions return HTTP 409. Invalid build fields and unknown part/category combinations return HTTP 422; malformed requests return HTTP 400. Requests have body limits and same-origin checks.

## Verification

```sh
npm run check
npx playwright install chromium
npm run test:browser
```

`check` verifies formatting, Node tests and the production build. Browser tests require a compiled frontend (`npm run build` first). They start an isolated in-memory test server. To use an already installed Chrome instead of downloading Chromium:

```sh
PLAYWRIGHT_CHANNEL=chrome npm run test:browser
```

Browser journeys cover G4 rebuilding, search, component inspection, persistence, LBX peak power, real WebGL controls, missing references and mobile overflow. Screenshot and trace artifacts are written to ignored `test-results/`.

## Credits

Code retains the repository's MIT license. Third-party product imagery is credited separately and is not relicensed under MIT. See [ASSET_CREDITS.md](ASSET_CREDITS.md) and the reference manifests for original URLs, variant notes and environment licenses.
