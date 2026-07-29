#!/usr/bin/env python3
"""Facebook cards: one per question, carrying the question and its answer.

The card is the post. Nothing here is written for the card - the question and
the answer are lifted verbatim from the published page (qa.json), converted to
plain ASCII, so what circulates on Facebook is what the archive actually says.

Two shapes: 1080x1080 for the feed, where square takes the most vertical space
on a phone, and 1200x630 for link posts.
"""
import json, os, subprocess

OUT = os.path.dirname(os.path.abspath(__file__))
QA = json.load(open(os.path.join(OUT, 'qa.json')))

CSS = """
* { box-sizing:border-box; margin:0; padding:0; }
body { background:#f6f5f1; color:#0b0b0b;
  font-family:system-ui,-apple-system,"Segoe UI","Helvetica Neue",Arial,sans-serif;
  display:flex; flex-direction:column; }
.mast { display:flex; align-items:flex-end; justify-content:space-between;
  border-bottom:5px solid #0b0b0b; padding-bottom:15px; flex:none; }
.mark { font-weight:800; letter-spacing:-0.02em; line-height:1; }
.sub { font-weight:700; letter-spacing:0.2em; text-transform:uppercase; color:#8a8880; margin-top:6px; }
.kick { font-weight:750; letter-spacing:0.17em; text-transform:uppercase; color:#2a78d6; text-align:right; }
.body { flex:1; display:flex; flex-direction:column; justify-content:center; min-height:0;
  padding:6px 0; }
.qline { display:flex; gap:18px; align-items:baseline; }
.qn { color:#2a78d6; font-weight:800; line-height:1; flex:none; }
h1 { font-weight:800; letter-spacing:-0.025em; line-height:1.08; }
.lede { font-weight:750; color:#0b0b0b; }
.lede .hit { box-shadow:inset 0 -0.34em 0 rgba(42,120,214,0.20); }
p.more { color:#46453f; }
.foot { display:flex; align-items:center; justify-content:space-between; flex:none;
  border-top:1px solid rgba(11,11,11,0.16); color:#6b6a65; }
.foot b { color:#0b0b0b; font-weight:750; }
.rule { background:#2a78d6; flex:none; }
"""

WIDE = dict(w=1200, h=630, pad='46px 60px 40px', mark=34, sub=13, kick=13,
            qn=34, h1=42, lede=27, more=21, foot=16, rule='64px 5px',
            gap1=22, gap2=20, gap3=16, footpad=14)
SQ = dict(w=1080, h=1080, pad='70px 74px 62px', mark=42, sub=15, kick=15,
          qn=60, h1=72, lede=46, more=34, foot=19, rule='80px 6px',
          gap1=40, gap2=34, gap3=26, footpad=18)


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def card(s, item, hit_words=1):
    """hit_words: how many leading sentences of the answer to set as the lede."""
    a = item['paras'][0]
    # The first sentence of an answer is the answer; the rest is its support.
    cut = a.find('. ') + 1
    lede, rest = (a[:cut].strip(), a[cut:].strip()) if 0 < cut < len(a) else (a, '')
    rw, rh = s['rule'].split()
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}
html,body {{ width:{s['w']}px; height:{s['h']}px; }}
body {{ padding:{s['pad']}; --k:1; }}
.mark {{ font-size:{s['mark']}px; }} .sub {{ font-size:{s['sub']}px; }}
.kick {{ font-size:{s['kick']}px; }}
.rule {{ width:{rw}; height:{rh}; margin-bottom:{s['gap1']}px; }}
.qn {{ font-size:calc({s['qn']}px * var(--k)); }}
h1 {{ font-size:calc({s['h1']}px * var(--k)); }}
.lede {{ font-size:calc({s['lede']}px * var(--k)); line-height:1.24;
  margin-top:calc({s['gap2']}px * var(--k)); }}
p.more {{ font-size:calc({s['more']}px * var(--k)); line-height:1.42;
  margin-top:calc({s['gap3']}px * var(--k)); }}
.rule {{ margin-bottom:calc({s['gap1']}px * var(--k)); }}
.foot {{ font-size:{s['foot']}px; padding-top:{s['footpad']}px; }}
</style></head><body>
<div class="mast">
  <div><div class="mark">MV Barima</div><div class="sub">Documented record</div></div>
  <div class="kick">Question {item['n']} of 5</div>
</div>
<div class="body">
  <div class="rule"></div>
  <div class="qline"><span class="qn">{item['n']}</span><h1>{esc(item['q'])}</h1></div>
  <div class="lede"><span class="hit">{esc(lede)}</span></div>
  {f'<p class="more">{esc(rest)}</p>' if rest else ''}
</div>
<div class="foot"><span>Answered from 209 published documents</span>
  <span><b>mvbarimadata.pages.dev</b></span></div>
</body></html>"""


def build():
    jobs = []
    for shape, s in (('wide', WIDE), ('square', SQ)):
        for it in QA:
            p = os.path.join(OUT, f"_q{it['n']}-{shape}.html")
            open(p, 'w', encoding='utf-8').write(card(s, it))
            jobs.append({'html': p, 'png': os.path.join(OUT, f"fb-q{it['n']}-{shape}.png"),
                         'w': s['w'], 'h': s['h']})
    pw = subprocess.run(['node', '-e', "process.stdout.write(require.resolve('playwright'))"],
                        capture_output=True, text=True, check=True).stdout.strip()
    r = os.path.join(OUT, '_r.mjs')
    open(r, 'w', encoding='utf-8').write("import pw from '" + pw + """';
const { chromium } = pw;
const jobs = JSON.parse(process.argv[2]);
const br = await chromium.launch();
let bad = 0;
for (const j of jobs) {
  const pg = await br.newPage({ viewport: { width: j.w, height: j.h }, deviceScaleFactor: 2 });
  await pg.goto('file://' + j.html, { waitUntil: 'load' });
  // The body is a flex child with min-height:0, so it clips silently instead of
  // scrolling the page. Measure the block itself and shrink until it fits.
  const k = await pg.evaluate(() => {
    const b = document.querySelector('.body');
    let k = 1;
    for (let i = 0; i < 26 && b.scrollHeight > b.clientHeight + 1; i++) {
      k -= 0.03;
      document.body.style.setProperty('--k', k.toFixed(3));
    }
    return { k, fits: b.scrollHeight <= b.clientHeight + 1 };
  });
  if (!k.fits) { console.log('STILL OVERFLOWING ' + j.png.split('/').pop()); bad++; }
  else if (k.k < 0.999) console.log('  fitted ' + j.png.split('/').pop() + ' at k=' + k.k.toFixed(2));
  await pg.screenshot({ path: j.png });
  await pg.close();
}
await br.close();
console.log(bad ? bad + ' OVERFLOWING' : 'all cards fit');
""")
    subprocess.run(['node', r, json.dumps(jobs)], check=True)
    for j in jobs:
        os.remove(j['html'])
    os.remove(r)
    print('cards:', len(jobs))


if __name__ == '__main__':
    build()
