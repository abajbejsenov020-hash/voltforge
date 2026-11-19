import { test, expect } from '@playwright/test';

test('finder wraps keyboard selection and treats exact aliases as catalog matches', async ({
  page,
}) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto('/');
  await page.locator('#browseModelLibrary').click();
  const input = page.locator('#vehicleName');
  const matches = page.locator('#vehicleSuggestions [data-vehicle]');
  const status = page.locator('#vehicleKeyboardStatus');
  await input.fill('Dualtron');
  const count = await matches.count();
  const first = await matches.first().getAttribute('data-vehicle');
  const last = await matches.last().getAttribute('data-vehicle');
  await input.press('ArrowUp');
  await expect(status).toHaveText(`${last}, result ${count} of ${count}`);
  await input.press('ArrowDown');
  await expect(status).toHaveText(`${first}, result 1 of ${count}`);
  await input.fill('surron lbx');
  await expect(page.locator('#customVehicle')).toBeHidden();
  await input.press('Enter');
  await expect(input).toHaveValue('Sur-Ron Light Bee X');
  await expect(page.locator('#startBuild')).toBeFocused();
});

test('part actions restore focus and switching modal views opens at the heading', async ({
  page,
}) => {
  await page.goto('/');
  await page.locator('[data-featured-brand="KuKirin"]').click();
  await page.locator('[data-vehicle="KuKirin G4"]').click();
  await page.locator('#startBuild').click();
  await page.locator('#categorySelect').selectOption('Controllers');
  await page.locator('#vehicleFilter').selectOption('all');
  await page.locator('#search').fill('ND72260');
  const add = page.locator('#parts [data-add]');
  const inspect = page.locator('#parts [data-detail]');
  await add.press('Enter');
  await expect(add).toBeFocused();
  await expect(add).toHaveAttribute('aria-pressed', 'true');
  await inspect.press('Enter');
  const dialog = page.getByRole('dialog', { name: /ND72260/ });
  await expect(dialog).toBeVisible();
  await page.locator('#detailAdd').press('Enter');
  await expect(inspect).toBeFocused();
  await expect(add).toHaveAttribute('aria-pressed', 'false');
  await page.locator('#reviewBuild').click();
  await page.locator('#reviewPeakSetup').click();
  await expect(page.getByRole('dialog', { name: /performance references/i })).toBeVisible();
  await expect(page.locator('#detailTitle')).toBeFocused();
  await expect
    .poll(() => page.locator('#detailDialog').evaluate((element) => element.scrollTop))
    .toBe(0);
  await page.keyboard.press('Escape');
  await expect(page.locator('#reviewBuild')).toBeFocused();
});
