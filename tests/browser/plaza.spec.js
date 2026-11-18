import { test, expect } from '@playwright/test';
import { createBuild } from '@voltforge/shared/build';

async function openPlaza(page) {
  const build = {
    ...createBuild('scooter', 'Night plaza'),
    mode: 'rebuild',
    vehicle: 'KuKirin G4',
  };
  await page.addInitScript((build) => {
    if (localStorage.getItem('plaza-seeded')) return;
    localStorage.setItem('plaza-seeded', 'yes');
    localStorage.setItem('voltforge-scene-environment', 'plaza');
    localStorage.setItem('voltforge-v1', JSON.stringify({ active: build.id, builds: [build] }));
  }, build);
  await page.goto('/');
  await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'blender');
}

test('city plaza loads actual parked vehicles, persists and supports close views on desktop and phone', async ({
  page,
}) => {
  test.setTimeout(90000);
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await openPlaza(page);
  await expect(page.locator('#sceneSetting')).toHaveValue('plaza');
  await expect(page.locator('#scene')).toHaveAttribute('data-plaza-state', 'ready', {
    timeout: 30000,
  });
  await expect(page.locator('#scene')).toHaveAttribute('data-plaza-vehicles', '2');
  await expect(page.locator('#sceneEnvironmentStatus')).toHaveText('City plaza · 3D night setting');
  await page.screenshot({ path: 'test-results/plaza-desktop.png' });
  await page.locator('[data-view="cockpit"]').click();
  await page.locator('#resetView').click();
  await page.locator('#explode').click();
  await page.locator('#explode').click();
  await page.locator('#scene').press('ArrowRight');
  await page.locator('#scene').press('ArrowRight');
  await page.screenshot({ path: 'test-results/plaza-rotated.png' });
  await page.locator('#sceneSetting').selectOption('garage');
  await expect(page.locator('#scene')).toHaveAttribute('data-garage-state', 'ready', {
    timeout: 30000,
  });
  await expect(page.locator('#scene')).not.toHaveAttribute('data-plaza-state');
  await page.locator('#sceneSetting').selectOption('plaza');
  await expect(page.locator('#scene')).toHaveAttribute('data-plaza-state', 'ready', {
    timeout: 30000,
  });
  await expect(page.locator('#scene')).not.toHaveAttribute('data-garage-state');
  await page.reload();
  await expect(page.locator('#sceneSetting')).toHaveValue('plaza');
  await expect(page.locator('#scene')).toHaveAttribute('data-plaza-vehicles', '2', {
    timeout: 30000,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator('#resetView').click();
  await page.screenshot({ path: 'test-results/plaza-mobile.png' });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  expect(errors).toEqual([]);
});

test('missing parked assets and failed HDR keep the physical plaza and build usable', async ({
  page,
}) => {
  test.setTimeout(60000);
  await page.route('**/models/expansion/premium/dualtron-thunder-3.glb', (route) =>
    route.abort('failed'),
  );
  await page.route('**/environments/courtyard_1k.hdr', (route) => route.abort('failed'));
  await openPlaza(page);
  await expect(page.locator('#scene')).toHaveAttribute('data-plaza-state', 'partial', {
    timeout: 30000,
  });
  await expect(page.locator('#scene')).toHaveAttribute('data-plaza-vehicles', '1');
  await expect(page.locator('#sceneEnvironmentStatus')).toHaveText(
    'City plaza · parked model unavailable',
  );
  await expect(page.locator('#estimatedSpeed')).toHaveText('70 km/h');
  await page.locator('#sceneSetting').selectOption('studio');
  await expect(page.locator('#sceneEnvironmentStatus')).toHaveText('Studio');
  await expect(page.locator('#scene')).not.toHaveAttribute('data-plaza-state');
  await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'blender');
});
