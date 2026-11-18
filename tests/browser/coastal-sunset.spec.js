import { expect, test } from '@playwright/test';
import { createBuild } from '@voltforge/shared/build';

async function openBuild(page) {
  const build = { ...createBuild('scooter', 'Coastal G4'), mode: 'rebuild', vehicle: 'KuKirin G4' };
  await page.addInitScript((build) => {
    if (sessionStorage.getItem('coast-fixture')) return;
    sessionStorage.setItem('coast-fixture', 'yes');
    localStorage.setItem('voltforge-scene-environment', 'studio');
    localStorage.setItem('voltforge-v1', JSON.stringify({ active: build.id, builds: [build] }));
  }, build);
  await page.goto('/');
  await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'blender');
}

test('Coastal Sunset loads both parked models, supports inspection and remembers the setting', async ({
  page,
}) => {
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('console', (message) => {
    if (message.type() === 'error' && !message.location().url.endsWith('/favicon.ico'))
      errors.push(message.text());
  });
  await openBuild(page);
  const setting = page.locator('#sceneSetting');
  const scene = page.locator('#scene');
  const stage = page.locator('.stage');
  await setting.selectOption({ label: 'Coastal Sunset' });
  await expect(scene).toHaveAttribute('data-coast-state', 'ready');
  await expect(scene).toHaveAttribute('data-coast-vehicles', '2');
  await expect(page.locator('#sceneEnvironmentStatus')).toHaveText(
    'Coastal Sunset · 3D waterfront',
  );
  const assembled = await stage.screenshot({ path: 'test-results/coastal-sunset-desktop.png' });
  await scene.press('ArrowRight');
  await scene.press('ArrowRight');
  const rotated = await stage.screenshot({ path: 'test-results/coastal-sunset-orbit.png' });
  expect(rotated.equals(assembled)).toBe(false);
  await page.locator('#explode').click();
  await expect(scene).toHaveAttribute('data-explode-state', 'exploded');
  await stage.screenshot({ path: 'test-results/coastal-sunset-exploded.png' });
  await setting.selectOption('studio');
  await expect(scene).not.toHaveAttribute('data-coast-state');
  await expect(page.locator('#sceneEnvironmentStatus')).toHaveText('Studio');
  await setting.selectOption('coast');
  await expect(scene).toHaveAttribute('data-coast-state', 'ready');
  await page.reload();
  await expect(setting).toHaveValue('coast');
  await expect(scene).toHaveAttribute('data-coast-vehicles', '2');
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator('#resetView').click();
  await stage.screenshot({ path: 'test-results/coastal-sunset-mobile.png' });
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(390);
  expect(errors).toEqual([]);
});

test('a parked model load failure leaves the coast and active build usable', async ({ page }) => {
  await page.route('**/models/catalog/lightmoto/talaria-sting-r-mx4.glb', (route) =>
    route.abort('failed'),
  );
  await openBuild(page);
  await page.locator('#sceneSetting').selectOption('coast');
  await expect(page.locator('#scene')).toHaveAttribute('data-coast-state', 'partial');
  await expect(page.locator('#scene')).toHaveAttribute('data-coast-vehicles', '1');
  await expect(page.locator('#sceneEnvironmentStatus')).toHaveText(
    'Coastal Sunset · parked model unavailable',
  );
  await expect(page.locator('#estimatedSpeed')).toHaveText('70 km/h');
  await page.locator('#sceneSetting').selectOption('garage');
  await expect(page.locator('#scene')).not.toHaveAttribute('data-coast-state');
  await expect(page.locator('#scene')).toHaveAttribute('data-garage-state', 'ready');
});
