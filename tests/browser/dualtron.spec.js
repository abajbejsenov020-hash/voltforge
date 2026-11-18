import { test, expect } from '@playwright/test';
import { VEHICLE_INDEX } from '@voltforge/shared/vehicles';
import { BLENDER_VEHICLES } from '../../apps/web/src/scene/blender-models.js';

test('all 23 Dualtrons load their own refined assets and retain inspection controls', async ({
  page,
}) => {
  test.setTimeout(240000);
  const vehicles = VEHICLE_INDEX.filter((entry) => entry.brand === 'Dualtron');
  expect(vehicles).toHaveLength(23);
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('console', (message) => {
    if (message.type() === 'error' && /GLTFLoader|texture|bitmap/i.test(message.text()))
      errors.push(message.text());
  });
  await page.goto('/');
  for (const vehicle of vehicles) {
    const model = BLENDER_VEHICLES.find((entry) => entry.name === vehicle.name);
    expect(model, vehicle.name).toBeTruthy();
    if (!(await page.locator('#startDialog').isVisible())) await page.locator('#newBuild').click();
    await page.locator('#browseModelLibrary').click();
    await page.locator('#vehicleName').fill(vehicle.name);
    await page.locator(`[data-vehicle="${vehicle.name}"]`).click();
    await page.locator('#startBuild').click();
    await expect(page.locator('#scene')).toHaveAttribute('data-model-profile', model.key, {
      timeout: 25000,
    });
    await expect(page.locator('#scene')).toHaveAttribute('data-model-source', 'blender');
    await expect(page.locator('#scene')).toHaveAttribute('data-model-state', 'ready');
    const decoded = await page.evaluate(async (url) => {
      const buffer = await (await fetch(url)).arrayBuffer();
      const view = new DataView(buffer),
        jsonLength = view.getUint32(12, true);
      const gltf = JSON.parse(new TextDecoder().decode(new Uint8Array(buffer, 20, jsonLength)));
      const binaryStart = 28 + jsonLength;
      return Promise.all(
        gltf.images.map(async (image) => {
          if (image.uri || image.bufferView === undefined)
            throw new Error('Expected an embedded model image');
          const data = gltf.bufferViews[image.bufferView];
          const start = binaryStart + (data.byteOffset || 0);
          const bitmap = await createImageBitmap(
            new Blob([buffer.slice(start, start + data.byteLength)], { type: image.mimeType }),
          );
          const size = [bitmap.width, bitmap.height];
          bitmap.close();
          return size;
        }),
      );
    }, model.url);
    expect(decoded.length, `${vehicle.name} embedded deck graphics`).toBeGreaterThanOrEqual(
      vehicle.name === 'Dualtron Thunder 3' ? 2 : 1,
    );
    expect(decoded.every(([width, height]) => width >= 16 && height >= 16)).toBe(true);
    await page.locator('#sceneSetting').selectOption('studio');
    if (
      ['Dualtron Thunder 3', 'Dualtron X2', 'Dualtron Spider', 'Dualtron Mini'].includes(
        vehicle.name,
      )
    ) {
      await page.locator('[data-view="frame"]').click();
      await page.locator('#scene').press('ArrowUp');
      await page.screenshot({ path: `test-results/${model.key}-browser-deck.png` });
      await page.locator('[data-view="cockpit"]').click();
      await page.screenshot({ path: `test-results/${model.key}-browser-cockpit.png` });
      await page.locator('#explode').click();
      await page.locator('#explode').click();
      await page.locator('#resetView').click();
    }
    await page.locator('button[data-presentation="photo"]').click();
    await expect(page.locator('#vehiclePhoto')).toHaveAttribute('src', model.image);
    await expect
      .poll(() =>
        page.locator('#vehiclePhoto').evaluate((img) => img.complete && img.naturalWidth > 0),
      )
      .toBe(true);
    await page.locator('button[data-presentation="concept"]').click();
  }
  await page.locator('#sceneSetting').selectOption('plaza');
  await expect(page.locator('#scene')).toHaveAttribute('data-plaza-state', 'ready', {
    timeout: 25000,
  });
  await page.reload();
  await expect(page.locator('#scene')).toHaveAttribute(
    'data-model-profile',
    BLENDER_VEHICLES.find((entry) => entry.name === vehicles.at(-1).name).key,
    { timeout: 25000 },
  );
  expect(errors).toEqual([]);
});
