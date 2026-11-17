# Vehicle appearance and speed comparison verification

Final checks on 17 November 2026:

- Complete source/asset gate: 345 indexed names, 341 completed photo/Blender entries, 281 added entries, four documented unresolved variants, zero pending audits.
- `npm run check`: formatting passed, all 430 Node tests passed, production Vite build passed.
- Chrome Playwright: all 12 affected journeys passed in 3.1 minutes. Covered 32 newly modeled vehicles across all three batches, decoded exact preview photos, 3D loading/controls, persisted selection, visible trim notes, unresolved original identity, automatic performance, stronger-motor comparison, entered supply restrictions, factory-part restoration and mobile garage controls.
- Independent Blender reopens: all 281 new native sources and exports passed their batch audits. Final photo/render comparison sheets were inspected, including targeted frame, suspension, wheel-cover, cast-wheel and exact-generation corrections.
- Source identity review corrected EP-2 Pro/Boost, original T1/T1 Pro and original Lectric generation mixups before publication. Unverified base Hiley and legacy scooter variants retain explicit reasons rather than substituted appearances.

The speed regression was reproduced before the correction: stock G4 reference 70 km/h versus approximately 54 km/h for a stronger motor when the calculator switched to an unrelated generic drag scenario. The revised comparison uses the same documented factory-relative basis. Narrow regression cases also verify weaker motors, low entered current, RPM limits, wind/load, GPS precedence, manual-current provenance on both stock and modified hardware, and unchanged saved inputs. A source reference and assumed current limits do not establish exact achievable speed or dyno power.

Geometry remains a photo-guided appearance reconstruction with approximate dimensions and hidden details. Four catalog variants still lack an accepted exact appearance reference: Ausom DT1, original Joyor S10-S, Hiley Tiger 8 and Hiley Tiger 9. Full reasons and checked URLs are in `apps/web/public/assets/vehicles/unresolved.json`.
