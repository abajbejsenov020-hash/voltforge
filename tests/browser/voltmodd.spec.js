import { readFile } from 'node:fs/promises';
import { expect, test } from '@playwright/test';
import { createBuild } from '@voltforge/shared/build';

test.use({ deviceScaleFactor: 2 });

async function openSavedBuild(page) {
  const build = {
    ...createBuild('scooter', 'My saved G4'),
    mode: 'rebuild',
    vehicle: 'KuKirin G4',
    selected: { Controllers: 'p291' },
  };
  await page.addInitScript((initial) => {
    if (sessionStorage.getItem('voltmodd-fixture')) return;
    sessionStorage.setItem('voltmodd-fixture', 'yes');
    localStorage.setItem('voltforge-v1', JSON.stringify({ active: initial.id, builds: [initial] }));
    localStorage.setItem('voltforge-scene-environment', 'studio');
  }, build);
  await page.goto('/');
  await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'blender');
}

test('VOLTMODD opens saved builds and upgrades their 3D view, graphics controls and exports', async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await openSavedBuild(page);
  await expect(page).toHaveTitle(/VOLTMODD/);
  await expect(page.locator('.site-header .wordmark')).toHaveText('VOLTMODD');
  await expect(page.locator('#buildName')).toContainText('My saved G4');
  await expect(page.locator('#swapStatus')).toContainText('In the 3D build: Controllers.');
  const scene = page.locator('#scene');
  const graphics = page.locator('#graphicsSettings > summary');
  const quality = page.locator('#renderQuality');
  const motion = page.locator('#reduceMotion');
  await expect(scene).toHaveAttribute('data-render-quality', 'high');
  const highWidth = await scene.evaluate((canvas) => canvas.width);
  await page.screenshot({ path: 'test-results/voltmodd-workbench.png' });
  await graphics.click();
  await quality.selectOption('efficient');
  await motion.check();
  await expect(scene).toHaveAttribute('data-render-quality', 'efficient');
  await expect.poll(() => scene.evaluate((canvas) => canvas.width)).toBeLessThan(highWidth);
  await expect(scene).toHaveAttribute('data-reduced-motion', 'true');
  await graphics.click();
  const exploded = await page.locator('#explode').evaluate((button) => {
    button.click();
    return document.querySelector('#scene').dataset.explodeState;
  });
  expect(exploded).toBe('exploded');
  await page.locator('#categorySelect').selectOption('Controllers');
  await page.locator('#vehicleFilter').selectOption('all');
  await page.locator('#search').fill('ND72260');
  await page.locator('[data-detail="p291"]').click();
  await page.locator('#detailBody [data-part-view="model"]').click();
  await expect(page.locator('#detailBody [data-component="p291"]')).toHaveAttribute(
    'data-render-quality',
    'efficient',
  );
  await page.locator('#closeDetail').click();
  const downloadEvent = page.waitForEvent('download');
  await page.locator('#exportBuild').click();
  const download = await downloadEvent;
  const text = await readFile(await download.path(), 'utf8');
  expect(text).toContain('VOLTMODD — BUILD PLAN');
  expect(text).toContain('My saved G4');
  await page.reload();
  await expect(scene).toHaveAttribute('data-render-quality', 'efficient');
  await expect(quality).toHaveValue('efficient');
  await expect(motion).toBeChecked();
  await expect(page.locator('#buildName')).toContainText('My saved G4');
});

test('graphics controls fit a narrow phone and still follow the system motion preference', async ({
  page,
}) => {
  await page.setViewportSize({ width: 320, height: 844 });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await openSavedBuild(page);
  await expect(page.locator('#scene')).toHaveAttribute('data-reduced-motion', 'true');
  const graphics = page.locator('#graphicsSettings > summary');
  await graphics.click();
  const quality = page.locator('#renderQuality');
  await expect(quality).toBeVisible();
  const control = await quality.boundingBox();
  expect(control.x).toBeGreaterThanOrEqual(0);
  expect(control.x + control.width).toBeLessThanOrEqual(320);
  await quality.selectOption('efficient');
  await expect(page.locator('#reduceMotion')).not.toBeChecked();
  await expect(page.locator('#scene')).toHaveAttribute('data-reduced-motion', 'true');
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(320);
  await quality.press('Escape');
  await expect(quality).toBeHidden();
  await expect(graphics).toBeFocused();
  await page.screenshot({ path: 'test-results/voltmodd-mobile.png' });

  await page.locator('#categorySelect').selectOption('Controllers');
  await page.locator('#vehicleFilter').selectOption('all');
  await page.locator('#search').fill('ND72260');
  await page.locator('[data-detail="p291"]').click();
  await page.locator('#detailBody [data-part-view="model"]').click();
  const inspector = page.locator('#detailDialog');
  const dialog = await inspector.boundingBox();
  const reset = inspector.getByRole('button', { name: 'Reset view', exact: true });
  const resetBounds = await reset.boundingBox();
  expect(resetBounds.x + resetBounds.width).toBeLessThan(dialog.x + dialog.width);
  await reset.click();
});
