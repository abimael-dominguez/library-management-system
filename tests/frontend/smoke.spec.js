import { expect, test } from '@playwright/test';

const apiBaseUrl = process.env.LMS_API_BASE_URL || 'http://localhost:8000';
const frontendBaseUrl = process.env.FRONTEND_BASE_URL || 'http://localhost:8080';

function appHosts() {
  return [new URL(frontendBaseUrl).host, new URL(apiBaseUrl).host];
}

async function installAppDefaults(page, language = 'es') {
  await page.addInitScript(({ apiUrl, preferredLanguage }) => {
    window.LMS_API_BASE_URL = apiUrl;
    if (!window.localStorage.getItem('language')) {
      window.localStorage.setItem('language', preferredLanguage);
    }
  }, { apiUrl: apiBaseUrl, preferredLanguage: language });
}

function observeCriticalBrowserNoise(page) {
  const consoleErrors = [];
  const pageErrors = [];
  const failedAppResponses = [];
  const hosts = appHosts();

  page.on('console', message => {
    if (message.type() === 'error') {
      consoleErrors.push(message.text());
    }
  });
  page.on('pageerror', error => {
    pageErrors.push(error.message);
  });
  page.on('response', response => {
    const url = new URL(response.url());
    if (hosts.includes(url.host) && response.status() >= 400) {
      failedAppResponses.push(`${response.status()} ${response.url()}`);
    }
  });

  return () => {
    expect(consoleErrors, 'console errors').toEqual([]);
    expect(pageErrors, 'page errors').toEqual([]);
    expect(failedAppResponses, 'failed app responses').toEqual([]);
  };
}

async function openApp(page, language = 'es') {
  await installAppDefaults(page, language);
  const assertNoCriticalNoise = observeCriticalBrowserNoise(page);
  await page.goto('/');
  await expect(page.locator('#searchInput')).toBeVisible();
  await expect(page.locator('#booksContainer')).toContainText(/gracia|antinomismo|bajo/i);
  return assertNoCriticalNoise;
}

async function clickVisibleNav(page, target) {
  await page.locator(`[data-nav-target="${target}"]:visible`).first().click();
  await expect(page.locator('body')).toHaveAttribute('data-workspace-view', target);
}

test('mobile first screen exposes circulation controls without initial scroll', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'mobile', 'mobile-only viewport assertion');

  const assertNoCriticalNoise = await openApp(page);
  const viewport = page.viewportSize();
  const keyControls = [
    page.locator('#searchInput'),
    page.locator('.action-loan:visible').first(),
    page.locator('.action-return:visible').first(),
    page.locator('[data-nav-target="home"]:visible').first(),
    page.locator('[data-nav-target="catalog"]:visible').first(),
    page.locator('[data-nav-target="loans"]:visible').first(),
    page.locator('[data-nav-target="members"]:visible').first(),
    page.locator('[data-nav-target="more"]:visible').first()
  ];

  for (const control of keyControls) {
    await expect(control).toBeVisible();
    const box = await control.boundingBox();
    expect(box, 'control must have layout box').not.toBeNull();
    expect(box.y + box.height).toBeLessThanOrEqual(viewport.height);
  }

  assertNoCriticalNoise();
});

test('catalog search, navigation, and circulation modals work', async ({ page }) => {
  const assertNoCriticalNoise = await openApp(page);

  await page.locator('#searchInput').fill('gracia');
  await expect(page.locator('#searchResults')).toContainText(/gracia/i);

  for (const target of ['catalog', 'loans', 'members', 'more', 'home']) {
    await clickVisibleNav(page, target);
  }

  await page.locator('.action-loan:visible').first().click();
  await expect(page.locator('#createLoanModal')).toHaveClass(/active/);
  await page.keyboard.press('Escape');
  await expect(page.locator('#createLoanModal')).not.toHaveClass(/active/);

  await page.locator('.action-return:visible').first().click();
  await expect(page.locator('#returnBookModal')).toHaveClass(/active/);
  await page.keyboard.press('Escape');
  await expect(page.locator('#returnBookModal')).not.toHaveClass(/active/);

  assertNoCriticalNoise();
});

test('selecting a loan book result does not submit or reload the form', async ({ page }) => {
  const assertNoCriticalNoise = await openApp(page);

  await page.locator('.action-loan:visible').first().click();
  await expect(page.locator('#createLoanModal')).toHaveClass(/active/);

  await page.locator('#bookSearch').pressSequentially('gracia');
  await expect(page.locator('#bookSearchResults')).toContainText(/gracia/i);
  await page.locator('#bookSearchResults .search-result-item').first().click();

  await expect(page.locator('#createLoanModal')).toHaveClass(/active/);
  await expect(page.locator('input[name="book_copy_id"]')).not.toHaveValue('');
  expect(new URL(page.url()).search).toBe('');

  assertNoCriticalNoise();
});

test('language switch persists after reload', async ({ page }) => {
  const assertNoCriticalNoise = await openApp(page, 'es');

  await clickVisibleNav(page, 'more');
  await page.locator('[data-language-option="en"]').click();
  await expect(page.locator('html')).toHaveAttribute('lang', 'en');
  await expect(page).toHaveTitle('CBG Library');

  await page.reload();
  await expect(page.locator('html')).toHaveAttribute('lang', 'en');
  await expect(page.locator('#searchInput')).toHaveAttribute('placeholder', 'Search title, author, or ISBN');

  await clickVisibleNav(page, 'more');
  await page.locator('[data-language-option="es"]').click();
  await expect(page.locator('html')).toHaveAttribute('lang', 'es');

  assertNoCriticalNoise();
});

test('frontend serves favicon assets', async ({ request }) => {
  const svgResponse = await request.get(`${frontendBaseUrl}/favicon.svg`);
  const icoResponse = await request.get(`${frontendBaseUrl}/favicon.ico`);

  expect(svgResponse.status()).toBe(200);
  expect(icoResponse.status()).toBe(200);
});
