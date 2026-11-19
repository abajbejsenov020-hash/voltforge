import { expect, test } from '@playwright/test';

const gSeries = [
  'KuKirin G4',
  'KuKirin G2 Master',
  'KuKirin G3 Pro',
  'KuKirin G2 Max',
  'KuKirin G2',
  'KuKirin G2 VMP',
  'KuKirin G2 Pro',
  'KuKirin G2 Pro VMP',
  'KuKirin G2 Pro ABE',
  'KuKirin G2 Ultra',
  'KuKirin G3',
  'KuKirin G4 Max',
  'KuKirin G4 Ultra',
];

async function choose(page, name) {
  if (!(await page.locator('#startDialog').isVisible())) await page.locator('#newBuild').click();
  await page.locator('[data-featured-brand="KuKirin"]').click();
  await page.locator(`[data-vehicle="${name}"]`).click();
  await page.locator('#startBuild').click();
  await expect(page.locator('#modelLabel')).toHaveText(name);
  await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'blender', {
    timeout: 20_000,
  });
  await expect(page.locator('#cockpitControls')).toBeVisible();
}

test('all 13 KuKirin G builds open their own Blender model with adjustable cockpit mounts', async ({
  page,
}) => {
  test.setTimeout(120_000);
  await page.addInitScript(() => {
    if (!localStorage.getItem('voltforge-scene-environment'))
      localStorage.setItem('voltforge-scene-environment', 'studio');
  });
  await page.goto('/');
  const models = new Set();
  for (const name of gSeries) {
    await choose(page, name);
    const canvas = page.locator('#scene');
    models.add(await canvas.getAttribute('data-model-profile'));
    await page.locator('#barStyle').selectOption('swept');
    await page.locator('#barWidth').selectOption('740');
    await expect(canvas).toHaveAttribute('data-cockpit-width', '740');
  }
  expect(models.size).toBe(gSeries.length);
});

test('grip design, color, handlebar and width survive reload, then restore together', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await choose(page, 'KuKirin G4');
  const canvas = page.locator('#scene');
  const stock = await canvas.getAttribute('data-cockpit-width');
  await expect(page.locator('#gripColor')).toBeDisabled();
  await expect(page.locator('#barWidth')).toBeDisabled();
  await page.locator('#gripStyle').selectOption('lock-on');
  await page.locator('#gripColor').selectOption('orange');
  await page.locator('#barStyle').selectOption('high-rise');
  await page.locator('#barWidth').selectOption('760');
  await page.locator('#inspectCockpit').click();
  await expect(page.locator('[data-view="cockpit"]')).toHaveAttribute('aria-pressed', 'true');
  await expect(canvas).toHaveAttribute('data-cockpit-width', '760');
  await page.reload();
  await expect(page.locator('#gripStyle')).toHaveValue('lock-on');
  await expect(page.locator('#gripColor')).toHaveValue('orange');
  await expect(page.locator('#barStyle')).toHaveValue('high-rise');
  await expect(page.locator('#barWidth')).toHaveValue('760');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.locator('#resetCockpit').click();
  await expect(canvas).toHaveAttribute('data-cockpit-width', stock);
  await expect(page.locator('#gripStyle')).toHaveValue('');
  await expect(page.locator('#barStyle')).toHaveValue('');
  await expect(page.locator('#resetCockpit')).toBeDisabled();
});
