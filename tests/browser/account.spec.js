import { test, expect } from '@playwright/test';
import { createBuild } from '@voltforge/shared/build';
import { readFile } from 'node:fs/promises';

test('guest drafts require explicit import and accounts have separate caches and sync', async ({
  context,
  page,
}) => {
  const guest = createBuild('scooter', 'Local G4 draft');
  const other = { ...createBuild('bike', 'Other account build'), revision: 1 };
  const accounts = {
    'rider@example.com': { id: 'rider', email: 'rider@example.com' },
    'friend@example.com': { id: 'friend', email: 'friend@example.com' },
  };
  const saved = { rider: [], friend: [other] };
  let user = null;
  const buildCalls = [];

  await context.addInitScript(
    ({ build }) => {
      if (!localStorage.getItem('voltforge-v1')) {
        localStorage.setItem('voltforge-v1', JSON.stringify({ active: build.id, builds: [build] }));
      }
    },
    { build: guest },
  );
  await context.route('**/api/**', async (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path === '/api/auth/session') return route.fulfill({ json: { enabled: true, user } });
    if (path === '/api/auth/signup')
      return route.fulfill({ json: { user: null, confirmationRequired: true } });
    if (path === '/api/auth/login') {
      user = accounts[route.request().postDataJSON().email];
      return route.fulfill({ json: { user } });
    }
    if (path === '/api/auth/logout') {
      user = null;
      return route.fulfill({ json: { user } });
    }
    if (!path.startsWith('/api/builds')) return route.fallback();
    const account = route.request().headers()['x-voltmodd-account'];
    buildCalls.push([path, account]);
    if (!user || user.id !== account) return route.fulfill({ status: 409, json: {} });
    if (path === '/api/builds/import') {
      const { builds } = route.request().postDataJSON();
      const additions = builds.filter(
        (build) => !saved[account].some((item) => item.id === build.id),
      );
      saved[account].push(...additions.map((build) => ({ ...build, revision: 1 })));
      return route.fulfill({
        json: {
          builds: saved[account],
          imported: additions.length,
          skipped: builds.length - additions.length,
        },
      });
    }
    return route.fulfill({ json: { builds: saved[account] } });
  });

  await page.goto('/');
  await expect(page.locator('#buildName')).toContainText('Local G4 draft');
  expect(buildCalls).toEqual([]);
  await page.locator('#accountBtn').click();
  await page.locator('#showSignup').click();
  await page.locator('#accountEmail').fill('rider@example.com');
  await page.locator('#accountPassword').fill('long-bike-password');
  await page.locator('#submitAccount').click();
  await expect(page.locator('#accountStatus')).toContainText('confirmation link');
  await page.locator('#accountPassword').fill('long-bike-password');
  await page.locator('#submitAccount').click();
  await expect(page.locator('#setupAccountBtn')).toHaveText('Account');
  expect(saved.rider).toEqual([]);
  expect(buildCalls).toContainEqual(['/api/builds', 'rider']);
  await page.locator('#setupAccountBtn').click();
  await page.locator('#importLocalBuilds').click();
  await expect(page.locator('#accountStatus')).toContainText('Imported 1 build');
  expect(saved.rider).toMatchObject([{ id: guest.id, name: guest.name }]);

  const second = await context.newPage();
  await second.goto('/');
  await expect(second.locator('#buildName')).toContainText('Local G4 draft');
  await page.locator('#logOut').click();
  await expect(page.locator('#accountBtn')).toHaveText('Log in');
  await expect(second.locator('#accountBtn')).toHaveText('Log in');
  await page.locator('#accountBtn').click();
  await page.locator('#accountEmail').fill('friend@example.com');
  await page.locator('#accountPassword').fill('long-bike-password');
  await page.locator('#submitAccount').click();
  await expect(page.locator('#buildName')).toContainText('Other account build');
  await expect(second.locator('#buildName')).toContainText('Other account build');
  await second.locator('#savedNav').click();
  await expect(second.locator('#detailBody')).not.toContainText('Local G4 draft');
  expect(saved.friend).toEqual([other]);
});

test('password recovery opens the change-password form and retains the mobile layout', async ({
  page,
}) => {
  let recovering = false;
  let user = null;
  await page.setViewportSize({ width: 360, height: 800 });
  await page.route('**/api/auth/**', async (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path === '/api/auth/session')
      return route.fulfill({ json: { enabled: true, user, recovering } });
    if (path === '/api/auth/reset') return route.fulfill({ json: { ok: true } });
    if (path === '/api/auth/password') {
      expect(route.request().postDataJSON().password).toBe('updated-password');
      recovering = false;
      user = { id: 'rider', email: 'rider@example.com' };
      return route.fulfill({ json: { user } });
    }
    return route.fallback();
  });
  await page.route('**/api/builds', (route) => route.fulfill({ json: { builds: [] } }));

  await page.goto('/');
  await page.locator('#setupAccountBtn').click();
  await page.locator('#showReset').click();
  await page.locator('#accountEmail').fill('rider@example.com');
  await page.locator('#submitAccount').click();
  await expect(page.locator('#accountStatus')).toContainText('reset link');
  recovering = true;
  await page.goto('/?auth=reset');
  await expect(page.locator('#accountHeading')).toHaveText('Choose a new password');
  await expect(page.locator('#accountEmail')).toBeHidden();
  expect(
    await page.locator('#accountDialog').evaluate((dialog) => dialog.clientWidth <= innerWidth),
  ).toBe(true);
  await page.locator('#accountPassword').fill('updated-password');
  await page.locator('#submitAccount').click();
  await expect(page.locator('#setupAccountBtn')).toHaveText('Account');
});

test('a garage download imports on a different origin and preserves duplicate builds', async ({
  context,
  page,
}) => {
  const build = {
    ...createBuild('bike', 'Portable bike build'),
    paint: { frame: '#217c83' },
    revision: 3,
  };
  const user = { id: 'rider', email: 'rider@example.com' };
  const saved = [];
  let attempts = 0;

  await page.addInitScript((build) => {
    localStorage.setItem('voltforge-v1', JSON.stringify({ active: build.id, builds: [build] }));
  }, build);
  await page.route('**/api/auth/session', (route) => route.fulfill({ json: { enabled: false } }));
  await page.route('**/api/builds', (route) => route.fulfill({ json: { builds: [build] } }));
  await page.goto('/');
  await page.locator('#savedNav').click();
  const downloadPromise = page.waitForEvent('download');
  await page.locator('#downloadBuilds').click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe('voltmodd-builds.json');
  const path = await download.path();
  const exported = JSON.parse(await readFile(path, 'utf8'));
  expect(exported.builds).toMatchObject([{ id: build.id, paint: build.paint }]);
  expect(exported.builds[0].revision).toBeUndefined();

  const hosted = await context.newPage();
  await hosted.route('**/api/auth/session', (route) =>
    route.fulfill({ json: { enabled: true, user } }),
  );
  await hosted.route('**/api/builds', (route) => route.fulfill({ json: { builds: saved } }));
  await hosted.route('**/api/builds/import', (route) => {
    attempts++;
    expect(route.request().headers()['x-voltmodd-account']).toBe(user.id);
    const { builds } = route.request().postDataJSON();
    const additions = builds.filter((item) => !saved.some((existing) => existing.id === item.id));
    saved.push(...additions.map((item) => ({ ...item, revision: 1 })));
    return route.fulfill({
      json: {
        builds: saved,
        imported: additions.length,
        skipped: builds.length - additions.length,
      },
    });
  });
  const origin = new URL(page.url());
  origin.hostname = 'localhost';
  await hosted.goto(origin.href);
  await hosted.locator('#setupAccountBtn').click();
  await expect(hosted.locator('#importLocalBuilds')).toBeDisabled();
  const picker = hosted.waitForEvent('filechooser');
  await hosted.locator('#importBuildFile').click();
  await (
    await picker
  ).setFiles({
    name: 'unrelated.json',
    mimeType: 'application/json',
    buffer: Buffer.from('{}'),
  });
  await expect(hosted.locator('#accountStatus')).toContainText(
    'downloaded from the VOLTMODD garage',
  );
  expect(attempts).toBe(0);
  await hosted.locator('#garageFile').setInputFiles(path);
  await expect(hosted.locator('#accountStatus')).toContainText('Imported 1 build.');
  await hosted.locator('#garageFile').setInputFiles(path);
  await expect(hosted.locator('#accountStatus')).toContainText('1 already in your account.');
  expect(saved).toMatchObject([
    { id: build.id, name: build.name, paint: build.paint, revision: 1 },
  ]);
});
