import { expect, test } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('report shell supports navigation, themes and keyboard access', async ({
  page,
}, testInfo) => {
  await page.goto('/');
  await expect(page.getByText('Service connected')).toBeVisible();
  await expect(
    page.getByRole('button', { name: 'Add a report' }),
  ).toBeDisabled();
  await page.keyboard.press('Tab');
  await expect(
    page.getByRole('link', { name: 'Skip to main content' }),
  ).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('main')).toBeFocused();
  const navigation = page.getByRole('navigation', { name: 'Main navigation' });
  const navBox = await navigation.boundingBox();
  expect(navBox).not.toBeNull();
  if (testInfo.project.name === 'mobile') {
    expect(navBox!.y).toBeGreaterThan(500);
  } else {
    expect(navBox!.x).toBeLessThan(256);
  }
  await page
    .getByRole('combobox', { name: 'Colour theme' })
    .selectOption('dark');
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await testInfo.attach(`report-${testInfo.project.name}`, {
    body: await page.screenshot({ fullPage: true, animations: 'disabled' }),
    contentType: 'image/png',
  });
  await expect(
    page.getByRole('link', { name: 'History', exact: true }),
  ).toBeVisible();
  await page.getByRole('link', { name: 'History', exact: true }).click();
  await expect(
    page.getByRole('heading', { name: 'Your history starts with an account' }),
  ).toBeVisible();
  await page.getByRole('link', { name: 'Account', exact: true }).click();
  await expect(page.getByLabel('Email address')).toBeVisible();
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
        .analyze()
    ).violations,
  ).toEqual([]);
});

test('all foundation screens have accessible light and dark states', async ({
  page,
}) => {
  for (const theme of ['light', 'dark']) {
    for (const route of ['report', 'history', 'account']) {
      await page.goto(`/#/${route}`);
      await expect(page.getByText('Service connected')).toBeVisible();
      await page
        .getByRole('combobox', { name: 'Colour theme' })
        .selectOption(theme);
      const results = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
        .analyze();
      expect(results.violations).toEqual([]);
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
    }
  }
});

test('offline account submission is disabled', async ({ page, context }) => {
  await page.goto('/#/account');
  await expect(page.getByLabel('Email address')).toBeVisible();
  await context.setOffline(true);
  await expect(
    page.getByText('Reconnect before submitting this form.'),
  ).toBeVisible();
  await expect(page.locator('button[type="submit"]')).toBeDisabled();
  await context.setOffline(false);
  await expect(page.getByText('Service connected')).toBeVisible();
});
