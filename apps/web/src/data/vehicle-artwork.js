import established from './vehicle-references.json' with { type: 'json' };
import commuter from './vehicle-expansion-commuter.json' with { type: 'json' };
import premium from './vehicle-expansion-premium.json' with { type: 'json' };
import bikes from './vehicle-expansion-bikes.json' with { type: 'json' };

export const ARTWORK_BATCHES = [commuter, premium, bikes];
const entries = ARTWORK_BATCHES.flatMap((batch) => batch.entries || []);
// Incomplete exports never enter the viewer or acquire a completed-appearance badge.
const ready = entries
  .filter((entry) => entry.image && entry.model?.bytes > 0)
  .map((entry) =>
    entry.model.revision ? { ...entry, image: entry.image + '?v=' + entry.model.revision } : entry,
  );
export const VEHICLE_REFERENCES = [
  ...established,
  ...ready.map(({ model, factorySpecs, ...reference }) => reference),
];
export const EXPANDED_BLENDER_VEHICLES = ready.map((entry) => ({
  ...entry.model,
  name: entry.name,
  image: entry.image,
  source: entry.source,
  variantNote: entry.variantNote,
}));
export const VEHICLE_ARTWORK_AUDIT = ARTWORK_BATCHES.flatMap((batch) => batch.unresolved || []);
