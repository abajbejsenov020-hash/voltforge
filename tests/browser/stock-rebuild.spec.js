import { test, expect } from '@playwright/test';
import { createBuild } from '@voltforge/shared/build';

async function seed(page, build) {
  await page.addInitScript((build) => {
    if (localStorage.getItem('stock-test-seeded')) return;
    localStorage.setItem('stock-test-seeded', 'yes');
    localStorage.setItem('voltforge-v1', JSON.stringify({ active: build.id, builds: [build] }));
  }, build);
  await page.goto('/');
  await expect(page.locator('#buildName')).toContainText(build.name);
}
async function choosePart(page, category, id, search) {
  await page.locator('#categorySelect').selectOption(category);
  await page.locator('#appearanceFilter').selectOption('all');
  await page.locator('#vehicleFilter').selectOption('all');
  await page.locator('#search').fill(search);
  await page.locator(`[data-add="${id}"]`).click();
}
const rebuild = (vehicle = 'KuKirin G4', type = 'scooter') => ({
  ...createBuild(type, vehicle + ' test rebuild'),
  mode: 'rebuild',
  vehicle,
});

test('a G4 OEM motor and controller upgrade retain factory hardware, produce estimates and restore stock', async ({
  page,
}) => {
  test.setTimeout(90000);
  await seed(page, rebuild());
  await expect(page.locator('#estimatedSpeed')).toHaveText('70 km/h');
  await expect(page.locator('#partCount')).toContainText('8 stock');
  await choosePart(page, 'Motors', 'p72', 'G4 Hub Motor');
  await expect(page.locator('#estimatedSpeed')).toHaveText('70 km/h');
  await expect(page.locator('#estimatedPeak')).toHaveText('2.4 kW');
  await expect(page.locator('#stockHardwareNote')).toContainText('Stock: controller, battery');
  await expect(page.locator('#energy')).toContainText('1200');
  await expect(page.locator('#stockHardwareNote')).toContainText(
    'Factory-equivalent replacement: motor',
  );
  await page.screenshot({
    path: 'test-results/g4-factory-replacement-performance.png',
    fullPage: true,
  });
  await choosePart(page, 'Controllers', 'p291', 'ND72260');
  await expect(page.locator('#estimatedSpeed')).toHaveText(/≈\d/);
  await page.reload();
  await expect(page.locator('#estimatedSpeed')).toHaveText(/≈\d/);
  await expect(page.locator('#partCount')).toContainText('2');
  await page.locator('#reviewBuild').click();
  await expect(page.locator('#detailBody')).toContainText('Stock · KuKirin G4 factory batteries');
  await page.locator('#closeDetail').click();
  await page.locator('#stockBaselineBtn').click();
  await expect(page.locator('#estimatedSpeed')).toHaveText('70 km/h');
  await expect(page.locator('#estimatedPeak')).toHaveText('2.4 kW');
  await expect(page.locator('#partCount')).toContainText('8 stock');
  await expect(page.locator('#saveStatus')).toContainText('Saved');
  const { builds } = await (await page.request.get('/api/builds')).json();
  expect(builds[0].selected).toEqual({});
  expect(builds[0].performance).not.toHaveProperty('vehicle');
  expect(builds[0].performance).not.toHaveProperty('wheel');
});

test('returning an individual battery to stock clears old pack overrides and cruise never persists factory defaults', async ({
  page,
}) => {
  await seed(page, {
    ...rebuild(),
    selected: { Batteries: 'p46' },
    specs: { motorCount: 1, fullV: 84, bms: 100 },
    performance: { schema: 2, nominalVoltage: 72, capacityAh: 40 },
  });
  await page.locator('#categorySelect').selectOption('Batteries');
  await page.locator('#returnToStock').click();
  await expect(page.locator('#energy')).toContainText('1200');
  await expect(page.locator('#estimatedSpeed')).toHaveText('70 km/h');
  await page.locator('#rangeCruise').selectOption('60');
  await expect(page.locator('#saveStatus')).toContainText('Saved');
  const { builds } = await (await page.request.get('/api/builds')).json();
  expect(builds[0].performance.nominalVoltage).toBe('');
  expect(builds[0].performance.capacityAh).toBe('');
  expect(builds[0].performance).not.toHaveProperty('vehicle');
  expect(builds[0].performance).not.toHaveProperty('wheel');
  expect(builds[0].specs.bms).toBe('');
});

test('legacy dual-motor conversions clear observations and unknown wheel diameter does not block saving', async ({
  page,
}) => {
  await seed(page, {
    ...rebuild('KuKirin G2 Master'),
    specs: { motorCount: 1 },
    performance: { schema: 2, gpsSpeed: 80, tripKm: 30, tripUsedWh: 900, tripSpeed: 40 },
  });
  await page.locator('#reviewBuild').click();
  await expect(page.locator('#specForm [name="motorCount"]')).toHaveValue('2');
  await page.locator('#specForm [name="motorCount"]').selectOption('1');
  await page.locator('#specForm button').click();
  await page.locator('#closeDetail').click();
  await expect(page.locator('#estimatedSpeed')).not.toHaveText('80 km/h');
  const { builds } = await (await page.request.get('/api/builds')).json();
  expect(Number(builds[0].specs.motorCountOverride)).toBe(1);
  expect(builds[0].performance.gpsSpeed).toBe('');
  expect(builds[0].performance.tripKm).toBe('');
  await page.locator('#newBuild').click();
  await page.locator('[data-type="bike"]').click();
  await page.locator('[data-featured="Sur-Ron Light Bee X"]').click();
  await page.locator('#startBuild').click();
  await page.locator('#tunePerformance').click();
  await expect(page.locator('#performanceForm [name="wheel"]')).toHaveValue('');
  await page.locator('#performanceForm [name="gpsSpeed"]').fill('72');
  expect(await page.locator('#performanceForm').evaluate((form) => form.checkValidity())).toBe(
    true,
  );
  await page.locator('#performanceForm button').click();
  await expect(page.locator('#detailBody')).toContainText('72 km/h');
});

test('the default garage has two actual parked Blender vehicles and works on a phone', async ({
  page,
}) => {
  test.setTimeout(90000);
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await seed(page, rebuild());
  await expect(page.locator('#sceneSetting')).toHaveValue('garage');
  await expect(page.locator('#scene')).toHaveAttribute('data-garage-state', 'ready', {
    timeout: 30000,
  });
  await expect(page.locator('#scene')).toHaveAttribute('data-garage-vehicles', '2');
  await page.screenshot({ path: 'test-results/stock-garage-desktop.png' });
  await page.locator('#sceneSetting').selectOption('studio');
  await expect(page.locator('#sceneEnvironmentStatus')).toHaveText('Studio');
  await page.reload();
  await expect(page.locator('#sceneSetting')).toHaveValue('studio');
  await page.locator('#sceneSetting').selectOption('garage');
  await expect(page.locator('#scene')).toHaveAttribute('data-garage-vehicles', '2', {
    timeout: 30000,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator('#scene').press('ArrowRight');
  await page.locator('#zoomIn').click();
  await page.locator('#resetView').click();
  await page.screenshot({ path: 'test-results/stock-garage-mobile.png' });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect(errors).toEqual([]);
});
