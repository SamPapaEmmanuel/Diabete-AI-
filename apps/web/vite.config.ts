import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';
import copy from '../../content/locales/en-GH.json' with { type: 'json' };

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'report-document-title',
      transformIndexHtml: (html) =>
        html.replace('%REPORT_TITLE%', copy['app.title']),
    },
  ],
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test_setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
    restoreMocks: true,
  },
});
