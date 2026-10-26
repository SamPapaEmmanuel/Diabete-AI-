import { randomUUID } from 'node:crypto';
import { readdirSync, readFileSync } from 'node:fs';
import path from 'node:path';
import { expect, test } from '@playwright/test';

test('an account can register, verify, recover access and sign out', async ({
  page,
}) => {
  const email = `browser-${randomUUID()}@example.org`;
  const password = 'A quiet morning near the garden';
  await page.goto('/#/account');
  await expect(page.getByLabel('Email address')).toBeVisible();
  await page
    .getByRole('button', { name: 'Create account', exact: true })
    .click();
  await page.getByLabel('Email address').fill(email);
  await page.getByLabel('Password', { exact: true }).fill(password);
  await page.locator('button[type="submit"]').click();
  await expect(
    page.getByText(
      'If this address can be used, an email with the next step will arrive shortly.',
    ),
  ).toBeVisible();
  const mailDirectory =
    process.env.REPORT_MAIL_DIRECTORY ?? path.resolve('.runtime/mail');
  const message = readdirSync(mailDirectory)
    .map(
      (file) =>
        JSON.parse(readFileSync(path.join(mailDirectory, file), 'utf8')) as {
          to: string;
          link: string;
        },
    )
    .find((item) => item.to === email);
  expect(message).toBeDefined();
  await page.goto(message!.link);
  await page.getByRole('button', { name: 'Verify email', exact: true }).click();
  await expect(
    page.getByText('Your email has been verified. You can sign in now.'),
  ).toBeVisible();
  await page.getByLabel('Email address').fill(email);
  await page.getByLabel('Password', { exact: true }).fill(password);
  await page.locator('button[type="submit"]').click();
  await expect(page.getByText('Email verified', { exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: email })).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading', { name: email })).toBeVisible();
  await page.getByRole('button', { name: 'Sign out' }).click();
  await expect(page.getByLabel('Email address')).toBeVisible();
  await page.getByRole('button', { name: 'Forgot your password?' }).click();
  await page.getByLabel('Email address').fill(email);
  await page.locator('button[type="submit"]').click();
  await expect(
    page.getByText(
      'If the account exists, a password reset link will arrive shortly.',
    ),
  ).toBeVisible();
  const recovery = readdirSync(mailDirectory)
    .map(
      (file) =>
        JSON.parse(readFileSync(path.join(mailDirectory, file), 'utf8')) as {
          to: string;
          link: string;
        },
    )
    .find((item) => item.to === email && item.link.includes('/account/reset'));
  expect(recovery).toBeDefined();
  await page.goto(recovery!.link);
  const replacementPassword = 'An afternoon walk through the garden';
  await page
    .getByLabel('New password', { exact: true })
    .fill(replacementPassword);
  await page.locator('button[type="submit"]').click();
  await expect(
    page.getByText(
      'Your password has been updated. Sign in with your new password.',
    ),
  ).toBeVisible();
  await page.getByLabel('Email address').fill(email);
  await page.getByLabel('Password', { exact: true }).fill(replacementPassword);
  await page.locator('button[type="submit"]').click();
  await expect(page.getByRole('heading', { name: email })).toBeVisible();
  await page.getByRole('button', { name: 'Sign out' }).click();
  await expect(page.getByLabel('Email address')).toBeVisible();
});
