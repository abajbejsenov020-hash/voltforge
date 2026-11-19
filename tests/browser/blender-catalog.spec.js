import { test, expect } from '@playwright/test';
import { BLENDER_VEHICLES } from '../../apps/web/src/scene/blender-models.js';
import { VEHICLE_INDEX } from '@voltforge/shared/vehicles';

async function selectVehicle(page, name) {
  if (!(await page.locator('#startDialog').isVisible())) await page.locator('#newBuild').click();
  const type = VEHICLE_INDEX.find((entry) => entry.name === name).type;
  await page.locator(`[data-type="${type}"]`).click();
  await page.locator('#browseModelLibrary').click();
  await page.locator('#vehicleName').fill(name);
  await page.locator(`[data-vehicle="${name}"]`).click();
  await page.locator('#startBuild').click();
  const model = BLENDER_VEHICLES.find((entry) => entry.name === name);
  await expect(page.locator('#modelLabel')).toHaveText(name);
  await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'blender', {
    timeout: 20000,
  });
  await expect(page.locator('#scene')).toHaveAttribute('data-model-profile', model.key);
  await expect(page.locator('#scene')).toHaveAttribute('data-model-state', 'ready');
}

const groups = {
  scooters: [
    'KuKirin G2 Max',
    'KuKirin G2 Master',
    'KuKirin G3 Pro',
    'KuKirin M4 Max',
    'KuKirin G4 Ultra',
    'Ausom DT2 Pro',
    'Ausom F1 Max',
    'Ausom Gosoul 2',
  ],
  lightmoto: [
    'Sur-Ron Ultra Bee',
    'Sur-Ron Storm Bee',
    'Sur-Ron Hyper Bee',
    'Talaria Sting R MX4',
    'Talaria XXX',
    'Talaria Komodo',
    'Talaria Junior ET01',
    'E Ride Pro SR',
    'E Ride Pro Mini R',
    'Altis Sigma MX',
    'Altis Omega',
  ],
  motoBicycle: [
    'Arctic Leopard XF Pro',
    'Arctic Leopard XE Pro S Enduro',
    'Arctic Leopard E-XE 880 Super',
    'Stark Varg MX',
    'Stark Varg EX',
    'Stark Varg SM Skoll',
    'Fiido M1 Pro',
    'Fiido C11',
  ],
};
for (const [group, names] of Object.entries(groups))
  test(`new Blender ${group} families load their exact assets and preserve controls`, async ({
    page,
  }) => {
    test.setTimeout(240000);
    const errors = [];
    page.on('pageerror', (error) => errors.push(error.message));
    await page.goto('/');
    for (const name of names) {
      await selectVehicle(page, name);
      await page.locator('#sceneSetting').selectOption('studio');
      await page.locator('[data-view="cockpit"]').click();
      await page.locator('#resetView').click();
      await page.locator('#explode').click();
      await page.locator('#explode').click();
      await page.locator('button[data-presentation="photo"]').click();
      await expect(page.locator('#vehiclePhoto')).toBeVisible();
      await page.locator('button[data-presentation="concept"]').click();
      await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'blender');
      if (['Sur-Ron Hyper Bee', 'Sur-Ron Ultra Bee'].includes(name))
        await page.screenshot({ path: `test-results/${name.replaceAll(' ', '-')}.png` });
    }
    await page.screenshot({ path: `test-results/blender-${group}-catalog.png`, fullPage: false });
    await page.reload();
    await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'blender', {
      timeout: 20000,
    });
    expect(errors).toEqual([]);
  });

test('a failed model request stays an explicitly labeled fallback without breaking build results', async ({
  page,
}) => {
  await page.route('**/models/catalog/**.glb', (route) => route.abort('failed'));
  await page.goto('/');
  await page.locator('[data-featured-brand="KuKirin"]').click();
  await expect(page.locator('#startBuild')).toBeDisabled();
  await page.locator('#vehicleName').fill('G2 Master');
  await page.locator('[data-vehicle="KuKirin G2 Master"]').click();
  await page.locator('#startBuild').click();
  await expect(page.locator('#modelLabel')).toHaveText('KuKirin G2 Master');
  await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'fallback', {
    timeout: 20000,
  });
  await expect(page.locator('#sceneModelStatus')).toContainText('fallback');
  await expect(page.locator('#estimatedPeak')).not.toBeEmpty();
  await page.locator('button[data-presentation="photo"]').click();
  await expect(page.locator('#vehiclePhoto')).toBeVisible();
});
