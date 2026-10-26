import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, beforeEach, vi } from 'vitest';

beforeEach(() => {
  window.location.hash = '#/report';
  localStorage.clear();
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: string) => {
      if (input.endsWith('/account'))
        return new Response(
          JSON.stringify({ message_key: 'auth.sign_in_required' }),
          { status: 401 },
        );
      return new Response(JSON.stringify({ status: 'ready' }));
    }),
  );
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
