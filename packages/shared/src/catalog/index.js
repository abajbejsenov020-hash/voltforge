import parts from './parts.json' with { type: 'json' };
import categories from './categories.json' with { type: 'json' };
export const CATALOG = parts;
export const CATEGORIES = categories;
export const PART_BY_ID = new Map(CATALOG.map((part) => [part.id, part]));
