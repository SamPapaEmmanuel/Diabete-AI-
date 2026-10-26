import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { ReportWorkspace } from './report_workspace';

describe('report workspace', () => {
  it('shows the report empty state without fabricating values or accepting uploads', async () => {
    render(<ReportWorkspace />);
    expect(
      screen.getByRole('heading', {
        level: 1,
        name: 'Understand your lab report.',
      }),
    ).toBeVisible();
    expect(screen.getByRole('button', { name: 'Add a report' })).toBeDisabled();
    expect(
      screen.getByText(
        'Your reviewed lab values will appear here. Nothing has been uploaded.',
      ),
    ).toBeVisible();
    await screen.findByText('Service connected');
    expect(screen.getByRole('link', { name: 'Report' })).toHaveAttribute(
      'aria-current',
      'page',
    );
  });

  it('navigates to a truthful guest history state and moves focus to main content', async () => {
    const user = userEvent.setup();
    render(<ReportWorkspace />);
    await user.click(screen.getByRole('link', { name: 'History' }));
    expect(
      await screen.findByRole('heading', {
        name: 'Your history starts with an account',
      }),
    ).toBeVisible();
    await waitFor(() => expect(screen.getByRole('main')).toHaveFocus());
  });

  it('stores only the public theme preference', async () => {
    const user = userEvent.setup();
    render(<ReportWorkspace />);
    await user.selectOptions(
      screen.getByRole('combobox', { name: 'Colour theme' }),
      'dark',
    );
    expect(document.documentElement).toHaveAttribute('data-theme', 'dark');
    expect(localStorage.getItem('report-theme')).toBe('dark');
    expect(localStorage.length).toBe(1);
  });

  it('announces offline state and prevents account submission', async () => {
    window.location.hash = '#/account';
    render(<ReportWorkspace />);
    await screen.findByLabelText('Email address');
    window.dispatchEvent(new Event('offline'));
    await screen.findByText('Reconnect before submitting this form.');
    expect(
      screen.getByRole('button', {
        name: 'Sign in',
        pressed: true,
      }),
    ).toBeEnabled();
    expect(
      screen
        .getAllByRole('button', { name: 'Sign in' })
        .some((button) => button.hasAttribute('disabled')),
    ).toBe(true);
  });
});
