import { test, expect } from '@playwright/test';
import { createBuild } from '@voltforge/shared/build';

test('stronger motor keeps a comparable stock-relative speed and explains the retained-supply limit', async ({
  page,
}) => {
  const build = {
    ...createBuild('scooter', 'G4 speed comparison'),
    mode: 'rebuild',
    vehicle: 'KuKirin G4',
  };
  await page.addInitScript((build) => {
    if (localStorage.getItem('speed-comparison-seeded')) return;
    localStorage.setItem('speed-comparison-seeded', 'yes');
    localStorage.setItem('voltforge-v1', JSON.stringify({ active: build.id, builds: [build] }));
  }, build);
  await page.goto('/');
  await expect(page.locator('#estimatedSpeed')).toHaveText('70 km/h');
  await page.locator('#appearanceFilter').selectOption('all');
  await page.locator('#search').fill('75/80mm');
  await page.locator('[data-add="p6"]').click();
  const speed = await page.locator('#estimatedSpeed').innerText();
  expect(Number(speed.match(/\d+/)[0])).toBeGreaterThanOrEqual(70);
  await expect(page.locator('#speedBasis')).toContainText('Factory-relative');
  await expect(page.locator('#speedBasis')).toContainText('cannot use its full rating');
  await page.locator('#automaticPerformance summary').click();
  await expect(page.locator('.estimate-assumptions')).toContainText('comparison anchored');
  await page.locator('#quickPerformanceForm [name="bms"]').fill('20');
  await page.locator('#quickPerformanceForm [name="peakControllerA"]').fill('20');
  await page.locator('#quickPerformanceForm button').click();
  const limited = await page.locator('#estimatedSpeed').innerText();
  expect(Number(limited.match(/\d+/)[0])).toBeLessThan(70);
  await expect(page.locator('#speedBasis')).toContainText('Entered supply limits');
  await page.reload();
  await expect(page.locator('#estimatedSpeed')).toHaveText(limited);
});
