import { createBuild, selectParts } from '@voltforge/shared/build';
import { resolveBuildParts } from '@voltforge/shared/stock';
import { checkCompatibility } from '@voltforge/shared/compatibility';
import { createPerformanceEngine } from '@voltforge/shared/performance';
import { createFeature as notifications } from '../features/notifications.js';
import { createFeature as catalog } from '../features/catalog.js';
import { createFeature as setup } from '../features/setup.js';
import { createFeature as review } from '../features/review.js';
import { createFeature as performance } from '../features/performance.js';
import { createFeature as workbench } from '../features/workbench.js';
import { bindEvents } from './events.js';

export function createWorkbench({ store, scene }) {
  const app = {
    get state() {
      return store.current;
    },
    set state(value) {
      store.current = value;
    },
    get builds() {
      return store.builds;
    },
    set builds(value) {
      store.builds = value;
    },
    isFirst: store.isFirst,
    scene,
    category: 'Motors',
    setupType: 'scooter',
    setupMode: 'rebuild',
    editMode: false,
    toastTimer: null,
    showAllVehicles: false,
    activeVehicleSuggestion: -1,
    blank: createBuild,
    selected: () => selectParts(store.current),
    effectiveParts: () => resolveBuildParts(store.current),
    checks: () => checkCompatibility(store.current),
    save: () => store.save(),
  };
  for (const name of [
    'performanceProfile',
    'performanceInputs',
    'invalidatePerformanceMeasurements',
    'estimatePerformance',
    'performanceExport',
  ]) {
    app[name] = (...args) => createPerformanceEngine(store.current)[name](...args);
  }
  for (const feature of [notifications, catalog, setup, review, performance, workbench])
    Object.assign(app, feature(app));
  bindEvents(app);
  return app;
}
