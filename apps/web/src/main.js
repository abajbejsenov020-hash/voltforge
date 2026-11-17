import './styles/app.css';
import './styles/vehicle-viewer.css';
import './styles/performance.css';
import { createApiClient } from './services/api.js';
import { BuildStore, BUILD_RECORD_PREFIX } from './state/build-store.js';
import { createVehicleScene } from './scene/vehicle-scene.js';
import { createWorkbench } from './app/controller.js';
import { createVehicleViewer } from './scene/vehicle-viewer.js';

const status = document.querySelector('#saveStatus');
const store = new BuildStore({
  api: createApiClient(),
  onStatus: ({ label }) => {
    status.textContent = label;
  },
});
status.textContent = 'Opening your workspace…';
await store.initialize();
const viewer = createVehicleViewer({ sceneFactory: createVehicleScene });
const app = createWorkbench({ store, scene: viewer });
window.addEventListener('online', async () => {
  await store.initialize();
  app.render();
});
window.addEventListener('pagehide', () => store.persist());
window.addEventListener('storage', (event) => {
  if (event.key === 'voltforge-v1' || event.key?.startsWith(BUILD_RECORD_PREFIX)) {
    store.refreshFromStorage();
    app.render();
  }
});
document.addEventListener('visibilitychange', async () => {
  if (document.visibilityState === 'visible') {
    await store.initialize();
    app.render();
  }
});
