import { test, expect } from '@playwright/test';
import { createBuild } from '@voltforge/shared/build';

async function openBuild(page, vehicle = 'KuKirin G4', type = 'scooter') {
  const build = { ...createBuild(type, vehicle + ' workshop'), mode: 'rebuild', vehicle };
  await page.addInitScript((initial) => {
    if (sessionStorage.getItem('customization-test-seeded')) return;
    sessionStorage.setItem('customization-test-seeded', 'yes');
    localStorage.setItem('voltforge-v1', JSON.stringify({ active: initial.id, builds: [initial] }));
    localStorage.setItem('voltforge-scene-environment', 'studio');
  }, build);
  await page.goto('/');
  await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'blender', {
    timeout: 20000,
  });
  return build.id;
}

async function selectPart(page, category, query, id) {
  await page.locator('#categorySelect').selectOption(category);
  await page.locator('#vehicleFilter').selectOption('all');
  await page.locator('#appearanceFilter').selectOption('all');
  await page.locator('#search').fill(query);
  await page.locator(`[data-add="${id}"]`).click();
}

test('shows a replacement in the G4 model, animates disassembly and restores stock', async ({
  page,
}) => {
  await openBuild(page);
  await page.locator('button[data-presentation="photo"]').click();
  await selectPart(page, 'Controllers', 'ND72260', 'p291');
  await page.locator('#inspectBuild3D').click();
  await expect(page.locator('#scene')).toBeFocused();
  await expect(page.locator('#swapStatus')).toContainText('In the 3D build: Controllers.');
  const scene = page.locator('#scene');
  const explode = page.locator('#explode');
  await explode.evaluate((button) => button.click());
  await expect(explode).toHaveAttribute('aria-pressed', 'true');
  await expect(scene).toHaveAttribute('data-explode-state', 'exploded');
  const preview = await page.locator('.stage').screenshot({
    path: 'test-results/g4-exploded-controller.png',
  });
  const greenPixels = await page.evaluate(async (png) => {
    const blob = await (await fetch('data:image/png;base64,' + png)).blob();
    const image = await createImageBitmap(blob);
    const context = new OffscreenCanvas(image.width, image.height).getContext('2d');
    context.drawImage(image, 0, 0);
    const { data } = context.getImageData(0, 0, image.width, image.height);
    let green = 0;
    for (let i = 0; i < data.length; i += 4) {
      if (data[i + 1] > data[i] * 1.2 && data[i + 1] > data[i + 2] * 1.25) green++;
    }
    image.close();
    return green;
  }, preview.toString('base64'));
  expect(greenPixels).toBeGreaterThan(10);
  const interruption = await explode.evaluate((button) => {
    button.click();
    const state = document.querySelector('#scene').dataset.explodeState;
    button.click();
    button.click();
    return state;
  });
  expect(interruption).toBe('moving');
  await expect(scene).toHaveAttribute('data-explode-state', 'assembled');
  await expect(explode).toHaveAttribute('aria-pressed', 'false');
  await page.locator('#returnToStock').click();
  await expect(page.locator('#swapStatus')).toBeHidden();
  await selectPart(page, 'Displays', 'Simple Display', 'p55');
  await expect(page.locator('#swapStatus')).toHaveText('3D replacement unavailable: Displays.');
});

test('saves independent LBX paint zones and resets only the active zone', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  const id = await openBuild(page, 'Sur-Ron Light Bee X', 'bike');
  const zone = page.locator('#paintZone');
  const color = page.locator('#paintColor');
  const reset = page.locator('#resetPaint');
  await zone.selectOption('fork');
  const factoryFork = await color.inputValue();
  await color.fill('#de400b');
  await zone.selectOption('body');
  await color.fill('#ef1280');
  await expect
    .poll(async () => {
      const { builds } = await (await page.request.get('/api/builds')).json();
      return builds.find((build) => build.id === id)?.paint;
    })
    .toEqual({ fork: '#de400b', body: '#ef1280' });
  await page.reload();
  await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'blender');
  await zone.selectOption('body');
  await expect(color).toHaveValue('#ef1280');
  await zone.selectOption('fork');
  await expect(color).toHaveValue('#de400b');
  await reset.click();
  await expect(color).toHaveValue(factoryFork);
  await expect(reset).toBeDisabled();
  await zone.selectOption('body');
  await expect(color).toHaveValue('#ef1280');
  const state = await page.locator('#explode').evaluate((button) => {
    button.click();
    return document.querySelector('#scene').dataset.explodeState;
  });
  expect(state).toBe('exploded');
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(390);
  await page.locator('.stage').screenshot({ path: 'test-results/lbx-painted-mobile.png' });
  await page.locator('button[data-presentation="photo"]').click();
  await expect(page.locator('#paintControls')).toBeHidden();
  await page.locator('button[data-presentation="concept"]').click();
  await expect(page.locator('#paintControls')).toBeVisible();
  await zone.selectOption('body');
  await expect(color).toHaveValue('#ef1280');
});
