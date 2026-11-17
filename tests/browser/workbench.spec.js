import { test, expect } from '@playwright/test';

async function startModel(page, name) {
  await page.locator(`[data-featured="${name}"]`).click();
  await page.locator('#startBuild').click();
  await expect(page.locator('#startDialog')).not.toBeVisible();
  await expect(page.locator('#modelLabel')).toHaveText(name);
  await expect(page.locator('#vehiclePhoto')).toBeVisible();
  await expect
    .poll(() =>
      page.locator('#vehiclePhoto').evaluate((image) => image.complete && image.naturalWidth > 0),
    )
    .toBe(true);
}

test('rebuild G4, inspect a real controller, calculate scenarios and keep the saved build', async ({
  page,
}) => {
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.goto('/');
  await expect(page.locator('#startDialog')).toBeVisible();
  await expect(page.locator('#featuredModels > button')).toHaveCount(4);
  await startModel(page, 'KuKirin G4');
  await expect(page.locator('#scene')).toBeHidden();
  await expect(page.locator('#energy')).toContainText('1200');
  await expect(page.locator('#speedBasis')).toContainText('90');
  await page.locator('#rangeCruise').selectOption('80');
  await expect(page.locator('#rangeBasis')).toContainText('80 km/h');
  await page.locator('#referencePhoto').click();
  await expect(page.locator('#detailBody img')).toHaveAttribute('src', /kukirin-g4/);
  await page.locator('#closeDetail').click();
  await page.locator('#categorySelect').selectOption('Controllers');
  await page.locator('#vehicleFilter').selectOption('all');
  await page.locator('#search').fill('ND72260');
  await expect(page.locator('.part-card')).toHaveCount(1);
  await expect(page.locator('.component-real-photo')).toBeVisible();
  await page.locator('[data-detail]').click();
  await expect(page.locator('#detailTitle')).toContainText('ND72260');
  await page.locator('#detailAdd').click();
  await expect(page.locator('#partCount')).toContainText('1');
  await page.locator('#reviewBuild').click();
  await expect(page.locator('#detailBody')).toContainText('ND72260');
  await page.locator('#closeDetail').click();
  await expect(page.locator('#saveStatus')).toContainText('Saved to your private workspace');
  await page.reload();
  await expect(page.locator('#buildName')).toContainText('KuKirin G4');
  await expect(page.locator('#partCount')).toContainText('1');
  await expect(page.locator('#vehiclePhoto')).toBeVisible();
  const duplicateIds = await page.evaluate(() => {
    const ids = [...document.querySelectorAll('[id]')].map((element) => element.id);
    return ids.filter((id, index) => ids.indexOf(id) !== index);
  });
  expect(duplicateIds).toEqual([]);
  expect(errors).toEqual([]);
});

test('e-moto picker, alias finder, original LBX appearance and peak power', async ({ page }) => {
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.goto('/');
  await page.locator('[data-type="bike"]').click();
  for (const name of [
    'Sur-Ron Light Bee X',
    'Talaria Sting Pro MX5',
    'Stark Varg EX',
    'Arctic Leopard XE Pro S',
  ]) {
    await expect(page.locator(`[data-featured="${name}"]`)).toBeVisible();
  }
  await page.locator('#browseModelLibrary').click();
  await page.locator('#vehicleName').fill('surron lbx');
  await expect(page.locator('[data-vehicle="Sur-Ron Light Bee X"]')).toBeVisible();
  await page.locator('[data-vehicle="Sur-Ron Light Bee X"]').click();
  await page.locator('#startBuild').click();
  await expect(page.locator('#vehiclePhoto')).toHaveAttribute('src', /surron-light-bee-x/);
  await page.locator('#tunePerformance').click();
  const form = page.locator('#performanceForm');
  for (const [name, value] of Object.entries({
    peakMotorW: '15000',
    peakControllerA: '300',
    peakBatteryA: '200',
    peakVoltage: '70',
    peakEfficiency: '90',
  })) {
    await form.locator(`[name="${name}"]`).fill(value);
  }
  await form.locator('button[type="submit"]').click();
  await page.locator('#closeDetail').click();
  await expect(page.locator('#estimatedPeak')).toHaveText('≈12.6 kW');
  await expect(page.locator('#peakBasis')).toContainText('Battery burst-current');
  await page.locator('#sceneSetting').selectOption('courtyard');
  await expect(page.locator('.stage')).toHaveAttribute('data-environment', 'courtyard');
  await page.screenshot({ path: 'test-results/lbx-desktop.png', fullPage: true });
  expect(errors).toEqual([]);
});

test('3D concept and component controls render in a real WebGL browser', async ({ page }) => {
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.goto('/');
  await startModel(page, 'KuKirin G4');
  await page.locator('button[data-presentation="concept"]').click();
  await expect(page.locator('#scene')).toBeVisible();
  await expect(page.locator('#sceneEnvironmentStatus')).toHaveText('Workshop');
  await page.locator('[data-view="cockpit"]').click();
  await page.locator('#zoomIn').click();
  await page.locator('#resetView').click();
  await page.locator('#explode').click();
  await page.locator('#sceneSetting').selectOption('courtyard');
  await expect(page.locator('#sceneEnvironmentStatus')).toHaveText('Courtyard');
  await page.locator('#sceneSetting').selectOption('studio');
  await expect(page.locator('#sceneEnvironmentStatus')).toHaveText('Studio');
  await page.locator('#categorySelect').selectOption('Controllers');
  await page.locator('#vehicleFilter').selectOption('all');
  await page.locator('#search').fill('ND72260');
  await page.locator('#parts [data-part-view="model"]').click();
  await expect(page.locator('#parts .component-model-pane')).toBeVisible();
  await expect(page.locator('#parts .component-fallback')).not.toBeVisible();
  await page.locator('#parts [data-detail]').click();
  await page.locator('#detailBody [data-part-view="model"]').click();
  await page.locator('#detailBody [data-component-action="in"]').click();
  await page.locator('#detailBody [data-component-action="reset"]').click();
  await page.locator('#closeDetail').click();
  await page.screenshot({ path: 'test-results/g4-concept-desktop.png', fullPage: true });
  expect(errors).toEqual([]);
});

test('mobile model selection and real image stay within the viewport', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await startModel(page, 'KuKirin G4');
  await page.locator('#sceneSetting').selectOption('workshop');
  const widths = await page.evaluate(() => ({
    viewport: innerWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(widths.content).toBeLessThanOrEqual(widths.viewport);
  await expect(page.locator('#vehiclePhoto')).toBeVisible();
  await page.screenshot({ path: 'test-results/g4-mobile.png', fullPage: true });
});

test('full model index and custom builds keep missing references explicit', async ({ page }) => {
  await page.goto('/');
  await page.locator('#browseModelLibrary').click();
  await page.locator('#vehicleName').fill('Dualtron Thunder');
  await page.locator('#photoModelsOnly').uncheck();
  await expect(page.locator('#vehicleSuggestions')).toContainText('Dualtron Thunder');
  await page.locator('#vehicleName').fill('My measured prototype');
  await page.locator('#customVehicle').click();
  await expect(page.locator('#vehicleReferenceMissing')).toBeVisible();
  await expect(page.locator('#vehiclePhoto')).toBeHidden();
  await expect(page.locator('#modelLabel')).toHaveText('My measured prototype');
});

test('legacy local builds migrate to SQLite and remain usable after reload', async ({ page }) => {
  await page.addInitScript(() => {
    if (localStorage.getItem('migration-test-seeded')) return;
    localStorage.setItem('migration-test-seeded', 'yes');
    localStorage.setItem(
      'voltforge-v1',
      JSON.stringify({
        active: 'legacy-g4',
        builds: [
          {
            id: 'legacy-g4',
            type: 'scooter',
            mode: 'rebuild',
            name: 'My existing G4',
            vehicle: 'KuKirin G4',
            selected: {},
            specs: {
              dropout: '140',
              fullV: '67.2',
              bms: '40',
              batteryLimit: '35',
              motorCount: '1',
            },
            performance: { schema: 2, gpsSpeed: '68' },
            updated: 1700000000000,
          },
        ],
      }),
    );
  });
  await page.goto('/');
  await expect(page.locator('#buildName')).toContainText('My existing G4');
  await expect(page.locator('#startDialog')).not.toBeVisible();
  await expect(page.locator('#saveStatus')).toContainText('Saved to your private workspace');
  const response = await page.request.get('/api/builds');
  const { builds } = await response.json();
  expect(builds).toHaveLength(1);
  expect(builds[0]).toMatchObject({
    id: 'legacy-g4',
    specs: { fullV: '67.2' },
    performance: { gpsSpeed: '68' },
  });
  await page.reload();
  await expect(page.locator('#buildName')).toContainText('My existing G4');
  await expect(page.locator('#estimatedSpeed')).toContainText('68');
});

test('a second tab sees offline edits and the workspace syncs them on return', async ({
  page,
  context,
}) => {
  await page.goto('/');
  await startModel(page, 'KuKirin G4');
  await expect(page.locator('#saveStatus')).toContainText('Saved to your private workspace');
  const other = await context.newPage();
  await other.goto('/');
  await expect(other.locator('#buildName')).toContainText('KuKirin G4');
  await other.route('**/api/builds/**', (route) => route.abort('internetdisconnected'));
  await other.locator('#categorySelect').selectOption('Controllers');
  await other.locator('#vehicleFilter').selectOption('all');
  await other.locator('#search').fill('ND72260');
  await other.locator('[data-add]').click();
  await expect(other.locator('#partCount')).toContainText('1');
  await expect(page.locator('#partCount')).toContainText('1');
  await page.bringToFront();
  await expect(page.locator('#saveStatus')).toContainText('Saved to your private workspace');
  await other.close();
  await page.reload();
  await expect(page.locator('#partCount')).toContainText('1');
  await page.locator('#reviewBuild').click();
  await expect(page.locator('#detailBody')).toContainText('ND72260');
});
