/**
 * Regression: .src { display:block } and .datebar { display:flex } override
 * the HTML hidden attribute, so source filters update the count but leave
 * every card visible. Author CSS must hide .is-filtered-out items.
 */
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const dir = dirname(fileURLToPath(import.meta.url));
const css = readFileSync(join(dir, 'style.css'), 'utf8');
const js = readFileSync(join(dir, 'site.js'), 'utf8');

assert.match(
  css,
  /\.src\.is-filtered-out[^{]*\{[^}]*display\s*:\s*none\s*!important/i,
  'style.css must hide .src.is-filtered-out with display:none !important'
);
assert.match(
  css,
  /\.datebar\.is-filtered-out/,
  'style.css must also hide filtered-out datebars'
);
assert.match(
  js,
  /classList\.toggle\(\s*['"]is-filtered-out['"]/,
  'site.js must toggle is-filtered-out when applying filters'
);
assert.match(
  js,
  /\.style\.display\s*=\s*ok\s*\?\s*['"]['"]\s*:\s*['"]none['"]/,
  'site.js must set style.display so author CSS cannot override hidden'
);

console.log('ok — filtered-out hide rule + JS toggle present');
