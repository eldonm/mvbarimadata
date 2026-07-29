#!/usr/bin/env python3
"""Render one Open Graph card per page.

Social platforms crop and scale aggressively, so the cards are built at the
canonical 1200x630 with large type and no detail that would survive being shown
at 300px wide. Each card carries the site's masthead treatment, the page title,
one line of subtext, and a footing line of provenance — the same institutional
furniture as the site, so a shared link looks like the thing it links to.

Rendered with the same browser the site is tested in, so the type is the type a
reader actually sees rather than an approximation from an image library.
"""
import json
import os
import subprocess
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'og')

TEMPLATE = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
  * { box-sizing:border-box; margin:0; padding:0; }
  html,body { width:1200px; height:630px; }
  body { background:%(paper)s; color:#0b0b0b;
    font-family:system-ui,-apple-system,"Segoe UI","Helvetica Neue",Arial,sans-serif;
    display:flex; flex-direction:column; padding:62px 68px 54px; }
  .mast { display:flex; align-items:flex-end; justify-content:space-between;
    border-bottom:5px solid #0b0b0b; padding-bottom:18px; }
  .mark { font-size:40px; font-weight:800; letter-spacing:-0.02em; line-height:1; }
  .sub { font-size:15px; font-weight:700; letter-spacing:0.22em; text-transform:uppercase;
    color:#8a8880; margin-top:7px; }
  .kicker { font-size:15px; font-weight:750; letter-spacing:0.2em; text-transform:uppercase;
    color:%(accent)s; text-align:right; max-width:430px; line-height:1.5; }
  .body { flex:1; display:flex; flex-direction:column; justify-content:center; padding:8px 0; }
  h1 { font-size:%(tsize)spx; font-weight:800; letter-spacing:-0.028em; line-height:1.06;
    max-width:1010px; }
  p.desc { margin-top:26px; font-size:26px; line-height:1.42; color:#3f3e3b; max-width:940px; }
  .foot { display:flex; align-items:center; justify-content:space-between;
    border-top:1px solid rgba(11,11,11,0.16); padding-top:18px;
    font-size:17px; color:#6b6a65; }
  .foot b { color:#0b0b0b; font-weight:750; }
  .rule { width:74px; height:5px; background:%(accent)s; margin-bottom:26px; }
</style></head><body>
  <div class="mast">
    <div><div class="mark">MV Barima</div><div class="sub">Documented record</div></div>
    <div class="kicker">%(kicker)s</div>
  </div>
  <div class="body"><div class="rule"></div><h1>%(title)s</h1><p class="desc">%(desc)s</p></div>
  <div class="foot"><span>%(footl)s</span><span><b>mvbarimadata.pages.dev</b></span></div>
</body></html>"""


def esc(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('&amp;middot;', '&middot;').replace('&amp;amp;', '&amp;')
             .replace('&amp;rsquo;', '&rsquo;').replace('&amp;ndash;', '&ndash;')
             .replace('&amp;mdash;', '&mdash;'))


def trim(t, n):
    t = ' '.join(t.split())
    if len(t) <= n:
        return t
    cut = t[:n]
    return cut[:cut.rfind(' ')].rstrip('.,;:') + '…'


def build(cards, n_docs, built):
    os.makedirs(OUT, exist_ok=True)
    jobs = []
    for slug, kicker, title, desc in cards:
        title = esc(trim(title, 78))
        size = 66 if len(title) > 52 else (76 if len(title) > 34 else 86)
        html = TEMPLATE % dict(
            paper='#f6f5f1', accent='#2a78d6', kicker=esc(kicker),
            title=title, desc=esc(trim(desc, 168)), tsize=size,
            footl=esc('%s published documents · %s' % (n_docs, built)))
        p = os.path.join(OUT, slug + '.html')
        with open(p, 'w', encoding='utf-8') as f:
            f.write(html)
        jobs.append({'html': p, 'png': os.path.join(OUT, slug + '.png')})

    # Playwright is installed globally and Node's ESM resolver will not find it
    # from inside the site tree, so import it by its resolved path.
    pw = subprocess.run(['node', '-e', "process.stdout.write(require.resolve('playwright'))"],
                        capture_output=True, text=True, check=True).stdout.strip()
    script = os.path.join(OUT, '_render.mjs')
    with open(script, 'w', encoding='utf-8') as f:
        f.write("""import pw from '""" + pw + """';
const { chromium } = pw;
const jobs = JSON.parse(process.argv[2]);
const br = await chromium.launch();
const pg = await br.newPage({ viewport: { width: 1200, height: 630 },
                              deviceScaleFactor: 1 });
for (const j of jobs) {
  await pg.goto('file://' + j.html, { waitUntil: 'load' });
  await pg.screenshot({ path: j.png });
}
await br.close();
""")
    subprocess.run(['node', script, json.dumps(jobs)], check=True)
    for j in jobs:
        os.remove(j['html'])
    os.remove(script)
    return [os.path.basename(j['png']) for j in jobs]


if __name__ == '__main__':
    sys.exit('imported by build_site.py')
