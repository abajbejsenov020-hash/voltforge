# Stock vehicle profiles

Checked 2026-11-17 against manufacturer product pages and official distributor technical pages. The catalog contains all 60 exact names from `apps/web/src/data/vehicle-references.json`; 57 have at least one verified numeric field. All fields known: 9. Metadata-only: Talaria XXX, Talaria XXX MX and Talaria Junior ET01. This is a curated specification set, not independent vehicle testing or an exhaustive historical variant database.

`packages/shared/src/vehicles/stock-profiles.json` is the source of truth. Each entry links its technical source and records its selected variant, conditions and unresolved conflicts. `sources` adds supporting URLs where needed. A null means unknown or unresolved, never zero. Original photo provenance stays in the reference catalog; a product image cannot establish battery year or hidden powertrain specifications.

## Units and interpretation

- `nominal`: battery/powertrain nominal volts; `ah`: explicitly published pack Ah; `vehicleMass`: kg, battery included where stated. Packaging weight and rider load are excluded.
- `ratedMotorW`: rated/nominal watts **per motor**. `peakMotorW`: published maximum/peak watts **for the whole vehicle**. Unqualified marketing watts are not silently labelled rated. Dual-motor peaks are summed only when the source explicitly gives per-motor peaks.
- `wheel`: driven tire nominal outside diameter in inches. Scooter tire-size designations and explicit e-bike OD values are nominal; Fiido M1 Pro 20x4 is left unknown because actual fat-tire OD is not established. Motorcycle rear OD is geometrically calculated only when tire width, aspect ratio and rim size are published: `rim_inches + 2 * width_mm * aspect_percent / 100 / 25.4`. These are not measured loaded rolling diameters. Rim-only sizes and unverified inch tire aspect ratios remain null.
- Optional `energyWh` records explicitly published pack Wh (or kWh multiplied by 1000), independently of Ah. It is present for 24 entries. No Ah is inferred from energy or voltage. When energy and V/Ah disagree (E Ride Pro Mini R), the energy field is absent pending correction.
- Speed is an advertised km/h claim, not GPS measurement. Range is advertised km under the entry's specified conditions; pedal-assisted bicycle range is not throttle-only range. Miles and mph use 1.609344; pounds use 0.45359237; Stark mechanical hp uses 745.699872 W/hp. Converted values are rounded.
- No battery-side controller/BMS current ratings were established. None are invented from motor watts, charger amps or phase-current claims. Wh/kWh is not substituted for Ah. Do not present a simulator's inferred values as source-backed manufacturer specifications.

## Decisions and limits

G4 preserves the factory 60 V, 20 Ah, 41.5 kg, 2000 W rated, 2400 W peak, 11-inch tire, 70 km/h and 75 km baseline, with 65 kg reference load. A user's 90 km/h display report does not modify this baseline. [Factory table](https://www.kukirinfactory.com/kukirin-g4-specification).

K20 Pro/Laluz 2 Pro and Talaria Komodo/Komodo MX, Sting Pro MX5/Sting Pro share documented source pages; their duplicate catalog names are intentional. Different road versions retain their own specifications.

Conflicts are preserved in notes: Sting R speed; Sur-Ron Storm battery/mass; Hyper Bee and PRO-S mass/speed; Ausom DT2 speed and L2 peak; G2 capacity/speed; several Arctic metric/imperial masses; Altis Omega US/UK and Sigma battery variants. Current xXx Pro data is deliberately not assigned to the older xXx MX photo. ET01's combined Premium/Basic page has malformed or ambiguous technical labels. Stark, Fiido and Altis Omega battery capacity is retained directly in `energyWh`; Ah remains unknown where unpublished.

## Coverage

| Field                 | Entries known / 60 |
| --------------------- | -----------------: |
| `nominal`             |                 55 |
| `ah`                  |                 45 |
| `vehicleMass`         |                 46 |
| `motors`              |                 57 |
| `ratedMotorW`         |                 25 |
| `peakMotorW`          |                 44 |
| `wheel`               |                 43 |
| `advertisedSpeed`     |                 46 |
| `advertisedRange`     |                 48 |
| `energyWh` (optional) |                 24 |

## Per-model evidence and gaps

The JSON notes contain the exact variant and interpretation. Missing fields below remain null.

| Model / primary technical source                                                                            | Unknown fields                                                                                     |
| ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| [Sur-Ron Light Bee X](https://sur-ron.co.uk/light-bee-x/)                                                   | ratedMotorW, wheel                                                                                 |
| [KuKirin G4](https://www.kukirinfactory.com/kukirin-g4-specification)                                       | None                                                                                               |
| [Talaria Sting R MX4](https://www.talaria.cn/html/115.html)                                                 | advertisedSpeed                                                                                    |
| [Talaria Sting Pro MX5](https://www.talaria.cn/html/117.html)                                               | None                                                                                               |
| [Talaria Komodo](https://www.talaria.cn/html/113.html)                                                      | None                                                                                               |
| [Stark Varg MX](https://starkfuture.com/products/stark-varg-1)                                              | ah, ratedMotorW, wheel, advertisedSpeed, advertisedRange                                           |
| [Stark Varg MX 1.2](https://starkfuture.com/products/stark-varg)                                            | ah, ratedMotorW, wheel, advertisedSpeed, advertisedRange                                           |
| [Stark Varg EX](https://starkfuture.com/products/stark-varg-ex)                                             | ah, ratedMotorW, wheel, advertisedSpeed, advertisedRange                                           |
| [Stark Varg SM](https://starkfuture.com/products/stark-varg-sm)                                             | ah, ratedMotorW, wheel, advertisedSpeed                                                            |
| [Arctic Leopard XF Pro](https://arctic-leopard.com/produit/xf-pro/)                                         | vehicleMass, ratedMotorW                                                                           |
| [Arctic Leopard XE Pro R](https://arctic-leopard.com/produit/xe-pro-r/)                                     | ratedMotorW, peakMotorW                                                                            |
| [Arctic Leopard XE Pro S](https://arctic-leopard.com/produit/xe-pro-s/)                                     | ratedMotorW                                                                                        |
| [Arctic Leopard E-XE 880 Enduro](https://arctic-leopard.com/produit/e%C2%B7xe880/)                          | ratedMotorW                                                                                        |
| [E Ride Pro SS 2.0](https://www.eridepro.com/products/pro-ss-2-0)                                           | wheel                                                                                              |
| [E Ride Pro SS 3.0](https://www.eridepro.com/products/pro-ss-3-0-off-road-fatty)                            | wheel                                                                                              |
| [E Ride Pro SR](https://www.eridepro.com/products/pro-sr)                                                   | wheel                                                                                              |
| [Sur-Ron Ultra Bee](https://sur-ron.co.uk/ultra-bee/)                                                       | ratedMotorW                                                                                        |
| [Sur-Ron Storm Bee](https://sur-ron.co.uk/storm-bee/)                                                       | nominal, ah, vehicleMass, ratedMotorW                                                              |
| [Sur-Ron Hyper Bee](https://sur-ron.co.uk/hyper-bee/)                                                       | vehicleMass, ratedMotorW                                                                           |
| [Talaria XXX](https://www.talaria.cn/html/750.html)                                                         | nominal, ah, vehicleMass, motors, ratedMotorW, peakMotorW, wheel, advertisedSpeed, advertisedRange |
| [Altis Sigma MX](https://www.altispowersports.com/products/altis-sigma)                                     | nominal, ah, vehicleMass, ratedMotorW, advertisedRange                                             |
| [KuKirin G2 Max](https://kukirin-escooter.com/products/kukirin-g2-max-electric-scooter-adults)              | peakMotorW                                                                                         |
| [KuKirin G2 Master](https://kukirin-escooter.com/products/kukirin-g2-master-electric-scooter-for-adults)    | peakMotorW                                                                                         |
| [Ausom DT2 Pro](https://ausomstore.com/products/ausom-dt2-pro-e-scooter)                                    | ratedMotorW, advertisedSpeed                                                                       |
| [Ausom L2 Max Dual Motor](https://ausomstore.com/products/ausom-l2-max-dual-electric-scooter)               | ratedMotorW, peakMotorW                                                                            |
| [Fiido M1 Pro](https://fiido.com/products/fiido-m1-pro-fat-tire-electric-bike)                              | ah, peakMotorW, wheel                                                                              |
| [Fiido C11](https://fiido.com/products/fiido-c11-electric-commuter-bike)                                    | ah, ratedMotorW, peakMotorW                                                                        |
| [Arctic Leopard XF Pro MX](https://arctic-leopard.com/produit/xf-pro-mx/)                                   | vehicleMass, ratedMotorW                                                                           |
| [Arctic Leopard XF Pro Super](https://arctic-leopard.com/produit/xf-pro-super/)                             | vehicleMass, ratedMotorW                                                                           |
| [Arctic Leopard XE Pro S Enduro](https://arctic-leopard.com/produit/xe-pro-s-enduro/)                       | ratedMotorW, advertisedRange                                                                       |
| [Arctic Leopard XE L1E](https://arctic-leopard.com/produit/xe-l1e-b/)                                       | ratedMotorW, peakMotorW                                                                            |
| [Arctic Leopard E-XE 880 Super](https://arctic-leopard.com/produit/e%C2%B7xe-880-super/)                    | ratedMotorW                                                                                        |
| [Arctic Leopard E-XE 800 Enduro](https://arctic-leopard.com/produit/e%C2%B7xe800-enduro/)                   | ratedMotorW                                                                                        |
| [Arctic Leopard E-XE L3E](https://arctic-leopard.com/produit/e%C2%B7xe-l3e/)                                | ratedMotorW                                                                                        |
| [Talaria Komodo L3E](https://www.talaria.cn/html/147.html)                                                  | vehicleMass                                                                                        |
| [Talaria Sting Pro L1E](https://www.talaria.cn/html/116.html)                                               | None                                                                                               |
| [Talaria Junior ET01](https://www.talaria.cn/html/1175.html)                                                | nominal, ah, vehicleMass, motors, ratedMotorW, peakMotorW, wheel, advertisedSpeed, advertisedRange |
| [E Ride Pro S](https://www.eridepro.com/products/pro-s)                                                     | vehicleMass, wheel, advertisedSpeed                                                                |
| [E Ride Pro 4.0](https://www.eridepro.com/products/pro-4-0)                                                 | wheel                                                                                              |
| [E Ride Pro Mini R](https://www.eridepro.com/products/mini-r)                                               | None                                                                                               |
| [Altis Delta x DBK](https://www.altispowersports.com/products/altis-delta-dbk)                              | vehicleMass, ratedMotorW, wheel, advertisedRange                                                   |
| [Altis Omega](https://www.altispowersports.com/products/altis-omega)                                        | ah, vehicleMass, ratedMotorW, advertisedSpeed, advertisedRange                                     |
| [KuKirin G2](https://kukirin-escooter.com/products/kukirinkugoo-kirin-2024-g2-electric-scooter)             | ah, peakMotorW, advertisedSpeed                                                                    |
| [KuKirin G4 Ultra](https://kukirin-escooter.com/products/kukirin-g4-ultra-electric-scooter)                 | None                                                                                               |
| [KuKirin M4 Max](https://kukirin-escooter.com/products/kukirinkugoo-kirin-m4-max-electric-scooter)          | peakMotorW                                                                                         |
| [KuKirin T4](https://kukirin-escooter.com/products/kukirin-t4-electric-scooter)                             | None                                                                                               |
| [KuKirin G2 Pro ABE](https://kukirin-escooter.com/products/kukirin-g2-pro-electric-scooter-abe-certified)   | vehicleMass, peakMotorW                                                                            |
| [KuKirin G3 Pro](https://kukirin-escooter.com/products/kukirin-g3-pro-off-road-electric-scooter)            | peakMotorW                                                                                         |
| [KuKirin G2 Pro VMP](https://kukirin-escooter.com/products/kukirin-kugoo-kirin-g2-pro-electric-scooter-dgt) | peakMotorW                                                                                         |
| [KuKirin G2 Pro](https://kukirin-escooter.com/products/kukirin-g2-pro-electric-scooter-with-seat)           | peakMotorW                                                                                         |
| [Ausom Gosoul 2 Pro Dual Motor](https://ausomstore.com/products/ausom-gosoul-2-pro-dual-motor-e-scooter)    | ratedMotorW                                                                                        |
| [Ausom K20 Pro Dual Motor](https://ausomstore.com/products/ausom-k20-pro-dual-motor-e-scooter)              | ratedMotorW                                                                                        |
| [Ausom Laluz 2 Pro Dual Motor](https://ausomstore.com/products/ausom-k20-pro-dual-motor-e-scooter)          | ratedMotorW                                                                                        |
| [Ausom F1 Max](https://ausomstore.com/products/ausom-f1-max-electric-scooter)                               | ratedMotorW                                                                                        |
| [Ausom Gosoul 2](https://ausomstore.com/products/ausom-gosoul-2-electric-scooter)                           | ratedMotorW                                                                                        |
| [Talaria Komodo MX](https://www.talaria.cn/html/113.html)                                                   | None                                                                                               |
| [Talaria XXX MX](https://www.talaria.cn/html/750.html)                                                      | nominal, ah, vehicleMass, motors, ratedMotorW, peakMotorW, wheel, advertisedSpeed, advertisedRange |
| [Talaria Sting Pro](https://www.talaria.cn/html/117.html)                                                   | None                                                                                               |
| [Stark Varg SM Skoll](https://starkfuture.com/products/varg-sm-skoll)                                       | ah, ratedMotorW, wheel, advertisedSpeed, advertisedRange                                           |
| [Stark Varg Factory Edition](https://starkfuture.com/products/varg-factory)                                 | ah, ratedMotorW, wheel, advertisedSpeed, advertisedRange                                           |

## Checks performed

Parsed JSON; confirmed 60 unique names exactly match the reference catalog; checked required numeric values are positive or null, every entry has source and note, no unverified current fields exist, published energy is positive and independent of Ah, and G4 matches the agreed factory baseline. This validates data shape and the captured evidence, not real-world performance. Future catalog maintenance should resolve exact regional/model-year gaps with serial-specific manuals or manufacturer confirmation.
