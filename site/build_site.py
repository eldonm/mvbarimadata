#!/usr/bin/env python3
"""Build the public MV Barima research site from the private full-text archive.

Publishes metadata, research summaries, extracted claims and short attributed
quotations only. Full article text is NOT republished — every source page links
out to the publisher. Official/state documents are treated the same way here for
consistency of presentation.
"""
import glob, json, os, re, html, shutil, collections
import yaml
import markdown as md

ARCHIVE = '/home/claude/mvb/archive'
DELIV   = '/home/claude/mvb/site_content'   # neutralised site copy, not the private working notes
OUT     = '/home/claude/mvb/site'
BUILT   = 'Sunday 26 July 2026, last revised Tuesday 28 July 2026'

# ---------------------------------------------------------------- parse archive
def parse_front(path):
    txt = open(path, encoding='utf-8', errors='replace').read()
    if not txt.startswith('---'):
        return {}
    end = txt.find('\n---', 3)
    block = txt[3:end] if end > 0 else txt[3:]
    try:
        d = yaml.safe_load(block)
        if isinstance(d, dict):
            return d
    except Exception:
        pass
    d, key = {}, None
    for ln in block.splitlines():
        m = re.match(r'^([a-z_]+):\s*(.*)$', ln)
        if m:
            key = m.group(1); val = m.group(2).strip().strip('"')
            d[key] = val if val else []
        elif ln.strip().startswith('- ') and key:
            if not isinstance(d.get(key), list):
                d[key] = []
            d[key].append(ln.strip()[2:].strip().strip('"'))
    return d

def listify(v):
    if v is None or v == '' or v == []:
        return []
    if isinstance(v, list):
        out = []
        for x in v:
            if isinstance(x, dict):
                out += [f'{k}: {vv}' for k, vv in x.items()]
            elif str(x).strip() and str(x).strip().lower() not in ('none', 'null'):
                out.append(str(x).strip())
        return out
    s = str(v).strip()
    return [] if s.lower() in ('none', 'null', '') else [s]

def scalar(v):
    if v is None or isinstance(v, (list, dict)):
        return ''
    s = str(v).strip()
    return '' if s.lower() in ('none', 'null', 'unknown') else s

TIER_KIND = {
    'official-primary': 'Official document',
    'domestic-press': 'Guyanese press',
    'international-press': 'International press',
    'regional-press': 'Regional press',
    'civil-society': 'Civil society',
    'historical': 'Historical & context',
    'reference': 'Historical & context',
    'analysis': 'Historical & context',
}
def kind_of(rec):
    t = (rec.get('tier') or '').lower()
    for key, val in TIER_KIND.items():
        if key in t:
            return val
    st = (rec.get('stream') or '').lower()
    if 'official' in st: return 'Official document'
    if 'vessel' in st or 'press-capacity' in st: return 'Historical & context'
    if 'international' in st: return 'International press'
    return 'Guyanese press'

# manifests: research annotations
ann = {}
for mf in sorted(glob.glob(os.path.join(ARCHIVE, '_manifest_*.jsonl'))):
    for ln in open(mf, encoding='utf-8'):
        ln = ln.strip()
        if not ln:
            continue
        try:
            o = json.loads(ln)
        except Exception:
            continue
        fn = str(o.get('filename', '')).split('/')[-1]
        if fn:
            ann[fn] = o

# neutralised, publication-facing summaries; these override the working-note summaries
NEUTRAL = {}
for _np in sorted(glob.glob(os.path.join(ARCHIVE, '_summaries_*.jsonl'))):
    for ln in open(_np, encoding='utf-8'):
        ln = ln.strip()
        if not ln:
            continue
        try:
            o = json.loads(ln)
        except Exception:
            continue
        fn = str(o.get('filename', '')).split('/')[-1]
        s = (o.get('summary') or '').strip()
        if fn and s:
            NEUTRAL[fn] = s
print(f'neutral summaries loaded: {len(NEUTRAL)}')

records = []
for path in sorted(glob.glob(os.path.join(ARCHIVE, '*.md'))):
    fn = os.path.basename(path)
    if fn.startswith('_'):
        continue
    fm = parse_front(path)
    a = ann.get(fn, {})
    pub = scalar(fm.get('published')) or scalar(a.get('published')) or '0000-00-00'
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', pub):
        pub = '0000-00-00'
    rec = {
        'slug': re.sub(r'[^a-z0-9\-]+', '-', fn[:-3].lower()).strip('-'),
        'file': fn,
        'title': scalar(fm.get('title')) or scalar(a.get('title')) or fn[:-3],
        'outlet': scalar(fm.get('outlet')) or scalar(a.get('outlet')) or 'Unknown',
        'author': scalar(fm.get('author')),
        'published': pub,
        'published_time': scalar(fm.get('published_time')),
        'url': scalar(fm.get('url')) or scalar(a.get('url')),
        'genre': scalar(fm.get('genre')) or scalar(a.get('genre')),
        'tier': scalar(fm.get('tier')),
        'stream': scalar(fm.get('stream')) or scalar(a.get('stream')),
        'summary': NEUTRAL.get(fn) or scalar(a.get('summary')),
        'claims': listify(fm.get('key_claims')) or listify(a.get('key_facts')),
        'facts': listify(a.get('key_facts')),
        'quotes': listify(a.get('notable_quotes')),
        'figures': scalar(fm.get('casualty_figures_cited')) or scalar(a.get('casualty_figures')),
        'argument': scalar(fm.get('argument')) or scalar(a.get('argument')),
        'position': scalar(fm.get('official_position')) or scalar(a.get('official_position')),
        'warnings': listify(fm.get('prior_warnings')) or listify(a.get('prior_warnings')),
        'vessel': listify(fm.get('vessel_facts')) or listify(a.get('vessel_facts')),
        'actors': listify(fm.get('actors_named')) or listify(a.get('actors_named')),
        'fidelity': scalar(fm.get('capture_fidelity')) or scalar(fm.get('fidelity')) or scalar(a.get('capture_fidelity')),
    }
    rec['kind'] = kind_of(rec)
    fid = rec['fidelity'].upper()
    rec['flagged'] = bool(rec['fidelity']) and not fid.startswith(('VERBATIM', 'TRUE'))
    records.append(rec)

# publisher concentration, computed so the overview copy cannot drift
_oc = collections.Counter(r['outlet'] for r in records)
STATE_OUTLETS = ('Guyana Chronicle', 'Department of Public Information')
N_CHRON  = _oc.get('Guyana Chronicle', 0)
N_DPI    = _oc.get('Department of Public Information', 0)
N_STATE  = N_CHRON + N_DPI
N_KAI    = _oc.get('Kaieteur News', 0)
N_TOP3   = sum(n for _, n in _oc.most_common(3))
N_OUTLET = len(_oc)

records.sort(key=lambda r: (r['published'], r['outlet'], r['title']), reverse=True)
by_slug = {r['slug']: r for r in records}
assert len(by_slug) == len(records), 'slug collision'
print(f'{len(records)} source records')

# ------------------------------------------------------------------- templates
E = html.escape
def esc(s): return E(str(s), quote=True)

# grouped so eight items stay legible: the record, then voices, then analysis,
# then the apparatus behind the archive. Separators are CSS-only, no JS.
NAV_GROUPS = [
    ('The record',   [('index.html', 'Overview'), ('timeline.html', 'Chronology'),
                      ('facts.html', 'The figures')]),
    ('Voices',       [('positions.html', 'Positions')]),
    ('Analysis',     [('questions.html', 'Questions')]),
    ('The archive',  [('sources.html', 'Documents'), ('about.html', 'Method &amp; gaps'),
                      ('changelog.html', 'Revisions')]),
]
NAV = [item for _, items in NAV_GROUPS for item in items]

CURATTR = ' aria-current="page"'
def head(title, desc, cur, depth=0):
    p = '../' * depth
    parts = []
    for gi, (gname, items) in enumerate(NAV_GROUPS):
        if gi:
            parts.append('<span class="navsep" role="presentation" aria-hidden="true"></span>')
        for h, t in items:
            parts.append('<a href="{}{}"{}{}>{}</a>'.format(
                p, h, CURATTR if h == cur else '',
                ' data-navgroup="{}"'.format(gname), t))
    nav = ''.join(parts)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index,follow">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<link rel="stylesheet" href="{p}assets/style.css">
<script src="{p}assets/site.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar"><div class="topbar-in">
  <a class="brand" href="{p}index.html">MV Barima <span>&middot; research archive</span></a>
  <nav class="main" aria-label="Main">{nav}</nav>
  <button class="themebtn" type="button">Dark</button>
</div></header>
<main id="main">
'''

FOOT_T = '''</main>
<footer class="site"><div class="footin">
  <div class="cols">
    <div>
      <h4>About this archive</h4>
      <p>An independent, citation-first record of the sinking of the <em>MV Barima</em> on the night of
      Saturday 18 July 2026, compiled from {n} published documents and checked line by line against them.
      It is not affiliated with the Government of Guyana, the Transport &amp; Harbours Department, any
      political party, or any news organisation.</p>
      <p>Compiled {built}. The Commission of Inquiry&rsquo;s members were named on 26 July 2026, its establishing instrument was not
      yet gazetted, and figures were still moving. Read <a href="{p}about.html">Method &amp; gaps</a> before citing anything here.</p>
      <p>This site records what the sources say and who said it. It does not advance an explanation of the
      cause, and it makes no recommendation.</p>
    </div>
    <div>
      <h4>Navigate</h4>
      <ul>
        <li><a href="{p}index.html">Overview and figures</a></li>
        <li><a href="{p}timeline.html">Chronology, 1936–2026</a></li>
        <li><a href="{p}facts.html">The figures, source by source</a></li>
        <li><a href="{p}positions.html">Positions and proposals</a></li>
        <li><a href="{p}sources.html">All {n} documents</a></li>
        <li><a href="{p}about.html">Method, gaps and corrections</a></li>
        <li><a href="{p}changelog.html">Revisions</a></li>
      </ul>
    </div>
    <div>
      <h4>Copyright &amp; corrections</h4>
      <p>Source pages carry bibliographic detail, a research summary, extracted claims and short quotations
      for the purpose of comment and review. Copyright in the underlying articles remains with their
      publishers, and every page links to the original — please read journalism at its source.</p>
      <p>Found an error? Corrections are welcome and will be logged. Accuracy matters more here than being
      first, and this archive has already been corrected once against itself.</p>
    </div>
  </div>
</div></footer>
</body>
</html>'''

def foot(depth=0):
    return FOOT_T.format(p='../' * depth, built=BUILT, n=len(records))

def write(relpath, content):
    full = os.path.join(OUT, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(content)

# ---------------------------------------------------------------- markdown prose
def prose(mdfile, drop_h1=True):
    raw = open(os.path.join(DELIV, mdfile), encoding='utf-8').read()
    if drop_h1:
        raw = re.sub(r'^#\s+.*?\n', '', raw, count=1)
    body = md.markdown(raw, extensions=['tables', 'sane_lists', 'attr_list'])
    body = body.replace('<table>', '<div class="scrollx"><table>').replace('</table>', '</table></div>')
    body = re.sub(r'\[CONTESTED\]', '<span class="badge contested">Contested</span>', body)
    body = re.sub(r'\[SINGLE SOURCE\]', '<span class="badge contested">Single source</span>', body)
    body = re.sub(r'\[UNRESOLVED\]', '<span class="badge contested">Unresolved</span>', body)
    return body

# ==================================================================== CHARTS ==
CHART_COUNT = '''
<div class="chart bars">
<svg viewBox="0 0 480 96" role="img" aria-labelledby="c1t c1d">
  <title id="c1t">Manifest against CCTV</title>
  <desc id="c1d">The manifest recorded 133 people aboard. A review of boarding-area CCTV established 179 — 46 unrecorded.</desc>
  <text x="0" y="9" font-size="9.5" font-weight="660" fill="var(--ink)">What the manifest claimed</text>
  <rect class="mark" x="0" y="13" width="280" height="15" rx="4" fill="var(--s1l)"
        data-label="Manifest, 19 July" data-value="133" data-unit="passengers and crew" data-var="--s1l"
        data-note="100 online bookings + 16 by Mobile Money"/>
  <text x="288" y="25" font-size="11.5" font-weight="680" fill="var(--ink)">133</text>
  <text x="320" y="25" font-size="8.5" fill="var(--ink2)">passengers + crew</text>
  <text x="0" y="48" font-size="9.5" font-weight="660" fill="var(--ink)">What the CCTV review showed</text>
  <rect class="mark" x="0" y="52" width="377" height="15" rx="4" fill="var(--s1)"
        data-label="CCTV review, confirmed 25 July" data-value="179" data-unit="aboard, incl. 18 crew" data-var="--s1"
        data-note="Not derived from any paper record"/>
  <text x="385" y="64" font-size="11.5" font-weight="680" fill="var(--ink)">179</text>
  <line x1="280" y1="79" x2="377" y2="79" stroke="var(--s2)" stroke-width="2"/>
  <line x1="280" y1="75" x2="280" y2="83" stroke="var(--s2)" stroke-width="2"/>
  <line x1="377" y1="75" x2="377" y2="83" stroke="var(--s2)" stroke-width="2"/>
  <text x="328" y="94" font-size="9" font-weight="660" fill="var(--ink)" text-anchor="middle">46 unrecorded</text>
</svg>
</div>
<div class="chart bars" style="margin-top:14px;">
<svg viewBox="0 0 480 40" role="img" aria-labelledby="c2t c2d">
  <title id="c2t">The first 67 survivors checked against the manifest</title>
  <desc id="c2d">35 of the first 67 survivors appeared on the manifest; 32 did not.</desc>
  <rect class="mark" x="0" y="4" width="219" height="18" rx="4" fill="var(--s1)"
        data-label="On the manifest" data-value="35" data-unit="of 67 survivors" data-var="--s1"/>
  <rect class="mark" x="221" y="4" width="201" height="18" rx="4" fill="var(--s2)"
        data-label="Never recorded as boarding" data-value="32" data-unit="of 67 survivors" data-var="--s2"/>
  <text x="9" y="17" font-size="11" font-weight="680" fill="#ffffff">35</text>
  <text x="230" y="17" font-size="11" font-weight="680" fill="#ffffff">32</text>
  <text x="0" y="37" font-size="8.5" fill="var(--ink2)">The first 67 survivors, checked against the manifest</text>
</svg>
</div>
<div class="legend">
  <div class="lg"><span class="lgk" style="background:var(--s1)"></span>On the manifest</div>
  <div class="lg"><span class="lgk" style="background:var(--s2)"></span>Never recorded as having boarded</div>
  <div class="lg"><span class="lgk" style="background:var(--s1l)"></span>What the manifest claimed</div>
</div>
<details class="tableview"><summary>Table view</summary>
<div class="scrollx"><table>
<caption>Complement and manifest reconciliation</caption>
<tr><th>Measure</th><th class="n">Value</th><th>Source and basis</th></tr>
<tr><td>Manifest complement</td><td class="n">133</td><td>116 passengers + 17 crew, Min. Edghill / DPI, 19 July</td></tr>
<tr><td>Booked online</td><td class="n">100</td><td>Online Booking System</td></tr>
<tr><td>Booked by Mobile Money</td><td class="n">16</td><td>Mobile Money Guyana</td></tr>
<tr><td>Complement from CCTV</td><td class="n">179</td><td>Incl. 18 crew; PM Phillips 21 July, confirmed by CCTV review 25 July</td></tr>
<tr><td>Unrecorded</td><td class="n">46</td><td>Difference between the two figures</td></tr>
<tr><td>First survivors on the manifest</td><td class="n">35 of 67</td><td>Min. Edghill, 19 July</td></tr>
<tr><td>First survivors not on the manifest</td><td class="n">32 of 67</td><td>Min. Edghill, 19 July</td></tr>
</table></div>
</details>
'''

CHART_CAP = '''
<div class="chart bars">
<svg viewBox="0 0 480 172" role="img" aria-labelledby="c3t c3d">
  <title id="c3t">Four official cargo limits against the load carried</title>
  <desc id="c3d">Official cargo limits given as 284, 126 and 120 tonnes, against an original 1938 rating of 120 tonnes
  and a manifested load of 268 tonnes. Three of the four official limits are below the load she was manifested to carry.</desc>
  <text x="373" y="9" font-size="8.5" font-weight="660" fill="var(--ink)" text-anchor="end">268 t actually manifested</text>
  <line x1="375" y1="12" x2="375" y2="152" stroke="var(--ink2)" stroke-width="2"/>

  <text x="0" y="28" font-size="8.8" fill="var(--ink)">Min. Edghill, 19 July &mdash; &ldquo;licensed&rdquo;</text>
  <rect class="mark" x="0" y="32" width="398" height="14" rx="4" fill="var(--s1)"
        data-label="Min. Edghill, 19 July" data-value="284 t" data-unit="licensed cargo" data-var="--s1"
        data-note="Paired with 397 passengers"/>
  <text x="406" y="43" font-size="10" font-weight="680" fill="var(--ink)">284 t</text>

  <text x="0" y="62" font-size="8.8" fill="var(--ink)">MARAD Director-General, 21&ndash;22 July</text>
  <rect class="mark" x="0" y="66" width="176" height="14" rx="4" fill="var(--s1)"
        data-label="MARAD Director-General, 21–22 July" data-value="126 t" data-unit="licensed cargo" data-var="--s1"
        data-note="Paired with 394 passengers"/>
  <text x="184" y="77" font-size="10" font-weight="680" fill="var(--ink)">126 t</text>

  <text x="0" y="96" font-size="8.8" fill="var(--ink)">MARAD Director-General, 24&ndash;25 July</text>
  <rect class="mark" x="0" y="100" width="168" height="14" rx="4" fill="var(--s1)"
        data-label="MARAD Director-General, 24–25 July" data-value="120 t" data-unit="licensed cargo" data-var="--s1"
        data-note="Same figure as the original 1938 rating"/>
  <text x="176" y="111" font-size="10" font-weight="680" fill="var(--ink)">120 t</text>

  <text x="0" y="130" font-size="8.8" fill="var(--ink)">Original 1938 rating (150 passengers)</text>
  <rect class="mark" x="0" y="134" width="168" height="14" rx="4" fill="var(--s1l)"
        data-label="Original 1938 rating" data-value="120 t" data-unit="cargo, and 150 passengers" data-var="--s1l"
        data-note="The regulator could not say when this was raised"/>
  <text x="176" y="145" font-size="10" font-weight="680" fill="var(--ink)">120 t</text>

  <line x1="0" y1="152" x2="440" y2="152" stroke="var(--axis)" stroke-width="1"/>
  <g font-size="8" fill="var(--muted)">
    <text x="0" y="165">0</text><text x="140" y="165">100</text>
    <text x="280" y="165">200</text><text x="410" y="165">300 tonnes</text>
  </g>
</svg>
</div>
<details class="tableview"><summary>Table view</summary>
<div class="scrollx"><table>
<caption>Stated cargo and passenger limits for the MV Barima</caption>
<tr><th>Stated by</th><th>Date</th><th class="n">Cargo</th><th class="n">Passengers</th></tr>
<tr><td>Min. Juan Edghill</td><td>19 July 2026</td><td class="n">284 t</td><td class="n">397</td></tr>
<tr><td>Capt. Stephen Thomas, MARAD</td><td>21–22 July 2026</td><td class="n">126 t</td><td class="n">394</td></tr>
<tr><td>Capt. Stephen Thomas, MARAD</td><td>24–25 July 2026</td><td class="n">120 t</td><td class="n">394</td></tr>
<tr><td>Original certification</td><td>1938</td><td class="n">120 t</td><td class="n">150</td></tr>
<tr><td><strong>Manifested load</strong></td><td>18 July 2026</td><td class="n"><strong>268 t</strong></td><td class="n">116</td></tr>
<tr><td>Minister's own line-by-line audit</td><td>19 July 2026</td><td class="n">260 t</td><td class="n">—</td></tr>
</table></div>
</details>
'''

TOLL_SERIES = json.dumps({
    "labels": ["19 July", "20 July", "21 July", "22 July", "23 July", "24 July", "25 July", "26 July"],
    "series": [
        {"name": "bodies recovered", "varname": "--s1", "fallback": "#2a78d6",
         "values": [2, 27, 53, 65, 72, 73, 73, 73]},
        {"name": "survivors confirmed", "varname": "--s2", "fallback": "#eb6834",
         "values": [67, 69, 77, 76, 76, 76, 76, 76]},
    ]
})

def toll_chart():
    xs = [60 + i * 117.14 for i in range(8)]
    rec = [2, 27, 53, 65, 72, 73, 73, 73]
    sur = [67, 69, 77, 76, 76, 76, 76, 76]
    y = lambda v: 200 - v * (180 / 190)
    pr = ' '.join(f'{x:.1f},{y(v):.1f}' for x, v in zip(xs, rec))
    ps = ' '.join(f'{x:.1f},{y(v):.1f}' for x, v in zip(xs, sur))
    hits = ''.join(
        f'<rect class="hit" data-i="{i}" data-x="{x:.1f}" x="{max(60, x-58.5):.1f}" y="18" '
        f'width="{min(117.14, x-60+58.5 if i==0 else (880-x+58.5 if i==7 else 117.14)):.1f}" height="184"/>'
        for i, x in enumerate(xs))
    ticks = ''.join(f'<text x="{x:.1f}" y="218">{lbl}</text>'
                    for x, lbl in zip(xs, ['19 Jul', '20', '21', '22', '23', '24', '25', '26']))
    return f'''
<div class="chart" data-series='{TOLL_SERIES}'>
<svg viewBox="0 0 1000 250" role="img" aria-labelledby="c4t c4d">
  <title id="c4t">Bodies recovered and survivors confirmed, 19 to 26 July 2026</title>
  <desc id="c4d">Bodies recovered rose from 2 to 73 and then stopped. Survivors confirmed settled at 76.
  Against 179 aboard, that leaves an arithmetic residual of 103 which no official document reports.</desc>
  <line x1="60" y1="152.6" x2="880" y2="152.6" stroke="var(--grid)" stroke-width="1"/>
  <g font-size="10" fill="var(--muted)" text-anchor="end" font-variant-numeric="tabular-nums">
    <text x="50" y="203">0</text><text x="50" y="156">50</text>
  </g>
  <line x1="60" y1="30.4" x2="880" y2="30.4" stroke="var(--ink2)" stroke-width="2"/>
  <text x="66" y="24" font-size="10.5" font-weight="660" fill="var(--ink)">179 aboard &mdash; reconstructed from CCTV</text>
  <line x1="60" y1="102.4" x2="880" y2="102.4" stroke="var(--ink2)" stroke-width="2"/>
  <text x="874" y="96" font-size="10.5" font-weight="660" fill="var(--ink)" text-anchor="end">103 &mdash; the arithmetic residual (179 aboard &minus; 76 survivors)</text>
  <line class="crosshair" x1="60" y1="18" x2="60" y2="202"/>
  <polyline fill="none" stroke="var(--s1)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" points="{pr}"/>
  <polyline fill="none" stroke="var(--s2)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" points="{ps}"/>
  <circle cx="411.4" cy="102.4" r="6" fill="none" stroke="var(--ink)" stroke-width="2"/>
  <line x1="411.4" y1="96" x2="411.4" y2="76" stroke="var(--muted)" stroke-width="1"/>
  <text x="411.4" y="62" font-size="10" font-weight="660" fill="var(--ink)" text-anchor="middle">Independent tally, 22 July: 103</text>
  <text x="411.4" y="72.5" font-size="9" fill="var(--ink2)" text-anchor="middle">the state reported 53 that day</text>
  <line x1="881" y1="128" x2="897" y2="114" stroke="var(--muted)" stroke-width="1"/>
  <text x="901" y="117" font-size="10.5" font-weight="660" fill="var(--ink)">76 survivors</text>
  <line x1="881" y1="130.8" x2="897" y2="150" stroke="var(--muted)" stroke-width="1"/>
  <text x="901" y="153" font-size="10.5" font-weight="660" fill="var(--ink)">73 recovered</text>
  <line x1="60" y1="200" x2="880" y2="200" stroke="var(--axis)" stroke-width="1"/>
  <g font-size="10" fill="var(--muted)" text-anchor="middle">{ticks}</g>
  {hits}
</svg>
</div>
<div class="legend">
  <div class="lg"><span class="lgk" style="background:var(--s1)"></span>Bodies recovered (official)</div>
  <div class="lg"><span class="lgk" style="background:var(--s2)"></span>Survivors confirmed (official)</div>
  <div class="lg"><span class="lgk" style="background:var(--ink2)"></span>Reference &mdash; total aboard, and the residual never reported</div>
</div>
<details class="tableview"><summary>Table view</summary>
<div class="scrollx"><table>
<caption>Day-end figures, July 2026. The residual column is arithmetic, not an official statement.</caption>
<tr><th>July</th><th class="n">Bodies recovered</th><th class="n">Survivors</th><th class="n">Residual</th></tr>
<tr><td>19</td><td class="n">2</td><td class="n">67</td><td class="n">—</td></tr>
<tr><td>20</td><td class="n">27</td><td class="n">69</td><td class="n">83 “missing”</td></tr>
<tr><td>21</td><td class="n">53</td><td class="n">77</td><td class="n">—</td></tr>
<tr><td>22</td><td class="n">65</td><td class="n">76</td><td class="n">103</td></tr>
<tr><td>23</td><td class="n">72</td><td class="n">76</td><td class="n">103</td></tr>
<tr><td>24</td><td class="n">73</td><td class="n">76</td><td class="n">30 “unaccounted”</td></tr>
<tr><td>25</td><td class="n">73</td><td class="n">76</td><td class="n">103</td></tr>
<tr><td>26</td><td class="n">73</td><td class="n">76</td><td class="n">103</td></tr>
</table></div>
</details>
'''

# ===================================================================== INDEX ==
NIGHT = [
    ('15:15', '', 'Departs the Transport &amp; Harbours Department wharf at Kingston, Georgetown, for Port Kaituma, with 116 passengers and 17 crew on the manifest.'),
    ('~19:00', 'hot', 'Survivor Leon Murray (AP) states one engine failed about four hours out and the crew repaired it at sea rather than turning back.'),
    ('~20:00', 'hot', 'Murray states a passenger reported water on the lower deck and was told: &ldquo;They told us this is normal.&rdquo;'),
    ('23:01', 'hot', 'A Mayday is widely reported as transmitted by radio at this time. On 25 July the Prime Minister said of a Mayday from the captain: &ldquo;We have no such record.&rdquo;'),
    ('01:36', '', 'Capt. Gerry Gouveia takes off from Ogle in a private fixed-wing Roraima Airways Islander, 2h 35m after the reported Mayday, and reports GPS coordinates from a sighted flare. Two military helicopters were reported unserviceable.'),
    ('03:15', '', 'Edghill announces on Facebook Live that eight people have been retrieved alive. Guyana Times reports that fisherman Haresh Singh located the hull.'),
]
FUSE = [
    ('1939', '', 'Built by Ferguson Brothers, Port Glasgow, ordered through the Crown Agents for the Colonies &mdash; one of three sisters for British Guiana Railways, per the Paxman engine register.'),
    ('1970', 'dead', '<em>MV Christena</em> capsizes off St Kitts&ndash;Nevis: a reported 233 dead, more than 320 aboard against a certified 155. One source places her construction at the same Georgetown yard as Guyana&rsquo;s own ferries.'),
    ('2010 · 2015', 'warn', 'Port Kaituma residents call for better vessels. A Kaieteur inspection describes the <em>Barima</em>&rsquo;s deck and winch area as &ldquo;a mass of junk and rust&rdquo;; master mariner Capt. R. E. W. Adams writes that such a vessel would be scrapped elsewhere in the Caribbean.'),
    ('2017 · 2019', 'money', 'G$150.6m spent rehabilitating the hull rather than replacing it. The sister ship is reported withdrawn, leaving the <em>Barima</em> the only vessel on the Port Kaituma run &mdash; though Kaieteur reported on 24 July that the sister ship &ldquo;continues operating.&rdquo;'),
    ('2020 · 2023', 'warn', 'A DPI release records mechanical failures on the vessel. The US$12.7m <em>MV Ma Lisha</em> is commissioned and does not run the route &mdash; for want of wharf works (PM Phillips) or cargo capacity (residents). Twenty children die in the Mahdia dormitory fire.'),
    ('2025', 'warn', 'A DPI release states the Transport &amp; Harbours Department has &ldquo;longstanding issues of negligence, mismanagement, and accountability.&rdquo; Published sixteen months before the sinking.'),
    ('2026', 'money', 'A further G$124.5m tendered for the hull in March, within a G$11.2bn river-transport allocation; no line for retiring the vessel appears in the corpus. Kaieteur reports a newer vessel uncommissioned at the wharf since May. Stabroek News ceases print in March.'),
]
# Left: a condition recorded in the sources. Right: proposals on the public record,
# each attributed to the party that made it. Nothing here is this archive's own proposal.
CHAIN = [
    ('One vessel on the route.',
     'After the sister ship&rsquo;s reported 2019 withdrawal the <em>Barima</em> was the only vessel on the Georgetown&ndash;Port Kaituma run.',
     '<b>Amerindian Peoples Association:</b> a parallel review of Guyana&rsquo;s entire river and sea transport system, with mandatory consultation of Indigenous and riverain communities.'),
    ('The replacement never ran the route.',
     'The <em>Ma Lisha</em>, commissioned 2023, did not serve Port Kaituma &mdash; incomplete wharf works per PM Phillips, insufficient cargo capacity per residents.',
     '<b>APNU:</b> the National Assembly, not the President, should set the inquiry&rsquo;s terms of reference. <b>David Patterson</b> alleges procurement advice was disregarded (uncorroborated).'),
    ('Three stated capacity figures, no published certificate.',
     'Edghill gave 284 t / 397 passengers; MARAD gave 126 t then 120 t / 394 passengers; the 1938 rating was 120 t / 150. MARAD said it could not date the increase.',
     '<b>Joint five opposition parties:</b> a marine casualty investigation under SOLAS and the IMO Casualty Investigation Code, in addition to the inquiry. <b>Kaieteur editorial:</b> an unredacted preliminary report within 90 days.'),
    ('Thirty-two survivors were not on the manifest.',
     '35 of the first 67 rescued appeared on it, per Edghill. AP reports clerks had sold unmanifested seats for cash &ldquo;for decades at state-run ferry terminals.&rdquo;',
     '<b>Government, 25 July:</b> strengthened compliance with existing standard operating procedures and stricter adherence to existing ticketing and passenger-management rules.'),
    ('Four hours between the reported engine failure and the Mayday.',
     'Per survivor accounts an engine was repaired at sea and water ingress was reported at about 20:00. No Pan Pan urgency call is established in the corpus.',
     '<b>Janette Bulkan:</b> published questions asking the Maritime Search and Rescue Coordination Centre to release the rescue timeline and the times at which the Mayday was relayed.'),
    ('The regulator reports to the operator&rsquo;s ministry.',
     'MARAD stated the vessel was not overloaded on 22 July, before any inquiry existed. Edghill described MARAD as regulator and the T&amp;HD as service provider.',
     '<b>GHRA:</b> a parliamentary commission, equal government and opposition membership, judicially qualified chair, statutory duty of candour, state-funded counsel for families. <b>TIGI and Rescue Guyana:</b> an IMO-led investigation. <b>WIN:</b> recusal of Ministers Edghill and Indar, livestreamed hearings.'),
]

def build_index():
    tiles = [
        ('179', '', 'People aboard', 'Reconstructed from boarding-area CCTV. The manifest said 133.'),
        ('73', '', 'Bodies recovered', 'Official count, unchanged from 24 to 26 July.'),
        ('~30', 'alarm', 'People in the arithmetic, in no official document', 'The state publishes recoveries, never the residual.'),
        ('87', '', 'Years the hull had been in service', 'Built 1939, Ferguson Brothers, Port Glasgow, via the Crown Agents.'),
        ('0', 'alarm', 'Survey, load-line or capacity certificates published', f'Across all {len(records)} documents. Seaworthiness was asserted, never documented.'),
    ]
    tilehtml = ''.join(
        f'<div class="tile {cls}"><div class="v">{v}</div><div class="l">{l}</div><div class="n">{n}</div></div>'
        for v, cls, l, n in tiles)
    nighthtml = ''.join(
        f'<div class="step {cls}"><div class="t">{t}</div><div class="d">{d}</div></div>'
        for t, cls, d in NIGHT)
    fusehtml = ''.join(
        f'<div class="fev {cls}"><div class="y">{y}</div><div class="x">{x}</div></div>'
        for y, cls, x in FUSE)
    chainhtml = '<div class="chdr">How the disaster was built</div><div class="chdr">What would have broken the chain</div>'
    for i, (hd, bd, fx) in enumerate(CHAIN, 1):
        last = ' style="border-bottom:none"' if i == len(CHAIN) else ''
        chainhtml += (f'<div class="lnk"{last}><span class="num">{i}</span>'
                      f'<span class="tx"><b>{hd}</b> {bd}</span></div>'
                      f'<div class="fix"{last}><span class="num fixn">{i}</span><span class="tx">{fx}</span></div>')

    return head('MV Barima — the documented record | Guyana ferry disaster, 18 July 2026',
                'What {len(records)} published documents record about the sinking of the Guyanese ferry MV Barima on '
                '18 July 2026: the figures, the chronology, the positions of each party, and every source.',
                'index.html') + f'''
<section style="margin-top:44px;">
  <p class="eyebrow">Guyana &middot; Transport &amp; Harbours Department ferry &middot; Georgetown → Port Kaituma</p>
  <h1>MV Barima: the documented record</h1>
  <p class="lede wrap-read">The <em>MV Barima</em> left the Transport &amp; Harbours Department wharf at Kingston,
  Georgetown at about 15:15 on Saturday 18 July 2026, bound for Port Kaituma, and capsized off Iron Punt at the
  mouth of the Pomeroon River in three to nine metres of water. Her manifest recorded 116 passengers and 17 crew.
  A review of boarding-area CCTV later put 179 people aboard.</p>
  <p class="small muted wrap-read">This site records what {len(records)} published documents say, who said it, and when.
  Where sources disagree, both figures are given. It does not advance an explanation of the cause. The Commission
  of Inquiry&rsquo;s five members were named on 26 July 2026 and its establishing instrument has not been gazetted;
  on 28 July three employees of the operator were charged with murder and remanded, and they are accused persons
  who have not been tried; and the figures are still being revised. Every claim links back to its source so it can
  be checked. Changes to this site are logged on the <a href="changelog.html">revisions page</a>.</p>
</section>

<section>
  <div class="grid g5">{tilehtml}</div>
</section>

<section>
  <h2>Three findings from the record</h2>
  <div class="grid g3">
    <div class="card">
      <h3 style="margin-top:0">35 of the first 67 survivors were on the manifest</h3>
      <p class="small muted">Minister Edghill stated on 19 July that 35 of the 67 people then rescued appeared on
      the vessel&rsquo;s manifest, and that authorities could no longer determine how many had been aboard. DPI
      releases of 19 July state that families were being updated using the manifest. The figure of 179 is
      attributed to a review of boarding-area CCTV rather than to a paper record.</p>
    </div>
    <div class="card">
      <h3 style="margin-top:0">Three stated capacity figures, no published certificate</h3>
      <p class="small muted">Edghill gave 284 tonnes and 397 passengers on 19 July. MARAD&rsquo;s Director-General
      gave 126 tonnes on 21&ndash;22 July and 120 tonnes on 24&ndash;25 July, both with 394 passengers, and said
      of the increase from the 1938 rating: &ldquo;I don&rsquo;t have that information.&rdquo; No certificate of
      survey, load line or passenger capacity appears in the corpus.</p>
    </div>
    <div class="card">
      <h3 style="margin-top:0">Who published this record</h3>
      <p class="small muted">Stabroek News, publishing for about forty years, ceased print in March 2026 in
      voluntary liquidation, four months before the sinking. It carried the 2015 letter by master mariner Capt.
      R. E. W. Adams that named this vessel. The largest single share of this archive is the state-owned
      <em>Guyana Chronicle</em> at {N_CHRON} documents; with the Department of Public Information&rsquo;s
      {N_DPI} releases, {N_STATE} of {len(records)} &mdash; about three in ten &mdash; come from the state or a
      state-owned outlet. Kaieteur News, at {N_KAI}, is the largest independent share, and three publishers
      account for {N_TOP3}. The full provenance breakdown is on the
      <a href="about.html">method and gaps page</a>.</p>
    </div>
  </div>
</section>

<section>
  <h2>1. The manifest and the complement</h2>
  <p class="wrap-read muted">Of the 116 passengers on the manifest, Edghill stated 100 booked through the Online
  Booking System and 16 through Mobile Money Guyana. The Associated Press reports that clerks had sold
  unmanifested seats for cash &ldquo;for decades at state-run ferry terminals.&rdquo; Hover or focus any bar for
  its figures; a table view sits beneath each chart.</p>
  <div class="card">{CHART_COUNT}</div>
</section>

<section>
  <h2>2. Stated capacity limits</h2>
  <p class="wrap-read muted">Officials gave different limits on different days. Three of the four figures on
  record sit below the 268 tonnes the vessel was manifested to carry; the fourth, Edghill&rsquo;s 284 tonnes,
  sits above it. On 22 July MARAD stated the vessel was &ldquo;not overloaded,&rdquo; citing the load line. No
  published certificate appears in the corpus against which any of these figures can be checked.</p>
  <div class="card">{CHART_CAP}</div>
</section>

<section>
  <h2>3. Recovery and survivor figures</h2>
  <p class="wrap-read muted">Bodies recovered reached 73 on 24 July and were unchanged through 26 July.
  Survivors were revised from 77 to 76 after de-duplication, per News Room and Kaieteur. Kaieteur published its
  own tally of 103 on 22 July, compiled from Coast Guard, opposition, private-vessel and fishermen&rsquo;s
  accounts, on a day the government reported 53.</p>
  <div class="card">{toll_chart()}</div>
  <div class="note" style="margin-top:16px;">
    <h4>What the figures imply, and what is published</h4>
    <p>Government releases report bodies recovered. No official death toll appears in the corpus. Against a
    stated complement of 179 and 76 survivors, subtraction leaves approximately 103 people; 73 bodies had been
    recovered. On 24 July the Prime Minister gave &ldquo;30 unaccounted for,&rdquo; against 83 &ldquo;missing&rdquo;
    four days earlier. Neither figure is reconciled in any source.</p>
  </div>
</section>

<section>
  <h2>4. The voyage, hour by hour</h2>
  <div class="card">
    <div class="steps">{nighthtml}</div>
    <p class="tiny" style="margin-top:22px;">Survivor accounts describe a packed lower deck (Leon Murray, AP),
    cargo stacked at the stern (Elena Moonsammy) and a list that did not right itself (Wayne Kitson). MARAD&rsquo;s
    Director-General stated that a vessel with positive stability returns upright even when heeled twenty degrees,
    and attributed the failure to right to operational error in treacherous conditions. The two accounts are not
    reconciled in any source. Reported sinking duration ranges from about four minutes (Murray) to
    &ldquo;less than a minute&rdquo; (Guyana Times).</p>
  </div>
</section>

<section>
  <h2>5. Vessel and institutional record, 1939&ndash;2026</h2>
  <div class="card">
    <div class="legend" style="margin-top:0">
      <div class="lg"><span class="lgk dot" style="background:var(--s2)"></span>Documented warning ignored</div>
      <div class="lg"><span class="lgk dot" style="background:var(--s1)"></span>Money spent, or not spent</div>
      <div class="lg"><span class="lgk dot" style="background:var(--ink)"></span>Lives lost</div>
      <div class="lg"><span class="lgk dot" style="background:var(--surface);border:2px solid var(--muted)"></span>Origin</div>
    </div>
    <div class="fuse"><div class="spine"></div><div class="fuserow">{fusehtml}</div></div>
    <p class="tiny" style="margin-top:22px;"><a href="timeline.html">Read the full chronology, entry by entry,
    with every conflict marked &rarr;</a></p>
  </div>
</section>

<section>
  <h2>6. Conditions recorded, and proposals on the record</h2>
  <p class="wrap-read muted">The left column states a condition as the sources record it, attributed. The right
  column lists proposals that identified parties have publicly made in response. Neither column contains any
  proposal or conclusion of this archive&rsquo;s own. Fuller statements of each party&rsquo;s position, with
  sourcing, are on the <a href="positions.html">positions page</a>.</p>
  <div class="card"><div class="chain">{chainhtml}</div></div>
</section>

<section>
  <h2>7. Where the parties stand on the inquiry</h2>
  <p class="wrap-read muted">As of 28 July 2026 the dispute on record was less about cause than about who should
  investigate. The three summaries below are the parties&rsquo; own stated positions.</p>
  <div class="grid g3">
    <div class="card tr">
      <h3>The Government</h3>
      <p>President Ali named the five-member Commission of Inquiry on 26 July: Justice Godfrey Phillip Smith of
      Belize as chair, with Capt. Hamada Fouda (Jamaica), Nyree Dawn Alfonso (Trinidad and Tobago), Dr Andrzej
      Jasionowski (Poland) and Rear Admiral (Ret&rsquo;d) Hayden Pritchard (Trinidad and Tobago). Terms of
      reference were announced covering loading, boarding, seaworthiness, maintenance history, crew competence,
      lifesaving arrangements, weather and the search-and-rescue response. The establishing instruments were
      described as still being finalised, and no secretary or reporting deadline was cited. Kiskadee Watch
      reports the commission was appointed under Section 2(1) of the Commissions of Inquiry Act; the two
      outlets corroborate the membership.</p>
    </div>
    <div class="card tr">
      <h3>The parliamentary opposition</h3>
      <p>APNU states the National Assembly should set the terms of reference and include IMO representatives.
      WIN seeks recusal of Ministers Edghill and Indar, livestreamed hearings and publication of the full report.
      The AFC proposes the Commission of Inquiry Act, Cap. 19:03. Jointly, five parties state that a Commission of
      Inquiry is not a substitute for a marine casualty investigation under SOLAS and the IMO Casualty
      Investigation Code, and that both should run. These positions were stated before the members were named;
      no response to the announced membership appears in the corpus.</p>
    </div>
    <div class="card tr">
      <h3>Civil society</h3>
      <p>The GHRA rejects executive appointment and proposes a parliamentary commission with equal government and
      opposition membership, a judicially qualified chair, a statutory duty of candour and state-funded counsel for
      bereaved families. TIGI and Rescue Guyana call for an IMO-led investigation. The Amerindian Peoples
      Association calls for Minister Edghill&rsquo;s removal and a review of the whole river and sea transport
      system with mandatory consultation of Indigenous and riverain communities. The Shipping Association of
      Guyana welcomed the inquiry. On 25 July the Prime Minister said that if contacting the IMO would help, the
      government would do it.</p>
    </div>
  </div>
  <p class="small muted" style="margin-top:16px;"><a href="positions.html">Every position, in full and attributed
  &rarr;</a></p>
</section>

<section>
  <h2>Check it yourself</h2>
  <div class="grid g3">
    <a class="card" href="sources.html" style="color:inherit">
      <h3 style="margin-top:0">All {len(records)} documents &rarr;</h3>
      <p class="small muted">Search and filter by outlet, type and period. Every source has a page with its
      summary, key claims, quotations and a link to the original.</p>
    </a>
    <a class="card" href="facts.html" style="color:inherit">
      <h3 style="margin-top:0">The figures, source by source &rarr;</h3>
      <p class="small muted">Every figure that changed, who stated it, when, and on what stated basis. Read this
      before citing a number from anywhere &mdash; including from here.</p>
    </a>
    <a class="card" href="about.html" style="color:inherit">
      <h3 style="margin-top:0">Method and gaps &rarr;</h3>
      <p class="small muted">How the corpus was assembled, what could not be retrieved, what was searched for and
      not found, and the eighteen corrections made after an adversarial check.</p>
    </a>
  </div>
</section>
''' + foot()

# ================================================================== SOURCES ===
MONTHS = {'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June',
          '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}
def prettydate(d):
    if d == '0000-00-00':
        return 'Undated'
    y, m, dd = d.split('-')
    return f'{int(dd)} {MONTHS[m]} {y}'

def build_sources():
    outlets = sorted({r['outlet'] for r in records})
    kinds = sorted({r['kind'] for r in records})
    osel = ''.join(f'<option value="{esc(o)}">{E(o)}</option>' for o in outlets)
    ksel = ''.join(f'<option value="{esc(k)}">{E(k)}</option>' for k in kinds)

    cards, cur = [], None
    for r in records:
        if r['published'] != cur:
            cur = r['published']
            cards.append(f'<div class="datebar"><span class="dl">{E(prettydate(cur))}</span><span class="dr"></span></div>')
        hay = ' '.join([r['title'], r['outlet'], r['author'], r['summary'], r['genre'], r['kind']]
                       + r['claims'][:6] + r['facts'][:6])
        badges = f'<span class="badge">{E(r["kind"])}</span>'
        if r['genre']:
            badges += f'<span class="badge">{E(r["genre"].replace("-", " "))}</span>'
        if r['flagged']:
            badges += '<span class="badge contested">Condensed capture</span>'
        summ = r['summary'] or (r['claims'][0] if r['claims'] else '')
        cards.append(f'''<a class="src" href="sources/{r['slug']}.html"
   data-search="{esc(hay)}" data-outlet="{esc(r['outlet'])}" data-kind="{esc(r['kind'])}" data-date="{r['published']}">
  <h3>{E(r['title'])}</h3>
  <div class="m"><span class="o">{E(r['outlet'])}</span><span>{E(prettydate(r['published']))}</span>{badges}</div>
  <div class="s">{E(summ[:280])}{'…' if len(summ) > 280 else ''}</div>
</a>''')

    return head(f'All {len(records)} documents — MV Barima research archive',
                'Search and filter every source behind this archive: Guyanese press, official documents, '
                'international coverage and historical record.',
                'sources.html') + f'''
<section style="margin-top:44px;">
  <p class="eyebrow">The evidence base</p>
  <h1>All {len(records)} documents</h1>
  <p class="lede wrap-read">Every source behind this archive, with a research summary, the claims it establishes,
  short attributed quotations and a link to the original. Search the full text of the summaries and claims, or
  filter by outlet, type and period.</p>
  <div class="note" style="margin-bottom:22px;">
    <h4>Why the full articles are not reproduced here</h4>
    <p>Copyright in these articles belongs to the journalists and outlets who did the work &mdash; several of them
    working a national disaster with very thin resources. Each page here carries bibliographic detail, a summary,
    extracted claims and short quotations for comment and review, and sends you to the source to read it.
    <strong>Please read journalism where it is published.</strong></p>
  </div>
</section>

<section style="margin-top:0">
  <div class="filters">
    <div class="fgroup">
      <label for="f-q">Search summaries and claims</label>
      <input type="search" id="f-q" placeholder="manifest, seaworthy, Mahdia, capacity…" autocomplete="off">
    </div>
    <div class="fgroup">
      <label for="f-period">Period</label>
      <select id="f-period">
        <option value="">All dates</option>
        <option value="pre">Before the sinking (1936–2026)</option>
        <option value="disaster">The sinking and rescue (18–21 July)</option>
        <option value="reckoning">The reckoning (22–26 July)</option>
      </select>
    </div>
    <div class="fgroup">
      <label for="f-kind">Type</label>
      <select id="f-kind"><option value="">All types</option>{ksel}</select>
    </div>
    <div class="fgroup">
      <label for="f-outlet">Outlet</label>
      <select id="f-outlet"><option value="">All outlets</option>{osel}</select>
    </div>
    <div class="fgroup">
      <label for="f-sort">Sort</label>
      <select id="f-sort">
        <option value="newest">Newest first</option>
        <option value="oldest">Oldest first</option>
        <option value="outlet">By outlet</option>
        <option value="title">By title</option>
      </select>
    </div>
    <button class="fclear" id="f-clear" type="button">Reset</button>
    <div class="fcount" id="f-count" role="status">{len(records)} documents</div>
  </div>
  <div class="srclist" id="srclist">{''.join(cards)}</div>
  <p class="empty" id="srcempty" hidden>No documents match those filters. <button class="fclear" onclick="document.getElementById('f-clear').click()">Reset the filters</button></p>
</section>
''' + foot()

def build_source_page(r):
    def block(title, items, cls=''):
        if not items:
            return ''
        lis = ''.join(f'<li>{E(x)}</li>' for x in items)
        return f'<h3>{title}</h3><ul class="{cls}">{lis}</ul>'

    quotes = ''
    if r['quotes']:
        lis = ''
        for q in r['quotes']:
            parts = re.split(r'\s+[—–-]\s+', q, maxsplit=1)
            body = parts[0].strip().strip('"“”')
            att = parts[1].strip() if len(parts) > 1 else ''
            lis += f'<li>&ldquo;{E(body)}&rdquo;{f"<span class=att>&mdash; {E(att)}</span>" if att else ""}</li>'
        quotes = f'<h3>Quotations</h3><ul class="qlist">{lis}</ul>'

    warn = ''
    if r['flagged']:
        warn = f'''<div class="note warn"><h4>Retrieval note &mdash; do not quote as verbatim</h4>
        <p>This source was returned by the retrieval tool in condensed form. Direct quotations recorded below are
        reliable; any connective wording is the tool&rsquo;s compression, not the outlet&rsquo;s. {E(r['fidelity'])}</p></div>'''

    meta = [('Outlet', r['outlet']), ('Author', r['author'] or '—'),
            ('Published', prettydate(r['published']) + (f' · {r["published_time"]}' if r['published_time'] else '')),
            ('Type', r['kind']), ('Genre', (r['genre'] or '—').replace('-', ' ')),
            ('Archive reference', r['file'])]
    metarows = ''.join(f'<tr><th>{E(k)}</th><td>{E(v)}</td></tr>' for k, v in meta)

    orig = (f'<a class="origin" href="{esc(r["url"])}" rel="nofollow noopener" target="_blank">'
            f'Read the original at {E(r["outlet"])} &nearr;</a>') if r['url'] else \
           '<p class="tiny">No public URL recorded for this source.</p>'

    extra = ''
    if r['position']:
        extra += f'<h3>Official statement recorded in this source</h3><blockquote>{E(r["position"])}</blockquote>'
    if r['argument']:
        extra += f'<h3>The author&rsquo;s argument, as stated</h3><p>{E(r["argument"])}</p>'
    if r['figures']:
        extra += f'<h3>Figures cited in this source</h3><p>{E(r["figures"])}</p>'

    desc = (r['summary'] or r['title'])[:180]
    return head(f'{r["title"]} — {r["outlet"]} | MV Barima archive', desc, 'sources.html', depth=1) + f'''
<p class="crumb"><a href="../sources.html">&larr; All {len(records)} documents</a></p>
<article>
  <div class="badgerow" style="margin-bottom:12px;">
    <span class="badge">{E(r['kind'])}</span>
    {f'<span class="badge">{E((r["genre"] or "").replace("-", " "))}</span>' if r['genre'] else ''}
    <span class="badge">{E(prettydate(r['published']))}</span>
  </div>
  <h1 style="font-size:clamp(25px,3.4vw,38px)">{E(r['title'])}</h1>
  <p class="lede muted" style="margin-bottom:18px;">{E(r['outlet'])}{f' &middot; {E(r["author"])}' if r['author'] else ''}</p>
  {orig}
  {warn}
  <div class="wrap-read">
  {f'<h3>What this source establishes</h3><p>{E(r["summary"])}</p>' if r['summary'] else ''}
  {extra}
  {block('Key claims', r['claims'], 'claims')}
  {quotes}
  {block('Prior warnings recorded', r['warnings'])}
  {block('Vessel facts recorded', r['vessel'])}
  {block('Actors named', r['actors'])}
  <div class="scrollx"><table class="metatable"><caption>Bibliographic detail</caption>{metarows}</table></div>
  <p class="tiny">This page is a research summary prepared for comment and review. It is not the article.
  Copyright in the original remains with {E(r['outlet'])}; the full text is held only in the private research
  corpus from which this archive was compiled. Follow the link above to read it at the source.</p>
  </div>
</article>
''' + foot(1)

# ==================================================================== PAGES ===
# ---------------------------------------------------------- questions charts --
# Three charts for the plain-language questions page. House rules throughout:
# thin marks, 4px rounded ends, a 2px surface gap between adjacent fills, every
# value direct-labelled (which is also what discharges the light-mode contrast
# warning on the green step), a legend wherever more than one series appears,
# and a table view so nothing is carried by colour alone. The hover layer is the
# shared one in site.js -- any element with data-value picks it up. The palette
# is the site's own categorical ramp, checked for CVD separation, chroma and
# lightness against both the light and dark surfaces before use.

CHART_ACTIONS = '''
<div class="chart bars">
<svg viewBox="0 0 480 146" role="img" aria-labelledby="qa1t qa1d">
  <title id="qa1t">People charged over the MV Barima disaster, by employing organisation</title>
  <desc id="qa1d">Three people have been charged, all of them employees of the operator. All three
  are accused persons who have not been tried. No charge against anyone at the regulator, on the
  departmental board, or in the ministry appears in this corpus. Bar length shows the number of
  people charged; one bar segment is one person, and nought is drawn as a stub at the origin.</desc>

  <text x="0" y="10" font-size="9.5" font-weight="680" fill="var(--ink)">Transport &amp; Harbours Department &mdash; the operator</text>
  <rect class="mark" x="0" y="16" width="52" height="18" rx="4" fill="var(--s2)"
        data-label="Captain" data-value="1" data-unit="charged with murder, 28 July" data-var="--s2"
        data-note="Accused; not tried"/>
  <rect class="mark" x="54" y="16" width="52" height="18" rx="4" fill="var(--s2)"
        data-label="Chief mate" data-value="1" data-unit="charged with murder, 28 July" data-var="--s2"
        data-note="Accused; not tried"/>
  <rect class="mark" x="108" y="16" width="52" height="18" rx="4" fill="var(--s2)"
        data-label="Goods superintendent" data-value="1" data-unit="charged with murder, 28 July" data-var="--s2"
        data-note="Accused; not tried"/>
  <text x="170" y="30" font-size="11.5" font-weight="700" fill="var(--ink)">3 charged</text>
  <text x="240" y="30" font-size="8.5" fill="var(--ink2)">captain, chief mate, goods superintendent</text>

  <text x="0" y="59" font-size="9.5" font-weight="680" fill="var(--ink)">MARAD &mdash; the regulator</text>
  <line x1="0" y1="70" x2="6" y2="70" stroke="var(--border)" stroke-width="3"/>
  <text x="14" y="74" font-size="11" font-weight="640" fill="var(--muted)">none</text>

  <text x="0" y="99" font-size="9.5" font-weight="680" fill="var(--ink)">Departmental board and Ministry of Public Works</text>
  <line x1="0" y1="110" x2="6" y2="110" stroke="var(--border)" stroke-width="3"/>
  <text x="14" y="114" font-size="11" font-weight="640" fill="var(--muted)">none</text>

  <text x="0" y="130" font-size="8.5" font-weight="640" fill="var(--ink2)">All three are accused persons who have not been tried.</text>
  <text x="0" y="142" font-size="8.5" fill="var(--muted)">One segment is one person. Detentions and suspensions, which are not charges, are in the table below.</text>
</svg>
</div>
<details class="tableview"><summary>Table view &mdash; all formal action recorded, not only charges</summary>
<div class="scrollx"><table>
<caption>Formal action recorded in this corpus, by employing organisation. All three charged are accused persons who have not been tried.</caption>
<tr><th>Level</th><th class="n">Charged</th><th>Held or detained</th><th>Suspended or on leave</th></tr>
<tr><td>Transport &amp; Harbours Department (operator)</td><td class="n">3</td><td>crew from 19 July; a superintendent 22 July</td><td>loading and dispatch team, 20 July</td></tr>
<tr><td>MARAD (regulator)</td><td class="n">0</td><td>none</td><td>none</td></tr>
<tr><td>Departmental board</td><td class="n">0</td><td>none</td><td>none</td></tr>
<tr><td>Ministry of Public Works</td><td class="n">0</td><td>none</td><td>none</td></tr>
</table></div>
</details>
'''

# Scale: 1 tonne = 1.3px, so the largest bar (284t) is 369px and stays in frame.
CHART_LOAD = '''
<div class="chart bars">
<svg viewBox="0 0 480 168" role="img" aria-labelledby="qa2t qa2d">
  <title id="qa2t">The manifested load against each stated limit</title>
  <desc id="qa2d">The manifest recorded 268 tonnes. Minister Edghill stated a limit of 284 tonnes,
  which the load is inside. MARAD stated 126 tonnes and later 120 tonnes, either of which the load
  exceeds by more than double. The vessel's original rating, dated by MARAD to 1938, was also 120 tonnes.</desc>

  <text x="0" y="10" font-size="9.5" font-weight="680" fill="var(--ink)">Cargo on the manifest</text>
  <rect class="mark" x="0" y="15" width="348" height="17" rx="4" fill="var(--ink2)"
        data-label="Manifested load, 18 July" data-value="268" data-unit="tonnes" data-var="--ink2"
        data-note="Minister Edghill's own line-by-line audit gave an early 260"/>
  <text x="10" y="28" font-size="11" font-weight="680" fill="var(--page)">268 tonnes</text>

  <line x1="348" y1="38" x2="348" y2="158" stroke="var(--ink2)" stroke-width="2" stroke-dasharray="3 3"/>

  <text x="0" y="52" font-size="9.5" font-weight="680" fill="var(--ink)">Limit stated by Minister Edghill, 19 July</text>
  <rect class="mark" x="0" y="57" width="369" height="15" rx="4" fill="var(--s3)"
        data-label="Min. Edghill, 19 July" data-value="284" data-unit="tonnes licensed" data-var="--s3"
        data-note="The manifested load is inside this limit"/>
  <text x="377" y="69" font-size="10.5" font-weight="680" fill="var(--ink)">284</text>
  <text x="404" y="69" font-size="8.5" fill="var(--ink2)">inside</text>

  <text x="0" y="92" font-size="9.5" font-weight="680" fill="var(--ink)">Limit stated by MARAD, 21&ndash;22 July</text>
  <rect class="mark" x="0" y="97" width="164" height="15" rx="4" fill="var(--s2)"
        data-label="MARAD Director-General, 21-22 July" data-value="126" data-unit="tonnes" data-var="--s2"
        data-note="The manifested load exceeds this by 142 tonnes"/>
  <text x="172" y="109" font-size="10.5" font-weight="680" fill="var(--ink)">126</text>
  <text x="199" y="109" font-size="8.5" fill="var(--ink2)">load is 2.1&times; this</text>

  <text x="0" y="132" font-size="9.5" font-weight="680" fill="var(--ink)">Limit stated by MARAD, 24&ndash;25 July, and the 1938 rating</text>
  <rect class="mark" x="0" y="137" width="156" height="15" rx="4" fill="var(--s2)"
        data-label="MARAD Director-General, 24-25 July" data-value="120" data-unit="tonnes" data-var="--s2"
        data-note="Also the vessel's original 1938 rating"/>
  <text x="164" y="149" font-size="10.5" font-weight="680" fill="var(--ink)">120</text>
  <text x="191" y="149" font-size="8.5" fill="var(--ink2)">load is 2.2&times; this</text>

  <text x="0" y="166" font-size="8.5" fill="var(--muted)">Dashed line marks the manifested load. No certificate for any of these limits has been published.</text>
</svg>
</div>
<div class="legend">
  <div class="lg"><span class="lgk" style="background:var(--ink2)"></span>Manifested load</div>
  <div class="lg"><span class="lgk" style="background:var(--s3)"></span>Stated limit the load is inside</div>
  <div class="lg"><span class="lgk" style="background:var(--s2)"></span>Stated limit the load exceeds</div>
</div>
<details class="tableview"><summary>Table view</summary>
<div class="scrollx"><table>
<caption>Cargo limits stated for the MV Barima, against the manifested load</caption>
<tr><th>Stated by</th><th>When</th><th class="n">Cargo limit</th><th>268 tonnes against it</th></tr>
<tr><td>Minister Juan Edghill</td><td>19 July</td><td class="n">284 tonnes</td><td>within the limit</td></tr>
<tr><td>MARAD Director-General Thomas</td><td>21&ndash;22 July</td><td class="n">126 tonnes</td><td>2.1&times; the limit</td></tr>
<tr><td>MARAD Director-General Thomas</td><td>24&ndash;25 July</td><td class="n">120 tonnes</td><td>2.2&times; the limit</td></tr>
<tr><td>Original certification, as described by MARAD</td><td>1938</td><td class="n">120 tonnes</td><td>2.2&times; the limit</td></tr>
</table></div>
</details>
'''

# Scale: 1 person = 2.35px, so the full complement of 179 spans 421px.
CHART_TOLL = '''
<div class="chart bars">
<svg viewBox="0 0 480 142" role="img" aria-labelledby="qa3t qa3d">
  <title id="qa3t">179 aboard: rescued, recovered and unaccounted for</title>
  <desc id="qa3d">Of 179 people aboard, 76 were rescued, 73 bodies have been recovered and about 30
  remain unaccounted for. The resulting figure of about 103 recovered and unaccounted has never
  been published together as a death toll. The complement of 179 is itself a CCTV-derived
  estimate, so the residual is approximate.</desc>

  <text x="0" y="10" font-size="9.5" font-weight="680" fill="var(--ink)">179 aboard, established by CCTV review</text>

  <rect class="mark" x="0" y="18" width="177" height="22" rx="4" fill="var(--s1)"
        data-label="Rescued" data-value="76" data-unit="people" data-var="--s1"
        data-note="Reported as 69, then 77, before settling at 76"/>
  <rect class="mark" x="179" y="18" width="170" height="22" rx="4" fill="var(--s2)"
        data-label="Bodies recovered" data-value="73" data-unit="people" data-var="--s2"
        data-note="Unchanged since 24 July"/>
  <rect class="mark" x="351" y="18" width="70" height="22" rx="4" fill="var(--s3)"
        data-label="Unaccounted for" data-value="about 30" data-unit="people" data-var="--s3"
        data-note="Never described by the state as dead"/>
  <text x="0" y="56" font-size="12" font-weight="700" fill="var(--ink)">76</text>
  <text x="24" y="56" font-size="9" fill="var(--ink2)">rescued</text>
  <text x="179" y="56" font-size="12" font-weight="700" fill="var(--ink)">73</text>
  <text x="203" y="56" font-size="9" fill="var(--ink2)">bodies recovered</text>
  <text x="351" y="56" font-size="12" font-weight="700" fill="var(--ink)">~30</text>
  <text x="381" y="56" font-size="9" fill="var(--ink2)">unaccounted</text>

  <line x1="179" y1="72" x2="421" y2="72" stroke="var(--ink)" stroke-width="2"/>
  <line x1="179" y1="68" x2="179" y2="76" stroke="var(--ink)" stroke-width="2"/>
  <line x1="421" y1="68" x2="421" y2="76" stroke="var(--ink)" stroke-width="2"/>
  <text x="300" y="90" font-size="11" font-weight="700" fill="var(--ink)" text-anchor="middle">about 103 people</text>
  <text x="300" y="103" font-size="9" fill="var(--ink2)" text-anchor="middle">never published together as a death toll</text>

  <text x="0" y="132" font-size="8.5" font-weight="640" fill="var(--muted)">Government releases report bodies recovered; the residual appears in no official total here.</text>
</svg>
</div>
<div class="legend">
  <div class="lg"><span class="lgk" style="background:var(--s1)"></span>Rescued (76)</div>
  <div class="lg"><span class="lgk" style="background:var(--s2)"></span>Bodies recovered (73)</div>
  <div class="lg"><span class="lgk" style="background:var(--s3)"></span>Unaccounted for (about 30)</div>
</div>
<details class="tableview"><summary>Table view</summary>
<div class="scrollx"><table>
<caption>Complement of the MV Barima, as officially stated</caption>
<tr><th>Measure</th><th class="n">People</th><th>Basis</th></tr>
<tr><td>Aboard</td><td class="n">179</td><td>Boarding-area CCTV review; the manifest recorded 133</td></tr>
<tr><td>Rescued</td><td class="n">76</td><td>Settled figure from 21 July</td></tr>
<tr><td>Bodies recovered</td><td class="n">73</td><td>Unchanged since 24 July</td></tr>
<tr><td>Unaccounted for</td><td class="n">about 30</td><td>The Prime Minister's phrasing; never described as dead</td></tr>
<tr><td>Recovered plus unaccounted</td><td class="n">about 103</td><td>Never published as a figure by any government source</td></tr>
</table></div>
</details>
'''

QUESTION_CHARTS = {
    'CHART_ACTIONS': CHART_ACTIONS,
    'CHART_LOAD':    CHART_LOAD,
    'CHART_TOLL':    CHART_TOLL,
}


def inject_charts(body):
    """Swap each {{CHART_X}} token for its figure. Markdown wraps a lone token
    in a paragraph, so strip that wrapper rather than nesting a figure inside a
    <p>. Fails loudly: an unreplaced token would still be visible on the page,
    and the build asserts none survive."""
    for key, svg in QUESTION_CHARTS.items():
        body = body.replace('<p>{{%s}}</p>' % key, svg).replace('{{%s}}' % key, svg)
    left = re.findall(r'\{\{[A-Z_]+\}\}', body)
    if left:
        raise SystemExit('unreplaced chart tokens: %s' % left)
    return body


def collapsible_qa(body):
    """Wrap each numbered `<h2>N. …</h2>` section of a prose page in a <details>,
    so the page reads as a list of questions and opens one answer at a time.

    Native <details>/<summary> only — it works with JavaScript off, is keyboard
    and screen-reader accessible for free, and browser find-in-page opens closed
    sections in current Chrome, Edge and Safari. The small script that follows
    only adds expand-all and deep-link behaviour; nothing depends on it.
    """
    parts = re.split(r'(<h2>)', body)
    if len(parts) < 3:
        return body
    out = [parts[0]]                      # anything before the first h2
    n = 0
    for i in range(1, len(parts), 2):
        chunk = parts[i] + parts[i + 1]   # '<h2>' + rest of that section
        m = re.match(r'<h2>(\d+)\.\s*(.*?)</h2>(.*)$', chunk, re.S)
        if not m:
            out.append(chunk)             # not a numbered question — leave alone
            continue
        num, qtext, answer = m.group(1), m.group(2), m.group(3)
        n += 1
        answer = answer.replace('<hr />', '').replace('<hr>', '')
        out.append(
            '<details class="qa" id="q{num}">'
            '<summary><span class="qnum">{num}</span>'
            '<span class="qtext">{q}</span></summary>'
            '<div class="qbody">{a}</div></details>'.format(num=num, q=qtext, a=answer))
    if not n:
        return body
    controls = (
        '<div class="qacontrols" data-count="{n}">'
        '<button type="button" class="qabtn" data-qa="open">Expand all</button>'
        '<button type="button" class="qabtn" data-qa="close">Collapse all</button>'
        '<span class="tiny muted qahint">{n} questions &middot; click any question to read the answer</span>'
        '</div>').format(n=n)
    # controls go directly above the first question
    joined = ''.join(out)
    return joined.replace('<details class="qa"', controls + '<details class="qa"', 1)


def build_prose_page(fname, title, h1, lede, cur, extra_note='', transform=None):
    body = prose(fname)
    if transform:
        body = transform(body)
    return head(title, lede[:180], cur) + f'''
<section style="margin-top:44px;">
  <h1>{h1}</h1>
  <p class="lede wrap-read">{lede}</p>
  {extra_note}
</section>
<section class="prose wrap-read" style="margin-top:32px;">
{body}
</section>
''' + foot()

# ---------------------------------------------------------------------- build
os.makedirs(OUT, exist_ok=True)
write('index.html', build_index())
write('sources.html', build_sources())
for r in records:
    write(f'sources/{r["slug"]}.html', build_source_page(r))

write('timeline.html', build_prose_page(
    'timeline.md',
    'Chronology, 1936–2026 — MV Barima documented record',
    'Chronology',
    'From the Clyde shipyard that built her in 1939 to the eight days after she sank. Every entry is attributed '
    'to the source that reports it; where sources conflict, both versions are given and marked.',
    'timeline.html'))

write('facts.html', build_prose_page(
    'facts.md',
    'The figures, source by source — MV Barima documented record',
    'The figures, source by source',
    'The complement, the recovery figures and the vessel’s stated capacity all changed over the eight days. This '
    'page records each figure, who stated it, when, on what stated basis, and what in the record differs from it.',
    'facts.html',
    '<div class="note warn"><h4>Read this before citing any number</h4><p>Including numbers from this site. Early '
    'disaster figures are revised, and these were revised repeatedly during the period covered. Several figures '
    'here have no published document behind them.</p></div>'))

write('positions.html', build_prose_page(
    'positions.md',
    'Positions and proposals — MV Barima documented record',
    'Positions and proposals',
    'What each identified party has publicly said and proposed — the government, the parliamentary opposition, '
    'civil society organisations and named commentators — attributed and dated.',
    'positions.html',
    '<div class="note"><h4>Attributed statements, not conclusions</h4><p>Everything on this page is a record of '
    'what a named party said. This archive takes no position on who is correct, endorses no proposal, and makes '
    'none of its own. Where two sources report a party’s position differently, both are given.</p></div>'))

write('about.html', build_prose_page(
    'about.md',
    'Method, gaps and corrections — MV Barima documented record',
    'Method, gaps and corrections',
    'How the corpus was assembled, what could not be retrieved, which documents were searched for and not found, '
    'and the eighteen corrections made after an adversarial check.',
    'about.html',
    '<div class="note"><h4>Why the gaps are listed before anything else</h4><p>A record that does not state what '
    'it is missing cannot be checked. Several documents were searched for and not found at all: any published '
    'capacity certificate, any gazetted commission instrument, any official death toll. Every revision to this '
    'site is logged on the <a href="changelog.html">revisions page</a>.</p></div>'))

write('questions.html', build_prose_page(
    'questions.md',
    'Questions of the record — MV Barima documented record',
    'Questions of the record',
    'Five questions about the MV Barima disaster, answered plainly from the 209 documents this '
    'archive holds — including what the record cannot settle.',
    'questions.html',
    '<div class="note warn"><h4>This page answers; the rest of the site reports</h4><p>Everywhere '
    'else this archive only sets out what published sources said, attributed. Here it answers '
    'directly. Evidence is named; where the record cannot settle something, that is the answer '
    'given. If this page and the record pages disagree, the record pages are right. Question five '
    'draws on international instruments held outside the archive, and says so. Nothing here bears '
    'on the guilt of the three men charged on 28 July, who have not been tried.</p></div>',
    transform=lambda b: collapsible_qa(inject_charts(b))))

write('changelog.html', build_prose_page(
    'changelog.md',
    'Revisions — MV Barima documented record',
    'Revisions',
    'Every change made to this site since first publication: what was added, what was corrected, and what '
    'a change was based on.',
    'changelog.html',
    '<div class="note"><h4>Why this page exists</h4><p>This record was compiled while the facts were still '
    'moving, so it will keep changing. A record that revises itself silently cannot be checked. Every entry '
    'below states what changed, when, and on what source.</p></div>'))

# the analysis page was replaced by positions.html; remove any stale copy
_stale = os.path.join(OUT, 'analysis.html')
if os.path.exists(_stale):
    os.remove(_stale)
    print('removed stale analysis.html')

write('data/sources.json', json.dumps(
    {'compiled': BUILT, 'count': len(records),
     'note': 'Research metadata and annotations only. Full source text is not included; see url for the original.',
     'sources': [{k: v for k, v in r.items() if k != 'file'} for r in records]},
    indent=1, ensure_ascii=False))

# stats for the console
print('outlets:', len({r['outlet'] for r in records}))
print('kinds  :', collections.Counter(r['kind'] for r in records).most_common())
print('flagged:', sum(1 for r in records if r['flagged']))
print('no url :', sum(1 for r in records if not r['url']))
print('no summ:', sum(1 for r in records if not r['summary']))
print('pages  :', 6 + len(records))
