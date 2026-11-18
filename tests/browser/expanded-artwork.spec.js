import { test, expect } from '@playwright/test';
import { VEHICLE_INDEX } from '@voltforge/shared/vehicles';
import { BLENDER_VEHICLES } from '../../apps/web/src/scene/blender-models.js';
import { createBuild } from '@voltforge/shared/build';

const groups = {
  commuter: [
    'KuKirin G3',
    'Kugoo G-Booster',
    'Ausom SR1',
    'NIU KQi2 Pro',
    'Segway Ninebot Max G2',
    'Segway Ninebot GT2',
    'Segway Ninebot ZT3 Pro',
    'Segway Ninebot Max G3',
    'Segway Ninebot F3 Pro',
    'Segway Ninebot E2 Pro',
    'Segway Ninebot ES4',
    'Joyor S10-S',
    'Joyor S5-Z',
    'Joyor S8-S-Z',
    'Joyor S10-S-Z',
    'Joyor Y6-S',
    'Joyor Y10',
    'Joyor T6',
    'Joyor T10',
    'Joyor T12 Ultra',
    'Joyor C10',
    'Joyor F5',
    'Xiaomi M365',
    'Xiaomi 4 Ultra',
    'iScooter iX6',
  ],
  premium: [
    'Dualtron X2',
    'Kaabo Wolf King GTR',
    'NAMI Burn-E',
    'Vsett 11+',
    'Apollo Pro',
    'EMOVE RoadRunner Pro',
    'Teverun Fighter Supreme',
    'Teverun Fighter Mini',
    'Teverun Blade GT',
    'Varla Eagle One Pro',
    'Inokim OXO',
    'RoadRunner RS5',
  ],
  bikes: [
    'Engwe EP-2 Pro',
    'Fiido T2',
    'Specialized Turbo Levo',
    'Specialized Turbo Como',
    'Super73 R',
    'Arctic Leopard E-16Z',
    'Rad Power RadWagon 4',
    'Trek Marlin',
    'Trek Marlin+',
    'Lectric XP 3.0',
    'KuKirin X1',
    'Sur-Ron Light Bee S',
  ],
};

for (const [batch, names] of Object.entries(groups))
  test(`expanded ${batch} models use exact photos and working 3D assemblies`, async ({ page }) => {
    test.setTimeout(300000);
    const errors = [];
    page.on('pageerror', (error) => errors.push(error.message));
    await page.goto('/');
    for (const name of names) {
      const vehicle = VEHICLE_INDEX.find((row) => row.name === name);
      const model = BLENDER_VEHICLES.find((row) => row.name === name);
      expect(model, `${name} completed model`).toBeTruthy();
      if (!(await page.locator('#startDialog').isVisible()))
        await page.locator('#newBuild').click();
      await page.locator(`[data-type="${vehicle.type}"]`).click();
      await page.locator('#browseModelLibrary').click();
      await page.locator('#vehicleName').fill(name);
      const option = page.locator(`[data-vehicle="${name}"]`);
      await expect(option.locator('img')).toHaveAttribute('src', model.image);
      await option.click();
      await page.locator('#startBuild').click();
      await expect(page.locator('#scene')).toHaveAttribute('data-model-profile', model.key, {
        timeout: 25000,
      });
      await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'blender');
      await expect(page.locator('#scene')).toHaveAttribute('data-model-state', 'ready');
      await expect(page.locator('#referenceVariant')).toBeVisible();
      await page.locator('#sceneSetting').selectOption('studio');
      if (/^(Segway Ninebot|Teverun|Joyor) /.test(name))
        await expect(page.locator('#paintControls')).toBeVisible();
      if (name === 'Teverun Blade GT') {
        await page.locator('#categorySelect').selectOption('Motors');
        await page.locator('#vehicleFilter').selectOption('all');
        await page.locator('#search').fill('Wide Tire Split Hub Motor');
        await page.locator('[data-add="p2"]').click();
        await expect(page.locator('#swapStatus')).toContainText('In the 3D build: Motors.');
        await page.locator('#returnToStock').click();
        await expect(page.locator('#swapStatus')).toBeHidden();
      }
      await page.locator('[data-view="cockpit"]').click();
      await page.locator('#resetView').click();
      await page.locator('#explode').click();
      await page.locator('#explode').click();
      await page.locator('button[data-presentation="photo"]').click();
      const photo = page.locator('#vehiclePhoto');
      await expect(photo).toBeVisible();
      await expect(photo).toHaveAttribute('src', model.image);
      await expect
        .poll(() => photo.evaluate((img) => img.complete && img.naturalWidth > 0))
        .toBe(true);
      await page.locator('button[data-presentation="concept"]').click();
      await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'blender');
    }
    await page.screenshot({ path: `test-results/expanded-${batch}.png` });
    await page.reload();
    await expect(page.locator('#scene')).toHaveAttribute(
      'data-model-profile',
      BLENDER_VEHICLES.find((row) => row.name === names.at(-1)).key,
      { timeout: 25000 },
    );
    expect(errors).toEqual([]);
  });

test('unverified original variants explain their missing reference without borrowing one', async ({
  page,
}) => {
  await page.goto('/');
  await page.locator('#browseModelLibrary').click();
  await page.locator('#vehicleName').fill('Hiley Tiger 8');
  const option = page.locator('[data-vehicle="Hiley Tiger 8"]');
  await expect(option.locator('img')).toHaveCount(0);
  await option.click();
  await expect(page.locator('#selectionNote')).toContainText('Source audit:');
  await page.locator('#startBuild').click();
  await page.locator('#openConceptView').click();
  await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'procedural');
});

test('a remodeled Joyor supports mounted upgrades, paint, and an exploded inspection on a phone', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  const build = {
    ...createBuild('scooter', 'Joyor T12 Ultra rebuild'),
    mode: 'rebuild',
    vehicle: 'Joyor T12 Ultra',
    selected: { Controllers: 'p291' },
  };
  await page.addInitScript((build) => {
    if (sessionStorage.getItem('remodel-seeded')) return;
    sessionStorage.setItem('remodel-seeded', 'yes');
    localStorage.setItem('voltforge-v1', JSON.stringify({ active: build.id, builds: [build] }));
    localStorage.setItem('voltforge-scene-environment', 'studio');
  }, build);
  await page.goto('/');
  const scene = page.locator('#scene');
  await expect(scene).toHaveAttribute('data-model-profile', 'joyor-t12-ultra');
  await expect(scene).toHaveAttribute('data-model-source', 'blender');
  await expect(page.locator('#swapStatus')).toContainText('In the 3D build: Controllers.');
  await page.locator('#paintZone').selectOption('deck');
  await page.locator('#paintColor').fill('#287479');
  await page.locator('#explode').click();
  await expect(scene).toHaveAttribute('data-explode-state', 'exploded');
  await page.locator('.stage').screenshot({ path: 'test-results/joyor-t12-ultra-exploded.png' });
  await page.reload();
  await expect(scene).toHaveAttribute('data-model-source', 'blender');
  await page.locator('#paintZone').selectOption('deck');
  await expect(page.locator('#paintColor')).toHaveValue('#287479');
  await page.locator('#categorySelect').selectOption('Controllers');
  await page.locator('#returnToStock').click();
  await expect(page.locator('#swapStatus')).toBeHidden();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(390);
});
