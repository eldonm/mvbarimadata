/**
 * E2E: sources page filters + sort must actually change visible DOM order/set.
 * Run: node site/assets/source-browser.e2e.mjs
 * Needs: local server on :8765 and puppeteer-core (see /tmp/mvbarima-test).
 */
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';

const require = createRequire('/tmp/mvbarima-test/node_modules/puppeteer-core/package.json');
const puppeteer = require('/tmp/mvbarima-test/node_modules/puppeteer-core');

const BASE = process.env.SITE_URL || 'http://127.0.0.1:8765/sources.html';
const CHROME =
  process.env.CHROME_PATH ||
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

function visibleMeta(page) {
  return page.evaluate(() => {
    const srcs = [...document.querySelectorAll('.src')].filter(
      (el) => getComputedStyle(el).display !== 'none' && !el.hidden
    );
    return srcs.map((el) => ({
      outlet: el.getAttribute('data-outlet'),
      kind: el.getAttribute('data-kind'),
      date: el.getAttribute('data-date'),
      title: el.querySelector('h3')?.textContent?.trim() || '',
    }));
  });
}

function countText(page) {
  return page.evaluate(() => document.getElementById('f-count').textContent);
}

async function setSelect(page, id, value) {
  await page.evaluate(
    ({ id, value }) => {
      const el = document.getElementById(id);
      el.value = value;
      el.dispatchEvent(new Event('change', { bubbles: true }));
      el.dispatchEvent(new Event('input', { bubbles: true }));
    },
    { id, value }
  );
}

async function setSearch(page, value) {
  await page.evaluate((value) => {
    const el = document.getElementById('f-q');
    el.value = value;
    el.dispatchEvent(new Event('input', { bubbles: true }));
  }, value);
}

async function reset(page) {
  await page.evaluate(() => document.getElementById('f-clear').click());
}

function isSorted(arr, cmp) {
  for (let i = 1; i < arr.length; i++) {
    if (cmp(arr[i - 1], arr[i]) > 0) return false;
  }
  return true;
}

const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: true,
  args: ['--no-sandbox'],
});
const page = await browser.newPage();
await page.goto(BASE + '?e2e=' + Date.now(), { waitUntil: 'networkidle0' });

const failures = [];
function check(name, ok, detail) {
  if (!ok) failures.push(`${name}: ${detail || 'failed'}`);
  else console.log('ok —', name);
}

try {
  await reset(page);
  let rows = await visibleMeta(page);
  check('baseline all visible', rows.length === 192, `got ${rows.length}`);
  check(
    'baseline count label',
    (await countText(page)).includes('192 sources shown of 192'),
    await countText(page)
  );

  // --- SORT: oldest ---
  await setSelect(page, 'f-sort', 'oldest');
  rows = await visibleMeta(page);
  check(
    'oldest: date ascending',
    isSorted(rows, (a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0)),
    `first=${rows[0]?.date} last=${rows[rows.length - 1]?.date}`
  );
  check(
    'oldest: first is undated or earliest',
    rows[0]?.date === '0000-00-00' || rows[0]?.date <= rows[rows.length - 1]?.date,
    rows[0]?.date
  );
  // Critical: must differ from newest-first default head
  check(
    'oldest: not still newest-first head',
    rows[0]?.date !== '2026-07-26',
    `head still ${rows[0]?.date} / ${rows[0]?.title?.slice(0, 40)}`
  );

  // --- SORT: newest ---
  await setSelect(page, 'f-sort', 'newest');
  rows = await visibleMeta(page);
  check(
    'newest: date descending',
    isSorted(rows, (a, b) => (a.date > b.date ? -1 : a.date < b.date ? 1 : 0)),
    `first=${rows[0]?.date} last=${rows[rows.length - 1]?.date}`
  );
  check('newest: head is 2026-07-26', rows[0]?.date === '2026-07-26', rows[0]?.date);

  // --- SORT: outlet ---
  await setSelect(page, 'f-sort', 'outlet');
  rows = await visibleMeta(page);
  check(
    'outlet: alpha by outlet',
    isSorted(rows, (a, b) => a.outlet.localeCompare(b.outlet) || (a.date < b.date ? 1 : -1)),
    `first=${rows[0]?.outlet} last=${rows[rows.length - 1]?.outlet}`
  );
  const datebarsVisible = await page.evaluate(
    () =>
      [...document.querySelectorAll('.datebar')].filter(
        (b) => getComputedStyle(b).display !== 'none'
      ).length
  );
  check('outlet: datebars hidden', datebarsVisible === 0, `visible bars=${datebarsVisible}`);

  // --- SORT: title ---
  await setSelect(page, 'f-sort', 'title');
  rows = await visibleMeta(page);
  check(
    'title: alpha by title',
    isSorted(rows, (a, b) => a.title.toLowerCase().localeCompare(b.title.toLowerCase())),
    `first=${rows[0]?.title?.slice(0, 30)}`
  );

  // Switch back to newest after outlet reorder — must restore chrono order
  await setSelect(page, 'f-sort', 'outlet');
  await setSelect(page, 'f-sort', 'newest');
  rows = await visibleMeta(page);
  check(
    'newest after outlet: date descending again',
    isSorted(rows, (a, b) => (a.date > b.date ? -1 : a.date < b.date ? 1 : 0)),
    `first=${rows[0]?.date} / ${rows[0]?.outlet}`
  );

  // --- FILTER: outlet ---
  await reset(page);
  await setSelect(page, 'f-outlet', 'Kaieteur News');
  rows = await visibleMeta(page);
  check('outlet filter count', rows.length === 32, `got ${rows.length}`);
  check(
    'outlet filter only Kaieteur',
    rows.every((r) => r.outlet === 'Kaieteur News'),
    rows.find((r) => r.outlet !== 'Kaieteur News')?.outlet
  );
  check(
    'outlet filter label',
    (await countText(page)).startsWith('32 sources shown'),
    await countText(page)
  );

  // --- FILTER: kind ---
  await reset(page);
  await setSelect(page, 'f-kind', 'International press');
  rows = await visibleMeta(page);
  check(
    'kind filter only International press',
    rows.length > 0 && rows.every((r) => r.kind === 'International press'),
    `n=${rows.length} bad=${rows.find((r) => r.kind !== 'International press')?.kind}`
  );

  await reset(page);
  await setSelect(page, 'f-kind', 'Historical & context');
  rows = await visibleMeta(page);
  check(
    'kind Historical & context',
    rows.length > 0 && rows.every((r) => r.kind === 'Historical & context'),
    `n=${rows.length}`
  );

  // --- FILTER: period ---
  await reset(page);
  await setSelect(page, 'f-period', 'disaster');
  rows = await visibleMeta(page);
  check(
    'period disaster dates',
    rows.every((r) => r.date >= '2026-07-18' && r.date <= '2026-07-21'),
    rows.find((r) => r.date < '2026-07-18' || r.date > '2026-07-21')?.date
  );
  check('period disaster nonempty', rows.length > 0, String(rows.length));

  await setSelect(page, 'f-period', 'pre');
  rows = await visibleMeta(page);
  check(
    'period pre dates',
    rows.every((r) => r.date < '2026-07-18'),
    rows.find((r) => r.date >= '2026-07-18')?.date
  );

  await setSelect(page, 'f-period', 'reckoning');
  rows = await visibleMeta(page);
  check(
    'period reckoning dates',
    rows.every((r) => r.date >= '2026-07-22'),
    rows.find((r) => r.date < '2026-07-22')?.date
  );

  // --- FILTER: search ---
  await reset(page);
  await setSearch(page, 'manifest');
  rows = await visibleMeta(page);
  const searchN = rows.length;
  check('search manifest nonempty', searchN > 0 && searchN < 192, String(searchN));
  check(
    'search label matches',
    (await countText(page)).startsWith(searchN + ' sources shown'),
    await countText(page)
  );

  // --- COMBINED: outlet + period + sort oldest ---
  await reset(page);
  await setSelect(page, 'f-outlet', 'Kaieteur News');
  await setSelect(page, 'f-period', 'reckoning');
  await setSelect(page, 'f-sort', 'oldest');
  rows = await visibleMeta(page);
  check(
    'combined outlet+period',
    rows.every((r) => r.outlet === 'Kaieteur News' && r.date >= '2026-07-22'),
    `n=${rows.length}`
  );
  check(
    'combined sorted oldest',
    isSorted(rows, (a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0)),
    `first=${rows[0]?.date} last=${rows[rows.length - 1]?.date}`
  );

  // --- empty state ---
  await reset(page);
  await setSearch(page, 'zzzxnotaword999');
  rows = await visibleMeta(page);
  const emptyShown = await page.evaluate(() => {
    const e = document.getElementById('srcempty');
    return e && getComputedStyle(e).display !== 'none' && !e.hidden;
  });
  check('empty: no cards', rows.length === 0, String(rows.length));
  check('empty: message visible', emptyShown, String(emptyShown));

  await reset(page);
  rows = await visibleMeta(page);
  check('reset restores all', rows.length === 192, String(rows.length));
} finally {
  await browser.close();
}

if (failures.length) {
  console.error('\nFAILURES:');
  failures.forEach((f) => console.error(' -', f));
  process.exit(1);
}
console.log('\nAll source browser checks passed.');
