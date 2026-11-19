import './styles/app.css';
import './styles/vehicle-viewer.css';
import './styles/performance.css';
import './styles/account.css';
import { createApiClient } from './services/api.js';
import { BuildStore } from './state/build-store.js';
import { ACCOUNT_CHANGE_KEY, bindAccount, loadAccountSession } from './features/account.js';
import { createVehicleScene } from './scene/vehicle-scene.js';
import { createWorkbench } from './app/controller.js';
import { createVehicleViewer } from './scene/vehicle-viewer.js';
import { PartPreviews } from './scene/components/index.js';
import { bindRenderPreferences } from './ui/render-preferences.js';

const status = document.querySelector('#saveStatus');
status.textContent = 'Opening your workspace…';
const session = await loadAccountSession(createApiClient());
const accountId = session?.user?.id;
const api = createApiClient(undefined, { accountId });
const canSync = Boolean(session && (!session.enabled || accountId));
const store = new BuildStore({
  accountId,
  api: canSync ? api : undefined,
  onStatus: ({ label }) => {
    status.textContent = label;
  },
});
await store.initialize();
if (!canSync) status.textContent = 'Saved on this device';
const viewer = createVehicleViewer({
  sceneFactory: createVehicleScene,
  onPaintChange(paint) {
    store.current.paint = paint;
    store.save();
  },
  onCockpitChange(cockpit) {
    if (Object.keys(cockpit).length) store.current.cockpit = cockpit;
    else delete store.current.cockpit;
    store.save();
  },
});
bindRenderPreferences((preferences) => {
  viewer.setRenderPreferences(preferences);
  PartPreviews.setRenderPreferences(preferences);
});
const app = createWorkbench({ store, scene: viewer });
bindAccount({
  api,
  session,
  readDrafts: () => new BuildStore({ storage: store.storage }).builds,
  onImport: async () => {
    await store.initialize();
    app.render();
  },
});

async function resumeWorkspace() {
  const latest = await loadAccountSession(api);
  if (!latest) return;
  if (
    latest.enabled !== session?.enabled ||
    latest.user?.id !== accountId ||
    Boolean(latest.recovering) !== Boolean(session.recovering)
  ) {
    location.reload();
    return;
  }
  await store.initialize();
  app.render();
}
window.addEventListener('online', resumeWorkspace);
window.addEventListener('pagehide', () => store.persist());
window.addEventListener('storage', (event) => {
  if (event.key === ACCOUNT_CHANGE_KEY) {
    void resumeWorkspace();
  } else if (store.handlesStorageKey(event.key)) {
    store.refreshFromStorage();
    app.render();
  }
});
document.addEventListener('visibilitychange', async () => {
  if (document.visibilityState === 'visible') await resumeWorkspace();
});
