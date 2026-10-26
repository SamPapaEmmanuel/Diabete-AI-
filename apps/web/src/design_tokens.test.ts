import { readFileSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

const sourceDirectory = dirname(fileURLToPath(import.meta.url));

function styleFiles(directory: string): string[] {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = join(directory, entry.name);
    return entry.isDirectory()
      ? styleFiles(path)
      : /\.(css|scss|sass|less)$/.test(entry.name) ||
          (/tokens?\.(ts|json)$/.test(entry.name) &&
            !entry.name.includes('.test.'))
        ? [path]
        : [];
  });
}

function luminance(hex: string): number {
  const values = hex.match(/[a-f0-9]{2}/gi)?.map((value) => {
    const component = parseInt(value, 16) / 255;
    return component <= 0.04045
      ? component / 12.92
      : ((component + 0.055) / 1.055) ** 2.4;
  });
  if (!values || values.length !== 3) throw new Error('Invalid colour token');
  return values[0]! * 0.2126 + values[1]! * 0.7152 + values[2]! * 0.0722;
}

describe('design contracts', () => {
  it('rejects gradients in every application token or stylesheet', () => {
    const paths = styleFiles(sourceDirectory);
    expect(paths.length).toBeGreaterThan(0);
    for (const path of paths)
      expect(readFileSync(path, 'utf8'), path).not.toMatch(
        /[\w-]*gradient\s*\(/i,
      );
  });

  it('keeps text and control tokens accessible in both themes', () => {
    const source = readFileSync(
      join(sourceDirectory, 'design_tokens.css'),
      'utf8',
    );
    const blocks = source.matchAll(/:root[^{}]*\{([^}]+)\}/g);
    let themes = 0;
    for (const block of blocks) {
      themes += 1;
      const colours = Object.fromEntries(
        [...block[1]!.matchAll(/--colour-([\w-]+):\s*(#[a-f0-9]{6});/gi)].map(
          (match) => [match[1], match[2]],
        ),
      );
      for (const [foreground, background, minimum] of [
        ['text', 'background', 4.5],
        ['text', 'surface', 4.5],
        ['muted', 'background', 4.5],
        ['muted', 'surface', 4.5],
        ['on-accent', 'accent', 4.5],
        ['accent', 'surface', 4.5],
        ['control', 'surface', 3],
        ['control', 'background', 3],
        ['status-high-text', 'status-high-surface', 4.5],
        ['status-intermediate-text', 'status-intermediate-surface', 4.5],
      ] as const) {
        const a = luminance(colours[foreground]!);
        const b = luminance(colours[background]!);
        expect(
          (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05),
          `${foreground}/${background}`,
        ).toBeGreaterThanOrEqual(minimum);
      }
    }
    expect(themes).toBe(2);
  });
});
