import { test, expect } from '@playwright/test';

async function choose(page, brand, name, type) {
  if ((await page.locator('#startDialog').isVisible()) === false)
    await page.locator('#newBuild').click();
  await page.locator(`[data-type="${type}"]`).click();
  await page.locator(`[data-featured-brand="${brand}"]`).click();
  await page.locator(`[data-vehicle="${name}"]`).click();
  await page.locator('#startBuild').click();
  await expect(page.locator('#modelLabel')).toHaveText(name);
  await expect(page.locator('#scene')).toBeVisible();
  await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'blender', {
    timeout: 20000,
  });
  await expect(page.locator('#scene')).toHaveAttribute('data-model-state', 'ready');
}

test('Blender G4 and LBX assets load as the default 3D view and preserve inspection controls', async ({
  page,
}) => {
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  await page.goto('/');
  await choose(page, 'KuKirin', 'KuKirin G4', 'scooter');
  await page.locator('#sceneSetting').selectOption('studio');
  await expect(page.locator('#sceneEnvironmentStatus')).toHaveText('Studio');
  await page.screenshot({ path: 'test-results/blender-g4-browser.png', fullPage: false });
  await page.locator('[data-view="cockpit"]').click();
  await page.locator('#zoomIn').click();
  await page.locator('#resetView').click();
  await page.locator('#explode').click();
  await page.locator('#explode').click();
  await page.locator('button[data-presentation="photo"]').click();
  await expect(page.locator('#vehiclePhoto')).toBeVisible();
  await page.locator('button[data-presentation="concept"]').click();
  await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'blender');
  await choose(page, 'Sur-Ron', 'Sur-Ron Light Bee X', 'bike');
  await page.locator('#sceneSetting').selectOption('studio');
  await page.screenshot({ path: 'test-results/blender-lbx-browser.png', fullPage: false });
  await page.locator('[data-view="drivetrain"]').click();
  await page.locator('#resetView').click();
  await page.reload();
  await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'blender', {
    timeout: 20000,
  });
  expect(errors).toEqual([]);
});

test('Blender model remains interactive and contained on a phone', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await choose(page, 'KuKirin', 'KuKirin G4', 'scooter');
  await page.locator('#sceneSetting').selectOption('studio');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.locator('#zoomIn').click();
  await page.locator('#resetView').click();
  await page.screenshot({ path: 'test-results/blender-g4-mobile.png', fullPage: false });
});

test('native full screen keeps the vehicle, settings and camera controls together', async ({
  page,
}) => {
  await page.goto('/');
  await choose(page, 'KuKirin', 'KuKirin G4', 'scooter');
  const fullscreen = page.locator('#sceneFullscreen');
  await fullscreen.click();
  await expect(fullscreen).toHaveAccessibleName('Exit full screen');
  await expect(page.locator('.stage:fullscreen')).toHaveCount(1);
  expect(await page.locator('.stage').evaluate((stage) => stage.clientWidth === innerWidth)).toBe(
    true,
  );
  await expect(page.locator('#scene')).toBeVisible();
  await page.locator('#zoomIn').click();
  await page.locator('#rotate').click();
  await expect(page.locator('#rotate')).toHaveAttribute('aria-pressed', 'true');
  await page.locator('#sceneSetting').selectOption('studio');
  await expect(page.locator('#sceneEnvironmentStatus')).toHaveText('Studio');
  await fullscreen.click();
  await expect(fullscreen).toHaveAccessibleName('Full screen');
  await expect(page.locator('.stage:fullscreen')).toHaveCount(0);
  await expect(page.locator('#sceneSetting')).toHaveValue('studio');
  await expect(page.locator('#estimatedSpeed')).toHaveText('70 km/h');
  await fullscreen.click();
  await expect(fullscreen).toHaveAccessibleName('Exit full screen');
  await page.keyboard.press('Escape');
  await expect(fullscreen).toHaveAccessibleName('Full screen');
});

test('removed background preferences fall back to Garage and the viewer can expand when native full screen is denied', async ({
  page,
}) => {
  const key = 'voltforge-scene-environment';
  await page.setViewportSize({ width: 320, height: 720 });
  await page.addInitScript((key) => {
    if (localStorage.getItem(key) === null) localStorage.setItem(key, 'workshop');
    Element.prototype.requestFullscreen = () => Promise.reject(new DOMException('Denied'));
  }, key);
  await page.goto('/');
  await choose(page, 'KuKirin', 'KuKirin G4', 'scooter');
  const setting = page.locator('#sceneSetting');
  await expect(setting.locator('option')).toHaveText([
    'Garage',
    'City plaza · Night',
    'Coastal Sunset',
    'Studio',
  ]);
  await expect(setting).toHaveValue('garage');
  expect(await page.evaluate((key) => localStorage.getItem(key), key)).toBe('garage');
  await page.evaluate((key) => localStorage.setItem(key, 'courtyard'), key);
  await page.reload();
  await expect(setting).toHaveValue('garage');
  expect(await page.evaluate((key) => localStorage.getItem(key), key)).toBe('garage');

  const fullscreen = page.locator('#sceneFullscreen');
  const dialog = page.getByRole('dialog', { name: 'Vehicle viewer' });
  await fullscreen.click();
  await expect(dialog).toBeVisible();
  await expect(fullscreen).toHaveAccessibleName('Exit full screen');
  expect(await dialog.boundingBox()).toMatchObject({ x: 0, y: 0, width: 320, height: 720 });
  await page.setViewportSize({ width: 720, height: 360 });
  await expect(page.locator('#zoomIn')).toBeInViewport();
  await page.locator('#zoomIn').click();
  await setting.selectOption('coast');
  await expect(page.locator('.stage')).toHaveAttribute('data-environment', 'coast');
  await page.keyboard.press('Escape');
  await expect(dialog).toBeHidden();
  await expect(page.locator('.workspace > .stage')).toBeVisible();
  await expect(fullscreen).toBeFocused();
  await expect(fullscreen).toHaveAccessibleName('Full screen');
  await expect(setting).toHaveValue('coast');
});
