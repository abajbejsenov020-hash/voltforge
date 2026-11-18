import { test, expect } from '@playwright/test';
import { createBuild } from '@voltforge/shared/build';
import { CATALOG } from '@voltforge/shared/catalog';

function fixture(motor = 'p4') {
  return {
    ...createBuild('scooter', 'My completed G4'),
    id: 'completed-g4',
    mode: 'rebuild',
    vehicle: 'KuKirin G4',
    selected: {
      Motors: motor,
      Controllers: 'p37',
      Batteries: 'p46',
      Brakes: 'p293',
      Displays: 'p57',
      Accessories: 'p305',
      'Tires & wheels': 'p299',
      Suspension: 'p302',
    },
    performance: { schema: 2, rider: 80, vehicle: 41.5, cruise: 40 },
  };
}
async function seed(page, build) {
  await page.addInitScript((build) => {
    if (localStorage.getItem('automatic-test-seeded')) return;
    localStorage.setItem('automatic-test-seeded', 'yes');
    localStorage.setItem('voltforge-v1', JSON.stringify({ active: build.id, builds: [build] }));
  }, build);
  await page.goto('/');
  await expect(page.locator('#buildName')).toContainText(build.name);
}

test('the existing completed build shows speed and power automatically and survives reload', async ({
  page,
}) => {
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await seed(page, fixture());
  await expect(page.locator('#estimatedSpeed')).toHaveText(/≈\d+(?:–\d+)? km\/h/);
  await expect(page.locator('#estimatedPeak')).toHaveText(/≈\d+\.\d(?:–\d+\.\d)? kW/);
  await expect(page.locator('#speedMetricLabel')).toContainText('ROUGH ESTIMATE');
  await expect(page.locator('#peakMetricLabel')).toContainText('ROUGH ESTIMATE');
  await page.locator('#automaticPerformance summary').click();
  await expect(page.locator('.estimate-assumptions')).toContainText('2C');
  await expect(page.locator('.estimate-assumptions')).toContainText('180 A');
  await expect(page.locator('.estimate-sources a')).toHaveCount(3);
  const speed = await page.locator('#estimatedSpeed').textContent();
  const peak = await page.locator('#estimatedPeak').textContent();
  await page.locator('#quickPerformanceForm [name="bms"]').fill('20');
  await page.locator('#quickPerformanceForm [name="peakControllerA"]').fill('20');
  await page.locator('#quickPerformanceForm button').click();
  await expect(page.locator('#estimatedSpeed')).not.toHaveText(speed);
  await expect(page.locator('#estimatedPeak')).not.toHaveText(peak);
  await expect(page.locator('#estimatedPeak')).toHaveText('≈1.2 kW');
  await expect(page.locator('#saveStatus')).toContainText('Saved to your private workspace');
  await page.reload();
  await expect(page.locator('#estimatedPeak')).toHaveText('≈1.2 kW');
  const { builds } = await (await page.request.get('/api/builds')).json();
  expect(builds[0].performance.peakMotorW).toBe('');
  expect(builds[0].performance.peakVoltage).toBe('');
  await page.locator('#categorySelect').selectOption('Batteries');
  await page.locator('#appearanceFilter').selectOption('all');
  await page.locator('#search').fill('60V 30Ah');
  await page.locator('[data-add="p45"]').click();
  await expect(page.locator('#energy')).toContainText('1800');
  await expect(page.locator('#estimatedPeak')).not.toHaveText('≈1.2 kW');
  await expect(page.locator('#estimatedSpeed')).toContainText('≈');
  await page.locator('#reviewBuild').click();
  await expect(page.locator('#detailBody .peak-result')).toContainText(
    await page.locator('#estimatedPeak').textContent(),
  );
  expect(errors).toEqual([]);
});

test('an unknown motor requests one essential rating inline, then calculates without hidden setup', async ({
  page,
}) => {
  await seed(page, fixture('p73'));
  await expect(page.locator('#estimatedSpeed')).toHaveText('Not established');
  await page.locator('#addSpeedData').click();
  await expect(page.locator('#quickPerformanceForm [name="power"]')).toBeFocused();
  await expect(page.locator('#quickPerformanceForm')).toBeVisible();
  await expect(page.locator('#quickPerformanceForm [required]')).toHaveCount(1);
  await expect(page.locator('#quickPerformanceForm [name="power"]')).toHaveAttribute(
    'required',
    '',
  );
  await page.locator('#quickPerformanceForm [name="power"]').fill('1500');
  await page.locator('#quickPerformanceForm button').click();
  await expect(page.locator('#estimatedSpeed')).toHaveText(/≈\d+ km\/h/);
  await expect(page.locator('#estimatedPeak')).toHaveText('≈2.3 kW');
  await expect(page.locator('#quickPerformanceForm [required]')).toHaveCount(0);
});

test('XF Pro upgrade estimates, compatibility and missing peak data work from the performance panel', async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 812 });
  const build = fixture('p165');
  Object.assign(build, {
    type: 'bike',
    vehicle: 'Arctic Leopard XF Pro',
    name: 'XF Pro audit',
    performance: { schema: 2 },
  });
  Object.assign(build.selected, { Controllers: 'p151', Batteries: 'p181', Displays: 'p186' });
  await seed(page, build);
  await expect(page.locator('#estimatedSpeed')).toHaveText(/≈\d+ km\/h/);
  await expect(page.locator('#energy')).toContainText('3168');
  await expect(page.locator('#peakBasis')).toContainText('missing motor peak output');
  await expect(page.locator('#performanceConflictText')).toContainText('Nucular');
  await page.locator('.performance').scrollIntoViewIfNeeded();
  await page.screenshot({ path: 'test-results/xf-pro-performance-mobile.png' });
  await page.locator('#reviewPerformanceConflicts').click();
  const dialog = page.getByRole('dialog', { name: 'Your build, at a glance' });
  await expect(dialog.locator('#reviewConflicts')).toBeFocused();
  await expect(dialog.locator('.issue.conflict').first()).toContainText('different platforms');
  await dialog.locator('#specForm [name="bms"]').fill('75');
  await dialog.locator('#specForm button').click();
  await expect(dialog.locator('#specForm button')).toBeFocused();
  await expect(dialog.getByRole('button', { name: 'Close details' })).toBeInViewport();
  await dialog.getByRole('button', { name: 'Close details' }).click();
  await page.locator('#addPeakData').click();
  const peakField = page.locator('#quickPerformanceForm [name="peakMotorW"]');
  await expect(peakField).toBeFocused();
  await peakField.fill('12000');
  await page.locator('#quickPerformanceForm button').click();
  await expect(page.locator('#estimatedPeak')).toHaveText('≈12.0 kW');
  await page.reload();
  await expect(page.locator('#estimatedPeak')).toHaveText('≈12.0 kW');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test('e-moto results use selected parts and quick inputs fit a phone', async ({ page }) => {
  const build = fixture('p169');
  build.type = 'bike';
  build.vehicle = 'Sur-Ron Light Bee X';
  build.name = 'TORP Light Bee';
  build.selected.Controllers = CATALOG.find(
    (part) => part.brand === 'TORP' && part.name === 'TC500 2.0',
  ).id;
  await page.setViewportSize({ width: 390, height: 844 });
  await seed(page, build);
  await expect(page.locator('#estimatedSpeed')).toContainText('≈');
  await expect(page.locator('#estimatedPeak')).toContainText('≈');
  await page.locator('#automaticPerformance summary').click();
  await expect(page.locator('.estimate-sources')).toContainText('Manufacturer reference');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({ path: 'test-results/automatic-estimates-mobile.png', fullPage: false });
});
