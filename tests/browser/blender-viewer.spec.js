import { test, expect } from '@playwright/test';

async function choose(page, name, type) {
  if ((await page.locator('#startDialog').isVisible()) === false)
    await page.locator('#newBuild').click();
  await page.locator(`[data-type="${type}"]`).click();
  await page.locator(`[data-featured="${name}"]`).click();
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
  await choose(page, 'KuKirin G4', 'scooter');
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
  await choose(page, 'Sur-Ron Light Bee X', 'bike');
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
  await choose(page, 'KuKirin G4', 'scooter');
  await page.locator('#sceneSetting').selectOption('studio');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.locator('#zoomIn').click();
  await page.locator('#resetView').click();
  await page.screenshot({ path: 'test-results/blender-g4-mobile.png', fullPage: false });
});
