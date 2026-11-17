import { test, expect } from '@playwright/test';
import { VEHICLE_INDEX } from '@voltforge/shared/vehicles';
import { BLENDER_VEHICLES } from '../../apps/web/src/scene/blender-models.js';

const groups = {
  commuter: [
    'KuKirin G3',
    'Kugoo G-Booster',
    'Ausom SR1',
    'NIU KQi2 Pro',
    'Segway Ninebot Max G2',
    'Segway Ninebot GT2',
    'Segway Ninebot ZT3 Pro',
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
  await page.locator('#vehicleName').fill('Joyor S10-S');
  const option = page.locator('[data-vehicle="Joyor S10-S"]');
  await expect(option.locator('img')).toHaveCount(0);
  await option.click();
  await expect(page.locator('#selectionNote')).toContainText('Source audit:');
  await page.locator('#startBuild').click();
  await page.locator('#openConceptView').click();
  await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'procedural');
});
