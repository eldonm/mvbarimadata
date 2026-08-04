#!/usr/bin/env python3
"""Build the public MV Barima research site from the private full-text archive.

Publishes metadata, research summaries, extracted claims and short attributed
quotations only. Full article text is NOT republished — every source page links
out to the publisher. Official/state documents are treated the same way here for
consistency of presentation.
"""
import glob, json, os, re, sys, html, shutil, collections
import yaml
import markdown as md

ARCHIVE = '/home/claude/mvb/archive'
DELIV   = '/home/claude/mvb/site_content'   # neutralised site copy, not the private working notes
OUT     = '/home/claude/mvb/site'
BUILT   = 'Sunday 26 July 2026, last revised Tuesday 4 August 2026'
# Absolute origin, needed for Open Graph — social crawlers will not resolve a
# relative image or URL. Change this one line if the site moves domain.
SITE_URL = 'https://mvbarimadata.pages.dev'

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
    'social-media': 'Social media',
    'expert-submission': 'Expert submission',
    'historical': 'Historical & context',
    'reference': 'Historical & context',
    'analysis': 'Historical & context',
}
SOCIAL_NOTE = (
    'Self-published on social media by the named account. No editor stood between the '
    'author and publication, and nothing in it has been verified by this archive or by any '
    'outlet unless a separate document says so. It is held because the speaker is on the '
    'record, not because the content is established.')


def is_social(rec):
    return 'social-media' in (rec.get('tier') or '').lower()


EXPERT_NOTE = (
    'An unsolicited analysis submitted to this archive by its named author and published here in '
    'full. It is not journalism, not a state document, and not a finding of any tribunal &mdash; it '
    'is one qualified person&rsquo;s reading of the statute book, offered as an aid to the Commission '
    'of Inquiry. Its author states he is not admitted to practise law in Guyana, that nothing in it '
    'is legal advice, that it makes no finding of fact, and that every person charged or named is '
    'presumed innocent. Weigh it on its reasoning and its citations, both of which it supplies.')


def is_expert(rec):
    return 'expert-submission' in (rec.get('tier') or '').lower()


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
# A two-tier masthead. The record itself sits on the primary row; the apparatus
# behind it — the documents, the method, the log of changes — sits on a quieter
# utility row with the theme control. Everything stays one click away and
# nothing hides behind a menu, which matters for a reference site.
NAV_PRIMARY = [
    ('index.html', 'Overview'), ('timeline.html', 'Chronology'),
    ('facts.html', 'The figures'), ('positions.html', 'Positions'),
    ('questions.html', 'Questions'),
]
NAV_UTILITY = [
    ('sources.html', 'Documents'), ('counterfactual.html', 'The road not taken'),
    ('about.html', 'Method &amp; gaps'), ('changelog.html', 'Revisions'),
]
NAV = NAV_PRIMARY + NAV_UTILITY

CURATTR = ' aria-current="page"'
THEME_ICON = (
    '<svg viewBox="0 0 20 20" width="16" height="16" aria-hidden="true" focusable="false">'
    '<path class="ico-moon" d="M15.5 12.4A6.6 6.6 0 0 1 7.6 4.5a6.6 6.6 0 1 0 7.9 7.9z" '
    'fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/>'
    '<g class="ico-sun" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round">'
    '<circle cx="10" cy="10" r="3.4"/><path d="M10 2.2v1.9M10 15.9v1.9M2.2 10h1.9M15.9 10h1.9'
    'M4.5 4.5l1.35 1.35M14.15 14.15l1.35 1.35M15.5 4.5l-1.35 1.35M5.85 14.15L4.5 15.5"/></g></svg>')


def head(title, desc, cur, depth=0, path=None):
    p = '../' * depth
    # `cur` drives which nav item is highlighted; `path` is where the page
    # actually lives. They differ for source pages, which highlight Documents.
    path = path or cur

    def row(items):
        return ''.join('<a href="{}{}"{}>{}</a>'.format(
            p, h, CURATTR if h == cur else '', t) for h, t in items)

    nav_primary = row(NAV_PRIMARY)
    nav_utility = row(NAV_UTILITY)
    # Source pages share one card; every top-level page has its own.
    ogcard = cur[:-5] if (not depth and cur.endswith('.html')) else 'source'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{SITE_URL}/{path}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="{'article' if depth else 'website'}">
<meta property="og:site_name" content="MV Barima — documented record">
<meta property="og:locale" content="en_GB">
<meta property="og:url" content="{SITE_URL}/{path}">
<meta property="og:image" content="{SITE_URL}/assets/og/{ogcard}.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(title)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{SITE_URL}/assets/og/{ogcard}.png">
<meta name="twitter:image:alt" content="{esc(title)}">
<link rel="stylesheet" href="{p}assets/style.css">
<script src="{p}assets/site.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <div class="masthead">
    <div class="masthead-in">
      <a class="brand" href="{p}index.html">
        <span class="bmark">MV Barima</span><span class="bsub">Documented record</span></a>
      <nav class="main" aria-label="Main">{nav_primary}</nav>
    </div>
  </div>
  <div class="utility">
    <div class="utility-in">
      <nav class="util" aria-label="Archive">{nav_utility}</nav>
      <button class="themebtn" type="button" aria-label="Switch to dark theme">{THEME_ICON}</button>
    </div>
  </div>
</header>
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
      <p>Compiled {built}. The Commission of Inquiry was sworn in on 30 July 2026 at a ceremony closed to the press; its
      establishing instrument was still not gazetted, and figures were still moving. Read <a href="{p}about.html">Method &amp; gaps</a> before citing anything here.</p>
      <p>This site records what the sources say and who said it. Outside the questions page it does not
      advance an explanation of the cause, and it makes no recommendation.</p>
      <p class="tiny">Research, retrieval, cross-checking and reasoning carried out with
      <strong>Claude Opus 5</strong>, Anthropic&rsquo;s frontier model. Every claim is traceable to a named
      published document; corrections are logged on the <a href="{p}changelog.html">revisions page</a>.</p>
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
        <li><a href="{p}anomalies.html">What doesn&rsquo;t add up</a></li>
        <li><a href="{p}counterfactual.html">The road not taken</a></li>
        <li><a href="{p}ask.html">Ask a question</a></li>
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
    # md_in_html lets a block marked markdown="1" have its contents processed,
    # which the plain-language summary on the anomalies page relies on.
    body = md.markdown(raw, extensions=['tables', 'sane_lists', 'attr_list', 'md_in_html'])
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

# ---------------------------------------------------------------- developments
# A short spine of the story, for a reader arriving cold. It is deliberately not
# the chronology: the chronology records everything the corpus holds, and this
# records only the turns. Each line has to be a moment after which something was
# different. `kind` drives the colour of the marker, nothing else.
DEVELOPMENTS = [
    ('vessel',  '1939', 'The <em>Barima</em> is built', 'Ferguson Brothers, Port Glasgow, for the British Guiana Railways, ordered through the Crown Agents. She is the last of three sisters. The build year is <strong>contested</strong> &mdash; most coverage says 1939 and the builder&rsquo;s engine register supports it; Kaieteur News says 1938, and MARAD refers to a &ldquo;1938 rating&rdquo;.'),
    ('vessel',  '2 Oct 2015', 'A master mariner names this ship in print', 'Capt. R. E. W. Adams writes to Stabroek News citing an inspection that found her deck and winch area &ldquo;a mass of junk and rust&rdquo;, and argues such a vessel would be barred from sea or scrapped elsewhere in the Caribbean. Eleven years before she sank.'),
    ('vessel',  '2017', 'The state chooses rehabilitation over replacement', 'G$150.6m is spent on her, including the installation of two engines. The 1939 hull stays.'),
    ('vessel',  '2019', 'She becomes the only vessel on the run', 'The <em>Lady Northcote</em> is reported withdrawn, leaving an 80-year-old ship as the sole practical link between Georgetown and Port Kaituma. <strong>Contested</strong>: Kaieteur News reported on 24 July 2026 that the <em>Lady Northcote</em> &ldquo;continues operating&rdquo;.'),
    ('vessel',  'Dec 2022', 'G$1.4bn is awarded for a new Port Kaituma stelling', 'It reaches about 90% in February 2024, then stalls on a failed tie-rod specification and design deficiencies. It is still unfinished on the day she sinks.'),
    ('vessel',  '2023', 'A replacement arrives and never takes the route', 'The US$12.7m India-funded <em>MV Ma Lisha</em> is commissioned and Parliament is told it will replace the <em>Barima</em>. Why it never sailed the route is <strong>contested</strong>: the Prime Minister says the Port Kaituma wharf works were unfinished; residents and contemporaneous reporting say her cargo capacity was inadequate for the route. Both may be true.'),
    ('vessel',  'Mar 2026', 'Stabroek News ceases print after about forty years', 'Guyana&rsquo;s principal independent daily, and the paper that carried the 2015 warning, goes into voluntary liquidation four months before the sinking.'),
    ('vessel',  '9 Mar 2026', 'A G$124.5m hull repair is put out to tender', 'Bidding documents specify examination of some 10,000 square metres of hull plating and frames, with deteriorated sections renewed where necessary. Four months before she sinks. Whether the contract was ever awarded or the work ever done is <strong>not established</strong> in this record, and the Opposition Leader alleges it was not.'),

    ('disaster','Sat 18 Jul 2026, 15:15', 'She sails for Port Kaituma', 'From the Transport &amp; Harbours Department wharf at Kingston, Georgetown. The manifest records 116 passengers and 17 crew. A CCTV review will later put 179 people aboard.'),
    ('disaster','18 Jul, about 23:01', 'A distress call is received', 'She capsizes off Iron Punt at the mouth of the Pomeroon River, in three to nine metres of water. Survivor accounts describe an engine repaired at sea and water entering from about 20:00.'),

    ('response','19 Jul', 'The minister names a cause on day one', 'Juan Edghill: &ldquo;One word&hellip; mischief.&rdquo; He gives 284 tonnes licensed against 268 manifested, and discloses that only 35 of the first 67 rescued appear on the manifest. Two crew test positive for cannabis.'),
    ('response','20 Jul', 'The loading team is suspended, and the wharf video is seized', 'The suspension is announced by Facebook post. Police extract the CCTV from the Kingston Goods Wharf. The working complement becomes 179, up from the manifest&rsquo;s 133.'),
    ('response','21&ndash;22 Jul', 'The regulator clears the vessel', 'MARAD&rsquo;s Director-General states she was &ldquo;not overloaded&rdquo;, citing the load line. Kaieteur News publishes its own tally of 103 dead. Three days of national mourning are declared. Edghill confirms she was uninsured.'),
    ('response','24 Jul', 'The recovery figure reaches 73 and stops', '73 recovered, 69 identified, about 30 unaccounted for. Boats are said to be standing by to right her. The figure of 73 will not move again.'),

    ('inquiry', '25 Jul', 'Families are asked to accept the wreck as a memorial', 'A draft Declaration of Agreement is circulated asking them to concur that the vessel remain undisturbed. The same day, President Ali announces a Commission of Inquiry.'),
    ('inquiry', '26&ndash;27 Jul', 'Five commissioners are named; the divers say the wreck cannot be entered', 'Nothing is gazetted. The French dive team tells relatives it is too dangerous to go inside &mdash; two days after the memorial document went out. Parliament sits and the opposition protests inside the chamber.'),

    ('legal',   '28 Jul', 'Three employees of the operator are charged with murder', 'Captain Kevin Price, Chief Mate Rondell Roberts and Goods Superintendent Delon Granderson face 72 counts jointly and are remanded. <strong>All three are accused persons who have not been tried, and nothing on this site is a view on their guilt or innocence.</strong> No charge touches the regulator, the board or either ministry. The Prime Minister says the wreck is &ldquo;likely to remain there as is&rdquo;.'),
    ('legal',   '29 Jul', 'The captain weeps in court and the streets fill', 'He says the vessel was unfit to sail. Protests at Den Amstel, Melanie Damishana and the Office of the President. Edghill, on the resignation calls: &ldquo;My life is in God&rsquo;s hands and that&rsquo;s not today.&rdquo; A retired ship pilot sends this archive 253 pages on the statute book.'),

    ('inquiry', '30 Jul', 'The Commission is sworn in, with the press shut out', 'At State House before the Chief Magistrate, the chairman virtually, streamed on the President&rsquo;s social media instead. The enabling statute is named officially for the first time. No instrument, no published terms, no secretary, no deadline, no budget.'),
    ('response','30 Jul', 'The government&rsquo;s own release lowers the toll to 72', 'After six days of official 73, with no announcement and no explanation, while four outlets carry 73 the same day. This archive keeps 73, and records the 72 as a divergence.'),
    ('inquiry', '30 Jul', 'A former minister of the responsible ministry treats the missing certificate as routine', 'On a broadcast interview, David Patterson &mdash; who held the Ministry of Public Works &mdash; treats annual certification of these vessels as routine: &ldquo;how can you say you don&rsquo;t have the registration certificate of a document&hellip; but you are certifying it every year.&rdquo; He also says the operator has not been audited since about 2005 and argues the murder charges will silence the operator&rsquo;s management as well as the accused. <strong>Uncorroborated</strong>, and captured from a machine caption track.'),
    ('inquiry', '4 Aug', 'The inquiry finally gets its papers &mdash; and the secretary is questioned the same day', 'The terms of reference are published in the Extraordinary Gazette after seventeen days: six heads including <strong>regulatory oversight by state entities</strong>, a <strong>two-month deadline</strong>, public hearings, and power to refer criminal negligence or official misconduct straight to prosecutors. A Secretary is named &mdash; and a former minister immediately objects that he holds a function in the ministry MARAD answers to. <strong>No instrument number, no budget.</strong>'),
    ('inquiry', '1&ndash;2 Aug', 'The state moves to raise the ship, and the memorial plan disappears', 'MARAD invites salvage contractors, closing 14 August, requiring bidders to protect &ldquo;forensic evidence for the ongoing Commission of Inquiry&rdquo;. <strong>No government statement anywhere says the memorial proposal &mdash; put to bereaved families in writing on 25 July &mdash; has been dropped.</strong> The opposition attacks the timetable rather than the decision: on its account salvage cannot start before late August, while &ldquo;salt water is unforgiving&rdquo;.'),
    ('legal',   '31 Jul', 'The defence moves to stop the inquiry and the prosecution running together', 'Counsel for the three accused prepares a court challenge, argues the case belongs under the Shipping Act rather than common-law murder, puts seaworthiness on the regulator, and makes sight of the terms of reference a condition of his clients taking part at all. The Opposition Leader escalates the salvage offer to a formal written request and reports no government reply of any kind.'),
]

def developments(compact=True):
    """The story in twenty-four turns. `compact` collapses the pre-disaster half
    behind a disclosure, because a reader arriving on the landing page wants
    the fortnight, not the ninety years."""
    def row(k, when, head_, body):
        return (f'<li class="dev dev-{k}"><span class="devdate">{when}</span>'
                f'<span class="devbody"><strong>{head_}</strong>'
                f'<span class="devtext">{body}</span></span></li>')
    pre  = [r for r in DEVELOPMENTS if r[0] == 'vessel']
    post = [r for r in DEVELOPMENTS if r[0] != 'vessel']
    pre_html  = ''.join(row(*r) for r in pre)
    post_html = ''.join(row(*r) for r in post)
    if compact:
        return (f'<details class="devpre"><summary>Before the sinking &mdash; '
                f'{len(pre)} turns, 1939 to March 2026</summary>'
                f'<ul class="devs">{pre_html}</ul></details>'
                f'<ul class="devs">{post_html}</ul>')
    return f'<ul class="devs">{pre_html}{post_html}</ul>'


ALT_DEVELOPMENTS = [
    ('disaster','Sat 18 Jul, 11pm', 'One agency takes charge of the rescue', 'The sea rescue centre runs the night. Every boat and plane sent out is written down with the time. One agency counts the people pulled from the water, so the count cannot go wrong.'),
    ('response','Sun 19 Jul', 'Nobody is blamed on day one', 'The Minister does not say &ldquo;mischief&rdquo;. He says the ship was licensed for 397 people and carried 250 life jackets, that this does not add up, and that he does not yet know why. He shows the ship&rsquo;s papers &mdash; or says plainly that he cannot find them.'),
    ('response','Mon 20 Jul', 'The rescue log is made public, gaps and all', 'Including any hours it shows with no government boat in the water. The wharf video is used to say what <em>cargo</em> went on board, not only how many people.'),
    ('response','Tue 21 Jul', 'One set of numbers, every day', 'On board, saved, found, named, still missing &mdash; and the total who did not come home. Same time each day, same officer. Families are told before the press.'),
    ('response','Wed 22 Jul', 'MARAD steps back from judging its own work', 'It passed this ship as fit to sail. So it cannot be the one to say the ship was fit. It hands over its whole file instead. The state also admits the ship had no insurance. (Asked for by the Transparency Institute the next day; we put it one day early.)'),
    ('legal',   'Thu 23 Jul', 'Two ministers step aside, and someone asks about the deadline', 'Stepping aside is not resigning and is not guilt. It just means they do not run the department the inquiry is examining. The Attorney General is asked whether families face a time limit to claim. If they do, the state promises in writing not to use it.'),
    ('inquiry', 'Fri 24 Jul', 'Outside investigators are asked in', 'The government owned the ship, inspected the ship and passed the ship. It cannot investigate itself and be believed.'),
    ('inquiry', 'Sat 25 Jul', 'Grieving families are asked nothing yet', 'No paper about the wreck goes to any family until the divers have reported and the prosecutor has said in writing whether the ship is needed as evidence. The inquiry&rsquo;s draft terms go out for comment, and Indigenous councils are asked what should be in them.'),
    ('inquiry', 'Mon 27 Jul', 'Parliament debates it, and the inquiry gets its papers', 'Signed and published before anyone is appointed, with a secretary, a deadline and a budget. A bill to protect families&rsquo; right to claim goes to the House the same day.'),
    ('legal',   'Tue 28 Jul', 'The inquiry&rsquo;s evidence rules are settled first', 'Anyone who may be asked to speak is told in advance what their words can be used for. <strong>Nothing here changes who gets charged, or when. That is the prosecutor&rsquo;s decision and hers alone.</strong>'),
    ('inquiry', 'Thu 30 Jul', 'The inquiry is sworn in with the press in the room', 'It starts on the paperwork &mdash; certificates, loading orders, contracts, repair records &mdash; because no silence can hide a document.'),
    ('response','Fri 31 Jul', 'The ministry publishes its own wharf file', 'Why a G$1.4 billion wharf failed, from the ministry that built it &mdash; not left for the opposition to reveal. With it, the March repair tender for the <em>Barima</em>, and whether that work was ever done.'),
    ('vessel',  'Sat 1 Aug', 'The law is checked, and a new bill is promised', 'A retired ship pilot read the Acts and found no duty on anyone to count passengers and keep the tally ashore, no life-jacket rule he could match to a ferry this size, and no mention anywhere of the loading boss&rsquo;s job. <em>That is one man&rsquo;s reading, uncorroborated &mdash; and his own second analysis of 3 August reaches a different view on the safety code.</em> A bill to fix it within thirty days.'),
    ('future',  'Aug 2026', 'The inquiry works on paper, and the ship is raised', 'It starts with documents &mdash; certificates, loading orders, contracts, repair records, the video, the rescue log &mdash; because no silence can hide a file. The prosecutor says in writing whether the wreck is evidence, the families are asked <em>after</em> the divers report rather than before, and the Government pays to lift her.'),
    ('future',  'Sep 2026', 'A first partial report, and the money starts', 'On the rescue and the counting only, published whole on the day it is handed over. The payment scheme opens with a published rate, a named officer and a running total, and every payment says on its face that it is not a settlement.'),
    ('future',  'Oct 2026', 'The law changes', 'Passengers must be counted and the count kept ashore. A life-jacket rule that covers ferries this size. The loading boss becomes a real job in law. An accident investigator who can investigate the Government&rsquo;s own ships. The six-month time limit is scrapped for this disaster.'),
    ('future',  'Dec 2026', 'The deadline passes and takes nothing with it', 'On the old law this is the month families would have had to file notice or lose their claim forever. It passes without harming anybody, because it was dealt with in July. <strong>The quietest turn on this page and the most important.</strong>'),
    ('future',  'Early 2027', 'The full report, published whole on the day', 'What it concludes about the sinking is not for this page to invent. What can be said is that the Cabinet does not read it first, and the Government answers every recommendation in writing within sixty days &mdash; accept, reject, or accept in part, and why.'),
    ('future',  'Mid 2027', 'The boats, and the wharf', 'Port Kaituma is finished and its final cost published. The newer ferry takes the route. Cargo is separated from passengers. Every ferry&rsquo;s certificate goes online each year &mdash; the cheapest thing on this list and the one that makes the rest keep themselves honest. A memorial is built with the families, not proposed to them.'),
]

def alt_developments():
    """The whole alternate arc, in the same visual grammar as the landing page's
    real timeline so a reader can hold the two side by side. A break row and
    hollow markers separate the half set against the record from the half that
    is invented outright, because that difference has to be visible before it
    is read."""
    out, broken = [], False
    for k, when, head_, body in ALT_DEVELOPMENTS:
        if k == 'future' and not broken:
            out.append('<li class="devbreak">Everything below this line is invented &mdash; '
                       'a plan, not a forecast</li>')
            broken = True
        out.append(f'<li class="dev dev-{k}"><span class="devdate">{when}</span>'
                   f'<span class="devbody"><strong>{head_}</strong>'
                   f'<span class="devtext">{body}</span></span></li>')
    return '<ul class="devs">' + ''.join(out) + '</ul>'


def questions_index():
    """Read the question headings straight out of questions.md so the landing
    page cannot drift from the page it advertises. Returns [(n, title), ...]."""
    raw = open(os.path.join(DELIV, 'questions.md'), encoding='utf-8').read()
    return [(m.group(1), m.group(2).strip())
            for m in re.finditer(r'^## (\d+)\.\s*(.+)$', raw, re.M)]


def questions_panel():
    qs = questions_index()
    links = ''.join(
        '<li><a href="questions.html#q{n}"><span class="qn">{n}</span>'
        '<span>{t}</span></a></li>'.format(n=n, t=E(t)) for n, t in qs)
    return '''
<section>
  <div class="leadpanel">
    <p class="eyebrow aiflag">Frontier AI analysis &middot; Claude Opus 5, reasoning across all {n} documents</p>
    <h2 style="margin-top:0">What doesn&rsquo;t add up</h2>
    <p class="lede wrap-read">Twenty-eight things in this record that do not reconcile. Figures that moved without
    explanation, documents that should exist and have not appeared, and official accounts contradicted by other
    official accounts. The short version, in plain language:</p>
    <ul class="leads"><li><span class="n">1</span><div><strong>The number Edghill used to clear the boat measures space inside the hull, not weight it can carry</strong><span class="sub">Set against the carrying figure, the manifest is about 70 tonnes over &mdash; that comparison is this archive&rsquo;s inference, not a finding. What is documented is that nobody in government has corrected the category error in seventeen days.</span></div></li><li><span class="n">2</span><div><strong>One sheet of paper would settle most of this. Nobody will produce it</strong><span class="sub">The safety certificate the regulator says it relied on. Requested on day one.</span></div></li><li><span class="n">3</span><div><strong>Families were asked to leave the wreck on the seabed two days before the divers called it too dangerous to move</strong><span class="sub">It is the only physical evidence, and about thirty people are still inside it. On 1 August the state reversed and tendered to raise her &mdash; without ever saying the memorial proposal had been dropped.</span></div></li><li><span class="n">4</span><div><strong>On day one the minister put the fault at ground level. Nine days later three ground-level staff were charged and nobody else</strong><span class="sub">No charge, suspension or accounting at the regulator, the board, or either ministry.</span></div></li><li><span class="n">5</span><div><strong>The government answered most freely in the first two days, then stopped as questions moved upward</strong><span class="sub">The one figure showing whether unticketed passengers lived or drowned was given, then refused.</span></div></li><li><span class="n">6</span><div><strong>Seventy-two murder charges. Seventy-three bodies recovered</strong><span class="sub">No official statement says how many charges were laid.</span></div></li><li><span class="n">7</span><div><strong>Nobody has ever said how any of these people died</strong><span class="sub">No cause of death, no coroner, no inquest, no pathologist, in any account of the disaster. Bodies were identified from photographs, released and buried. Seventy-two murder charges rest on those deaths.</span></div></li><li><span class="n">8</span><div><strong>The inquiry into these deaths was sworn in with the press shut out</strong><span class="sub">Streamed on the President&rsquo;s own social media instead. The terms, a two-month deadline and a secretary finally arrived on 4 August &mdash; seventeen days on, and the secretary&rsquo;s independence was questioned the same day. Still no instrument number, no budget, no call for submissions.</span></div></li><li><span class="n">9</span><div><strong>Then the government&rsquo;s own release quietly lowered the bodies recovered from 73 to 72</strong><span class="sub">Six days of official 73, then 72 with no announcement &mdash; while four other outlets still said 73 the same day.</span></div></li><li><span class="n">10</span><div><strong>Licensed for 397 people. Two hundred and fifty life jackets aboard</strong><span class="sub">Both numbers from the same minister at the same press conference on day one. He called it meeting the required standard. The government has never reconciled them, and how many places the eight liferafts held is not on record at all.</span></div></li><li><span class="n">11</span><div><strong>There is video of the boat being loaded. The state has had it since day two</strong><span class="sub">It told us how many people it shows. It has never said what it shows about the cargo &mdash; the thing three men were charged over.</span></div></li><li><span class="n">12</span><div><strong>Money is going to bereaved families at figures nobody can explain, and a deadline may be running behind it</strong><span class="sub">No published scheme, no rate, no total. On the only published reading of the statute, a claim must be filed by about 18 January 2027 &mdash; and there is no insurer.</span></div></li></ul>
    <p class="wrap-read small muted"><strong>Produced by Claude Opus 5, Anthropic&rsquo;s frontier model,
    reasoning across the whole corpus &mdash; no human investigator assembled it.</strong> Each finding gives the
    anomaly, then the innocent explanation at its strongest, then the document that would settle it, and names its
    sources so you can check the reasoning. The page opens by correcting four of this archive&rsquo;s own errors.
    It accuses nobody of a crime: three men have been charged and not tried, and nothing on it bears on their
    guilt or innocence.</p>
    <p style="margin-bottom:0"><a class="origin" href="anomalies.html">Read the analysis</a></p>
  </div></section>

<section>
  <div class="card askpanel">
    <p class="eyebrow">Answered by AI, reasoning over the whole archive</p>
    <h2 style="margin-top:2px">Questions of the record</h2>
    <p class="wrap-read muted" style="margin-bottom:18px">The rest of this site reports only what published
    sources said, attributed. On one page the archive answers directly, reading across all {n} documents:
    the short answer first, the working underneath, and a plain statement wherever the record cannot settle
    the question. <a href="ask.html"><strong>Anyone can send a question in.</strong></a></p>
    <ul class="qlinks">{links}</ul>
    <p style="margin-bottom:0"><a class="origin" href="questions.html">Read the answers</a><a class="ghost" href="ask.html">Ask a question</a></p>
  </div></section>

<section>
  <div class="card">
    <p class="eyebrow">Counterfactual analysis &mdash; not the record</p>
    <h2 style="margin-top:2px">The road not taken</h2>
    <p class="wrap-read muted" style="margin-bottom:14px">Imagine the Government had an AI advisor from the
    night the <em>Barima</em> went down. One job: keep the people&rsquo;s trust. This is what it would have said
    to do &mdash; day by day through the first fortnight, then month by month to the end. Almost none of it is
    new: nearly every step was asked for in public at the time, by lawyers, village councils, opposition MPs,
    newspapers and a retired ship captain. <strong>The advice was given. It just wasn&rsquo;t taken.</strong></p>
    <p class="wrap-read small muted" style="margin-bottom:18px"><strong>None of it happened.</strong> The ship
    still sinks and about 103 people still do not come home. What changes is only what the Government said and
    showed afterwards. Nothing on the page touches the court case against the three men charged and not tried.</p>
    <p style="margin-bottom:0"><a class="origin" href="counterfactual.html">Read the comparison</a></p>
  </div></section>
'''.format(links=links, n=len(records))

# The submission route. Web3Forms handles delivery; the access key below is a
# public client-side key by design (their dashboard says so explicitly), so it
# lives in the built HTML like any other form action. No secret is exposed.
WEB3FORMS_KEY = 'bf6a5eff-c197-4aa4-842c-8949b80a5ca2'


def build_ask():
    return head('Ask a question — MV Barima documented record',
                'Send a question about the MV Barima disaster. It will be answered from the '
                'documents this archive holds, and published with its answer.',
                'ask.html') + f'''
<section style="margin-top:44px;">
  <p class="eyebrow">Open to anyone</p>
  <h1>Ask a question</h1>
  <p class="lede wrap-read">Send a question about the <em>MV Barima</em> disaster and it will be answered on the
  <a href="questions.html">questions page</a>, from the {len(records)} documents this archive holds. If the record
  cannot answer it, that is published too &mdash; what the record cannot answer is itself worth knowing.</p>
</section>

<section>
  <div class="grid" style="grid-template-columns:minmax(0,1.15fr) minmax(0,0.85fr); gap:34px; align-items:start;">
    <div class="card">
      <form class="askform" id="askform" action="https://api.web3forms.com/submit" method="POST">
        <input type="hidden" name="access_key" value="{WEB3FORMS_KEY}">
        <input type="hidden" name="from_name" value="MV Barima archive">
        <input type="hidden" name="subject" value="MV Barima archive — new submission">
        <!-- Web3Forms honeypot: a real person never fills this in. -->
        <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off">

        <div class="ffield">
          <label for="ask-type">This is a</label>
          <select id="ask-type" name="Type" required>
            <option value="Question">Question &mdash; something you want the archive to answer</option>
            <option value="Correction">Correction &mdash; something on this site is wrong</option>
            <option value="Document">A document the archive is missing</option>
          </select>
        </div>

        <div class="ffield">
          <label for="ask-msg">Your question, in your own words</label>
          <textarea id="ask-msg" name="Message" rows="7" required
            placeholder="Be as specific as you like. Questions that name a date, a figure or a document are the easiest to answer well."></textarea>
        </div>

        <div class="frow">
          <div class="ffield">
            <label for="ask-name">Name <span class="opt">optional</span></label>
            <input id="ask-name" name="Name" type="text" autocomplete="name">
          </div>
          <div class="ffield">
            <label for="ask-email">Email <span class="opt">optional</span></label>
            <input id="ask-email" name="Email" type="email" autocomplete="email">
          </div>
        </div>
        <p class="tiny muted" style="margin:-4px 0 18px">An address is only needed if you want a reply. Neither your
        name nor your address is published unless you ask for it.</p>

        <button class="origin" type="submit">Send it</button>
        <p class="askstatus" id="askstatus" role="status" aria-live="polite"></p>
        <noscript><p class="tiny muted" style="margin-top:12px">With JavaScript off, sending will take you to a
        confirmation page on web3forms.com. That is expected.</p></noscript>
      </form>
    </div>

    <div>
      <h2 style="margin-top:0">What happens next</h2>
      <p class="small muted">Every question is answered on the questions page, with the evidence named and the limits
      stated. The answer is written by Claude Opus 5 reading across the whole corpus, and it is checked before it is
      published &mdash; against the documents, and adversarially, which is how this archive has caught and corrected
      its own errors. Those corrections are logged on the <a href="changelog.html">revisions page</a>.</p>
      <p class="small muted">Questions are published with their answers. Your name and address are not, unless you ask
      for them to be.</p>
      <p class="small muted">If you are reporting a <strong>correction</strong>, the most useful thing you can send is
      the document. This archive would rather be corrected than be consistent.</p>
      <p class="small muted">If you hold a document this archive is missing &mdash; a certificate, a log, a tender file,
      an inspection report &mdash; the <a href="about.html">method and gaps page</a> lists what has been searched for
      and not found.</p>
      <h2>What this cannot do</h2>
      <p class="small muted">This archive does not give legal advice, does not speculate about the guilt or innocence
      of the three men charged on 28 July, and does not take a position on who should resign. Questions on those
      subjects will be answered as questions about what the record shows, or answered by saying that it shows
      nothing.</p>
    </div>
  </div>
</section>
''' + foot()

def build_index():
    tiles = [
        ('179', '', 'People aboard', 'Reconstructed from boarding-area CCTV. The manifest said 133.'),
        ('73', '', 'Bodies recovered', 'Official from 24 to 29 July. The 30 July release says 72, unexplained.'),
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
    qpanel = questions_panel()
    devhtml = developments(compact=True)
    chainhtml = '<div class="chdr">How the disaster was built</div><div class="chdr">What would have broken the chain</div>'
    for i, (hd, bd, fx) in enumerate(CHAIN, 1):
        last = ' style="border-bottom:none"' if i == len(CHAIN) else ''
        chainhtml += (f'<div class="lnk"{last}><span class="num">{i}</span>'
                      f'<span class="tx"><b>{hd}</b> {bd}</span></div>'
                      f'<div class="fix"{last}><span class="num fixn">{i}</span><span class="tx">{fx}</span></div>')

    return head('MV Barima — the documented record | Guyana ferry disaster, 18 July 2026',
                f'What {len(records)} published documents record about the sinking of the Guyanese ferry MV Barima on '
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
  of Inquiry&rsquo;s five members were sworn in on 30 July 2026, at a ceremony the press was not invited to, and its
  establishing instrument has still not been gazetted;
  on 28 July three employees of the operator were charged with murder and remanded, and they are accused persons
  who have not been tried; and the figures are still being revised. Every claim links back to its source so it can
  be checked. Changes to this site are logged on the <a href="changelog.html">revisions page</a>.</p>
</section>

<section>
  <div class="grid g5">{tilehtml}</div>
</section>

<section>
  <p class="eyebrow">How it happened, in twenty-four turns</p>
  <h2 style="margin-top:2px">Notable developments</h2>
  <p class="wrap-read muted" style="margin-bottom:20px">The turns in the story, from the yard that built her to
  today. Each entry is a moment after which something was different. The full record &mdash; every dated entry the
  corpus supports, with conflicts marked &mdash; is on the <a href="timeline.html">chronology page</a>.</p>
  {devhtml}
  <div class="devkey">
    <span><i style="background:var(--muted)"></i>Before the sinking</span>
    <span><i style="background:var(--ink)"></i>The sinking</span>
    <span><i style="background:var(--s1)"></i>The response</span>
    <span><i style="background:var(--s2)"></i>The charges</span>
    <span><i style="background:var(--s3)"></i>The inquiry</span>
  </div>
  <p class="small muted" style="margin-top:18px"><a href="timeline.html">The full chronology &rarr;</a><span class="sep" aria-hidden="true"> &middot; </span><a href="counterfactual.html">The Road Not Taken &rarr;</a> <span class="tiny muted">(a counterfactual &mdash; not the record)</span></p>
</section>
{qpanel}
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
      <h3 style="margin-top:0">Three stated capacity figures, and 250 life jackets</h3>
      <p class="small muted">Edghill gave 284 tonnes and 397 passengers on 19 July. MARAD&rsquo;s Director-General
      gave 126 tonnes on 21&ndash;22 July and 120 tonnes on 24&ndash;25 July, both with 394 passengers, and said
      of the increase from the 1938 rating: &ldquo;I don&rsquo;t have that information.&rdquo; The government&rsquo;s
      own release of 19 July puts 250 life jackets aboard a vessel the same minister said was licensed for 397
      people, and describes that as meeting the required standard. No certificate of survey, load line or
      passenger capacity appears in the corpus.</p>
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
  <p class="wrap-read muted">As at 30 July 2026, the day the commissioners were sworn in, the dispute on record is
  less about cause than about who should investigate and on what terms. The three summaries below are the
  parties&rsquo; own stated positions.</p>
  <div class="grid g3">
    <div class="card tr">
      <h3>The Government</h3>
      <p>President Ali named the five-member Commission of Inquiry on 26 July: Justice Godfrey Phillip Smith of
      Belize as chair, with Capt. Hamada Fouda (Jamaica), Nyree Dawn Alfonso (Trinidad and Tobago), Dr Andrzej
      Jasionowski (Poland) and Rear Admiral (Ret&rsquo;d) Hayden Pritchard (Trinidad and Tobago). Terms of
      reference were announced covering loading, boarding, seaworthiness, maintenance history, crew competence,
      lifesaving arrangements, weather and the search-and-rescue response. The establishing instruments were
      described as still being finalised. All five were sworn in at State House on 30 July before the Chief
      Magistrate, the chairman virtually, at a ceremony the press was not invited to and which was streamed on
      the President&rsquo;s social media accounts instead. The same day the Department of Public Information named
      the enabling statute for the first time &mdash; the Commissions of Inquiry Act, Cap. 19:03, s. 2(1) &mdash;
      and named nothing else: no gazetted instrument, no published terms, no secretary, no deadline, no budget,
      no rules of procedure and no route for public submissions.</p>
    </div>
    <div class="card tr">
      <h3>The parliamentary opposition</h3>
      <p>APNU states the National Assembly should set the terms of reference and include IMO representatives.
      WIN seeks recusal of Ministers Edghill and Indar, livestreamed hearings and publication of the full report.
      The AFC proposes the Commission of Inquiry Act, Cap. 19:03. Jointly, five parties state that a Commission of
      Inquiry is not a substitute for a marine casualty investigation under SOLAS and the IMO Casualty
      Investigation Code, and that both should run. Most of those positions were stated before the members were
      named. On 30 July, the day of the swearing-in, the opposition welcomed the Commission while raising the
      lack of consultation on the selection of commissioners and the terms of reference, and potential conflicts
      of interest.</p>
    </div>
    <div class="card tr">
      <h3>Civil society</h3>
      <p>The GHRA rejects executive appointment and proposes a parliamentary commission with equal government and
      opposition membership, a judicially qualified chair, a statutory duty of candour and state-funded counsel for
      bereaved families. TIGI and Rescue Guyana call for an IMO-led investigation. The Amerindian Peoples
      Association calls for Minister Edghill&rsquo;s removal and a review of the whole river and sea transport
      system with mandatory consultation of Indigenous and riverain communities, and states on 30 July that it
      was not consulted on the terms of reference or the selection of commissioners. TIGI&rsquo;s president
      questioned the neutrality of several appointees on the day they were sworn. The Shipping Association of
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
        if is_social(r):
            badges += '<span class="badge social">Social media &mdash; unverified</span>'
        if is_expert(r):
            badges += '<span class="badge expert">Submitted analysis</span>'
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
        <option value="charges">Charges and inquiry (27–30 July)</option>
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

    # A document held on this site (an author's own submission) is linked
    # relatively and must be resolved from the source page's depth, not from
    # sources/. External URLs are left alone.
    _u = r['url'] or ''
    _internal = bool(_u) and not _u.startswith(('http://', 'https://', 'mailto:'))
    _href = ('../' + _u.lstrip('/')) if _internal else _u
    if not _u:
        orig = '<p class="tiny">No public URL recorded for this source.</p>'
    elif _internal:
        orig = (f'<a class="origin" href="{esc(_href)}">'
                f'Read the full document, held on this site &darr;</a>')
    else:
        orig = (f'<a class="origin" href="{esc(_href)}" rel="nofollow noopener" target="_blank">'
                f'Read the original at {E(r["outlet"])} &nearr;</a>')

    extra = ''
    if r['position']:
        extra += f'<h3>Official statement recorded in this source</h3><blockquote>{E(r["position"])}</blockquote>'
    if r['argument']:
        extra += f'<h3>The author&rsquo;s argument, as stated</h3><p>{E(r["argument"])}</p>'
    if r['figures']:
        extra += f'<h3>Figures cited in this source</h3><p>{E(r["figures"])}</p>'

    desc = (r['summary'] or r['title'])[:180]
    return head(f'{r["title"]} — {r["outlet"]} | MV Barima archive', desc, 'sources.html', depth=1,
                path=f'sources/{r["slug"]}.html') + f'''
<p class="crumb"><a href="../sources.html">&larr; All {len(records)} documents</a></p>
<article>
  <div class="badgerow" style="margin-bottom:12px;">
    <span class="badge">{E(r['kind'])}</span>
    {f'<span class="badge">{E((r["genre"] or "").replace("-", " "))}</span>' if r['genre'] else ''}
    <span class="badge">{E(prettydate(r['published']))}</span>
    {'<span class="badge social">Social media &mdash; unverified</span>' if is_social(r) else ''}
    {'<span class="badge expert">Submitted analysis</span>' if is_expert(r) else ''}
  </div>
  <h1 style="font-size:clamp(25px,3.4vw,38px)">{E(r['title'])}</h1>
  <p class="lede muted" style="margin-bottom:18px;">{E(r['outlet'])}{f' &middot; {E(r["author"])}' if r['author'] else ''}</p>
  {orig}
  {warn}
  {f'<div class="socialwarn"><strong>This is a social media post.</strong> {SOCIAL_NOTE}</div>' if is_social(r) else ''}
  {f'<div class="expertwarn"><strong>This is a submitted analysis, not a record.</strong> {EXPERT_NOTE}</div>' if is_expert(r) else ''}
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
  <desc id="qa3d">Of 179 people aboard, 77 were taken from the water and 76 survived, 73 bodies
  have been recovered by this archive&rsquo;s reckoning &mdash; the official releases of 30 July say 72 &mdash; and about 30
  remain unaccounted for. The resulting figure of about 103 recovered and unaccounted has never
  been published together as a death toll. The complement of 179 is itself a CCTV-derived
  estimate, so the residual is approximate.</desc>

  <text x="0" y="10" font-size="9.5" font-weight="680" fill="var(--ink)">179 aboard, established by CCTV review</text>

  <rect class="mark" x="0" y="18" width="177" height="22" rx="4" fill="var(--s1)"
        data-label="Survived" data-value="76" data-unit="people" data-var="--s1"
        data-note="77 were taken from the water; one died, so 76 survived"/>
  <rect class="mark" x="179" y="18" width="170" height="22" rx="4" fill="var(--s2)"
        data-label="Bodies recovered" data-value="73" data-unit="people" data-var="--s2"
        data-note="Official 24 to 29 July; the 30 July release says 72, unexplained"/>
  <rect class="mark" x="351" y="18" width="70" height="22" rx="4" fill="var(--s3)"
        data-label="Unaccounted for" data-value="about 30" data-unit="people" data-var="--s3"
        data-note="Never described by the state as dead"/>
  <text x="0" y="56" font-size="12" font-weight="700" fill="var(--ink)">76</text>
  <text x="24" y="56" font-size="9" fill="var(--ink2)">survived</text>
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
  <div class="lg"><span class="lgk" style="background:var(--s1)"></span>Survived (76)</div>
  <div class="lg"><span class="lgk" style="background:var(--s2)"></span>Bodies recovered (73)</div>
  <div class="lg"><span class="lgk" style="background:var(--s3)"></span>Unaccounted for (about 30)</div>
</div>
<details class="tableview"><summary>Table view</summary>
<div class="scrollx"><table>
<caption>Complement of the MV Barima, as officially stated</caption>
<tr><th>Measure</th><th class="n">People</th><th>Basis</th></tr>
<tr><td>Aboard</td><td class="n">179</td><td>Boarding-area CCTV review; the manifest recorded 133</td></tr>
<tr><td>Survived</td><td class="n">76</td><td>77 taken from the water; one died, so 76 survived</td></tr>
<tr><td>Bodies recovered</td><td class="n">73</td><td>Official from 24 to 29 July; the 30 July release says 72, with no explanation</td></tr>
<tr><td>Unaccounted for</td><td class="n">about 30</td><td>The Prime Minister's phrasing; never described as dead</td></tr>
<tr><td>Recovered plus unaccounted</td><td class="n">about 103</td><td>Never published as a figure by any government source</td></tr>
</table></div>
</details>
'''

# Scale: day 0 at x=52, one day = 30px, so day 12 sits at x=412 and the arrow
# and labels to its right stay inside the 480 frame.
CHART_INQUIRY = '''
<div class="chart bars">
<svg viewBox="0 0 480 172" role="img" aria-labelledby="qa4t qa4d">
  <title id="qa4t">Days from the sinking to each step toward an investigation</title>
  <desc id="qa4d">After the Estonia sank, three states established a joint investigation commission the
  next day. After the MV Barima sank, an inquiry was committed to on day four, announced on day
  seven and its members named on day eight; criminal charges were laid on day ten; the commissioners
  were sworn in on day twelve, at a ceremony closed to the press. The establishing instrument had
  still not been gazetted at the end of the period this archive covers.</desc>

  <line x1="52" y1="30" x2="412" y2="30" stroke="var(--grid)" stroke-width="1"/>
  <text x="52" y="14" font-size="8.5" fill="var(--muted)">day 0</text>
  <text x="172" y="14" font-size="8.5" fill="var(--muted)">day 4</text>
  <text x="292" y="14" font-size="8.5" fill="var(--muted)">day 8</text>
  <text x="412" y="14" font-size="8.5" fill="var(--muted)">day 12</text>
  <line x1="52" y1="20" x2="52" y2="26" stroke="var(--border)" stroke-width="1"/>
  <line x1="172" y1="20" x2="172" y2="26" stroke="var(--border)" stroke-width="1"/>
  <line x1="292" y1="20" x2="292" y2="26" stroke="var(--border)" stroke-width="1"/>
  <line x1="412" y1="20" x2="412" y2="26" stroke="var(--border)" stroke-width="1"/>

  <text x="0" y="52" font-size="9.5" font-weight="680" fill="var(--ink)">MV Barima, 2026</text>
  <line x1="52" y1="66" x2="412" y2="66" stroke="var(--s1l)" stroke-width="3"/>
  <circle class="mark" cx="52" cy="66" r="6" fill="var(--ink2)"
          data-label="Day 0, 18 July" data-value="0" data-unit="the vessel sinks" data-var="--ink2"/>
  <circle class="mark" cx="172" cy="66" r="6" fill="var(--s1)"
          data-label="Day 4, 22 July" data-value="4" data-unit="days" data-var="--s1"
          data-note="Prime Minister commits to an inquiry, no timeline given"/>
  <circle class="mark" cx="262" cy="66" r="6" fill="var(--s1)"
          data-label="Day 7, 25 July" data-value="7" data-unit="days" data-var="--s1"
          data-note="President announces the Commission"/>
  <circle class="mark" cx="292" cy="66" r="6" fill="var(--s1)"
          data-label="Day 8, 26 July" data-value="8" data-unit="days" data-var="--s1"
          data-note="Five commissioners named"/>
  <circle class="mark" cx="352" cy="66" r="6" fill="var(--s2)"
          data-label="Day 10, 28 July" data-value="10" data-unit="days" data-var="--s2"
          data-note="Three operator employees charged, before the inquiry is constituted"/>
  <circle class="mark" cx="412" cy="66" r="6" fill="var(--s1)"
          data-label="Day 12, 30 July" data-value="12" data-unit="days" data-var="--s1"
          data-note="Commissioners sworn in at State House; the press was not invited"/>
  <text x="52" y="86" font-size="8.5" fill="var(--ink2)">sinks</text>
  <text x="158" y="86" font-size="8.5" fill="var(--ink2)">committed to</text>
  <text x="242" y="86" font-size="8.5" fill="var(--ink2)">announced</text>
  <text x="268" y="98" font-size="8.5" fill="var(--ink2)">members named</text>
  <text x="352" y="112" font-size="8.5" font-weight="640" fill="var(--s2)" text-anchor="middle">charges</text>
  <text x="412" y="86" font-size="8.5" font-weight="640" fill="var(--ink)" text-anchor="end">sworn in</text>
  <text x="412" y="128" font-size="8.5" font-weight="640" fill="var(--muted)" text-anchor="end">still not gazetted</text>

  <text x="0" y="146" font-size="9.5" font-weight="680" fill="var(--ink)">MV Estonia, 1994</text>
  <circle class="mark" cx="52" cy="160" r="6" fill="var(--ink2)"
          data-label="Day 0, 28 September 1994" data-value="0" data-unit="the vessel sinks" data-var="--ink2"/>
  <circle class="mark" cx="82" cy="160" r="6" fill="var(--s3)"
          data-label="Day 1, 29 September 1994" data-value="1" data-unit="day" data-var="--s3"
          data-note="Estonia, Finland and Sweden establish a joint investigation commission"/>
  <line x1="52" y1="160" x2="82" y2="160" stroke="var(--s3)" stroke-width="3"/>
  <text x="94" y="164" font-size="8.5" fill="var(--ink2)">joint commission of three states established the next day</text>
</svg>
</div>
<div class="legend">
  <div class="lg"><span class="lgk" style="background:var(--s1)"></span>Steps toward the inquiry</div>
  <div class="lg"><span class="lgk" style="background:var(--s2)"></span>Criminal charges</div>
  <div class="lg"><span class="lgk" style="background:var(--s3)"></span>Estonia comparison</div>
</div>
<details class="tableview"><summary>Table view</summary>
<div class="scrollx"><table>
<caption>Days from the sinking to each step</caption>
<tr><th>Day</th><th>Date</th><th>Step</th></tr>
<tr><td class="n">0</td><td>18 July</td><td>The MV Barima sinks</td></tr>
<tr><td class="n">4</td><td>22 July</td><td>Prime Minister commits to a Commission of Inquiry; declines to give a timeline</td></tr>
<tr><td class="n">7</td><td>25 July</td><td>President announces an independent international Commission</td></tr>
<tr><td class="n">8</td><td>26 July</td><td>Five commissioners named; instruments &quot;being formalised&quot;</td></tr>
<tr><td class="n">10</td><td>28 July</td><td>Three operator employees charged with murder; the Commission is not yet constituted</td></tr>
<tr><td class="n">12</td><td>30 July</td><td>Commissioners sworn in at State House before the Chief Magistrate; the press was not invited. DPI names the enabling statute for the first time: Commissions of Inquiry Act, Cap. 19:03, s. 2(1)</td></tr>
<tr><td>&mdash;</td><td>&mdash;</td><td>No gazetted instrument, secretary, reporting deadline, budget, rules of procedure or call for submissions appears in this archive</td></tr>
<tr><td class="n">1</td><td>29 Sept 1994</td><td><em>Separate case, for comparison:</em> Estonia, Finland and Sweden establish a joint commission the day after the MV Estonia sinks</td></tr>
</table></div>
</details>
'''

QUESTION_CHARTS = {
    'CHART_ACTIONS': CHART_ACTIONS,
    'CHART_LOAD':    CHART_LOAD,
    'CHART_TOLL':    CHART_TOLL,
    'CHART_INQUIRY': CHART_INQUIRY,
}


def inject_altstrip(body):
    """{{ALTSTRIP}} renders the alternate fortnight strip."""
    return body.replace('<p>{{ALTSTRIP}}</p>', alt_developments()).replace('{{ALTSTRIP}}', alt_developments())


def inject_charts(body):
    """Swap each {{CHART_X}} token for its figure. Markdown wraps a lone token
    in a paragraph, so strip that wrapper rather than nesting a figure inside a
    <p>. Fails loudly: an unreplaced token would still be visible on the page,
    and the build asserts none survive."""
    for key, svg in QUESTION_CHARTS.items():
        body = body.replace('<p>{{%s}}</p>' % key, svg).replace('{{%s}}' % key, svg)
    left = [t for t in re.findall(r'\{\{[A-Z_]+\}\}', body) if t not in ('{{MORE}}', '{{VIEW}}', '{{GIST}}')]
    if left:
        raise SystemExit('unreplaced chart tokens: %s' % left)
    return body


def sources_block(keys):
    """Render a citation list from archive slugs. Fails the build on an unknown
    slug, so a citation can never silently point at nothing, and pulls the
    outlet, date and title from the record itself so they cannot drift."""
    rows = []
    for k in keys:
        r = by_slug.get(k)
        if r is None:
            raise SystemExit('unknown citation slug: %s' % k)
        when = prettydate(r['published']) if r.get('published') and r['published'] != '0000-00-00' else 'undated'
        rows.append(
            '<li><a href="sources/{slug}.html">{title}</a>'
            '<span class="ctmeta">{outlet} &middot; {when}</span></li>'.format(
                slug=r['slug'], title=E(r['title']), outlet=E(r['outlet']), when=when))
    return ('<details class="cites"><summary>Sources for this answer '
            '<span class="ctn">{n}</span></summary><ul class="ctlist">{rows}</ul>'
            '<p class="tiny muted">Each links to this archive&rsquo;s page for that document, '
            'which carries the publisher, the date and a link to the original.</p></details>').format(
                n=len(keys), rows=''.join(rows))


def inject_gist(body):
    """{{GIST}} ... {{/GIST}} renders the one-paragraph distillation of an
    answer's reasoned view, shown with the short answer so a reader gets the
    archive's conclusion without opening the working. Same marker discipline as
    the reasoned block: strip any paragraph wrapper first."""
    def one(m):
        return ('<div class="gist"><p class="glabel">The reasoned view, in short</p>'
                '<div class="gbody">{inner}</div></div>').format(inner=m.group(1))
    body = re.sub(r'<p>\s*\{\{GIST\}\}\s*</p>', '{{GIST}}', body)
    body = re.sub(r'<p>\s*\{\{/GIST\}\}\s*</p>', '{{/GIST}}', body)
    body = re.sub(r'<p>\s*\{\{GIST\}\}\s*', '{{GIST}}<p>', body)
    body = re.sub(r'\s*\{\{/GIST\}\}\s*</p>', '</p>{{/GIST}}', body)
    body = re.sub(r'\{\{GIST\}\}(.*?)\{\{/GIST\}\}', one, body, flags=re.S)
    if '{{GIST}}' in body or '{{/GIST}}' in body:
        raise SystemExit('unbalanced GIST markers')
    return body


def inject_reasoned(body):
    """Turn a {{VIEW}} ... {{/VIEW}} pair into a labelled block. This is the one
    place on the site where the archive reasons past what a document states, so
    it is fenced off visually and carries its own standing caveat rather than
    blending into the evidence above it."""
    def one(m):
        return ('<aside class="reasoned" aria-label="The reasoned view">'
                '<p class="rlabel">The reasoned view</p>'
                '<div class="rbody">{inner}</div>'
                '<p class="rnote">This block is reasoning, not record. It goes past what any single '
                'document states, and it can be wrong where the documents cannot. Everything above it '
                'is evidence; everything in it is inference from that evidence, and the record pages '
                'remain authoritative.</p></aside>').format(inner=m.group(1))
    # Markdown may leave the marker inside a paragraph of its own or glued to
    # the following one, so strip any wrapper before substituting. Otherwise the
    # <aside> lands inside a <p> and the browser silently unwraps it.
    body = re.sub(r'<p>\s*\{\{VIEW\}\}\s*</p>', '{{VIEW}}', body)
    body = re.sub(r'<p>\s*\{\{/VIEW\}\}\s*</p>', '{{/VIEW}}', body)
    body = re.sub(r'<p>\s*\{\{VIEW\}\}\s*', '{{VIEW}}<p>', body)
    body = re.sub(r'\s*\{\{/VIEW\}\}\s*</p>', '</p>{{/VIEW}}', body)
    body = re.sub(r'\{\{VIEW\}\}(.*?)\{\{/VIEW\}\}', one, body, flags=re.S)
    if '{{VIEW}}' in body or '{{/VIEW}}' in body:
        raise SystemExit('unbalanced VIEW markers')
    return body


def inject_sources(body):
    """Expand {{SOURCES: slug | slug | ... }} markers."""
    def one(m):
        keys = [k.strip() for k in m.group(1).split('|') if k.strip()]
        return sources_block(keys)
    body = re.sub(r'<p>\{\{SOURCES:(.*?)\}\}</p>', one, body, flags=re.S)
    body = re.sub(r'\{\{SOURCES:(.*?)\}\}', one, body, flags=re.S)
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
        # A {{MORE}} marker splits the answer: everything above it is the short
        # answer and shows as soon as the question is opened; everything below
        # goes behind a second disclosure, so a reader gets the answer first and
        # the working only if they want it.
        parts2 = re.split(r'<p>\{\{MORE\}\}</p>|\{\{MORE\}\}', answer, maxsplit=1)
        if len(parts2) == 2:
            short, rest = parts2
            answer = (
                '<div class="qshort">{s}</div>'
                '<details class="qmore"><summary>Keep reading</summary>'
                '<div class="qmorebody">{r}</div></details>').format(s=short, r=rest)
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
        '<span class="tiny muted qahint">{n} questions &middot; click a question for the short answer</span>'
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

# ------------------------------------------------------------------ og cards --
# One card per top-level page plus a shared one for the source pages. Titles
# and subtext are written for the crop: a social preview is read at a glance and
# at a fraction of full size, so each card says what the page is and one true
# thing about it, and nothing that needs squinting at.
OG_CARDS = [
    ('index',     'Guyana &middot; 18 July 2026',
     'MV Barima: the documented record',
     '179 aboard. 73 recovered. About 30 unaccounted for. What {n} published documents record about '
     'the sinking of 18 July 2026 — attributed, dated, and checkable.'),
    ('timeline',  'Chronology, 1936&ndash;2026',
     'Chronology',
     'From the Clyde shipyard that built her in 1939 to the inquiry sworn in twelve days after she sank. '
     'Every entry attributed; where sources conflict, both versions are given.'),
    ('facts',     'The figures, source by source',
     'The figures, source by source',
     'The complement, the recovery figures and the vessel’s stated capacity all moved. Who stated '
     'each figure, when, and on what basis — including the ones with no document behind them.'),
    ('positions', 'Positions and proposals',
     'What each party has said',
     'Government, opposition, civil society and named commentators — attributed and dated, with no '
     'assessment by this archive of who is right.'),
    ('anomalies', 'Frontier AI analysis &middot; Claude Opus 5',
     'What doesn&rsquo;t add up',
     'Twenty-eight things in this record that do not reconcile - figures that moved without '
     'explanation, documents that should exist and have not appeared, official accounts '
     'contradicted by other official accounts.'),
    ('questions', 'Answered by AI over the whole archive',
     'Questions of the record',
     'Who is accountable. Whether the boat was overloaded. How many actually died. Plain answers '
     'from {n} documents, with the reasoning shown and the limits stated.'),
    ('sources',   '{n} documents, browsable',
     'Every document in the archive',
     'Filter {n} published documents by outlet, kind and period. Each one carries its publisher, '
     'date, key claims and a link to the original.'),
    ('about',     'Method, gaps and corrections',
     'How this was built, and what is missing',
     'How the corpus was assembled, what could not be retrieved, what this archive got wrong, and '
     'the documents that would settle the questions it cannot.'),
    ('counterfactual', 'Counterfactual analysis &middot; not the record',
     'The road not taken',
     'Imagine the Government had an AI advisor from the night the Barima went down. What it would have '
     'said to do \u2014 day by day, then month by month to the end.'),
    ('changelog', 'Every revision, logged',
     'Revisions',
     'Every change to this site since it was first built, newest first — including the claims this '
     'archive published and later had to withdraw.'),
    ('ask',       'Open to anyone',
     'Ask a question',
     'Send a question about the disaster and it will be answered from the documents this archive '
     'holds. If the record cannot answer it, that is published too.'),
    ('source',    'One document in the archive',
     'A document in the record',
     'A research summary of one published document — its publisher, date, key claims and a link to '
     'the original. The full text is not republished.'),
]

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_og
_cards = [(slug, k.format(n=len(records)), t, d.format(n=len(records)))
          for slug, k, t, d in OG_CARDS]
print('og cards:', len(make_og.build(_cards, len(records), BUILT.split(',')[0])))

# ---------------------------------------------------------------------- build
os.makedirs(OUT, exist_ok=True)
write('index.html', build_index())
write('sources.html', build_sources())
write('ask.html', build_ask())
for r in records:
    write(f'sources/{r["slug"]}.html', build_source_page(r))

DEV_NOTE = ('<div class="card" style="margin-top:26px">'
            '<p class="eyebrow" style="margin-top:0">The story in twenty-four turns</p>'
            '<h2 style="margin-top:2px;margin-bottom:6px">Notable developments</h2>'
            '<p class="small muted" style="margin-bottom:16px">A reader arriving cold should be able to '
            'follow the arc before reading the record underneath. Each entry is a moment after which '
            'something was different; the full chronology, with every dated entry the corpus supports and '
            'every conflict marked, follows below.</p>'
            + developments(compact=False) +
            '<div class="devkey">'
            '<span><i style="background:var(--muted)"></i>Before the sinking</span>'
            '<span><i style="background:var(--ink)"></i>The sinking</span>'
            '<span><i style="background:var(--s1)"></i>The response</span>'
            '<span><i style="background:var(--s2)"></i>The charges</span>'
            '<span><i style="background:var(--s3)"></i>The inquiry</span>'
            '</div></div>')

write('timeline.html', build_prose_page(
    'timeline.md',
    'Chronology, 1936–2026 — MV Barima documented record',
    'Chronology',
    'From the Clyde shipyard that built her in 1939 to the thirteen days after she sank. Every entry is attributed '
    'to the source that reports it; where sources conflict, both versions are given and marked.',
    'timeline.html', extra_note=DEV_NOTE))

write('facts.html', build_prose_page(
    'facts.md',
    'The figures, source by source — MV Barima documented record',
    'The figures, source by source',
    'The complement, the recovery figures and the vessel’s stated capacity all changed over the thirteen days. This '
    'page records each figure, who stated it, when, on what stated basis, and what in the record differs from it.',
    'facts.html',
    '<div class="note warn"><h4>Read this before citing any number</h4><p>Including numbers from this site. Early '
    'disaster figures are revised, and these were revised repeatedly during the period covered. Several figures '
    'here have no published document behind them.</p></div>'))

write('anomalies.html', build_prose_page(
    'anomalies.md',
    'What doesn\u2019t add up \u2014 MV Barima documented record',
    'What doesn\u2019t add up',
    f'A frontier AI analysis by Claude Opus 5, reasoning across all {len(records)} documents. Twenty-eight '
    'things in this record that do not reconcile: figures that moved without explanation, documents that '
    'should exist and have not appeared, official accounts contradicted by other official accounts.',
    'anomalies.html',
    transform=inject_sources,
    extra_note='<div class="note warn"><h4>This is a frontier AI analysis, not the record</h4>'
    '<p><strong>Every finding on this page was produced by Claude Opus 5, Anthropic&rsquo;s frontier model, '
    f'reasoning across all {len(records)} documents in this archive.</strong> No human investigator assembled it. It goes '
    'further than any single document states, and that is what it is for &mdash; but it is inference, and '
    'inference can be wrong where a document cannot. Every finding names the documents behind it so you can '
    'check the reasoning yourself.</p>'
    '<p>It accuses no one of a crime. Three men have been charged with murder and have not been tried, and '
    'nothing here bears on their guilt or innocence. Where a benign explanation accounts for something, this '
    'page says so and drops it. The record pages remain authoritative over everything on it.</p></div>'))

write('counterfactual.html', build_prose_page(
    'counterfactual.md',
    'The road not taken \u2014 MV Barima documented record',
    'The road not taken',
    'Imagine the Government had an AI advisor from the night the Barima went down. One job: keep the '
    'people\u2019s trust. This is what it would have said to do \u2014 day by day through the first '
    'fortnight, then month by month to the end.',
    'counterfactual.html',
    transform=lambda b: inject_altstrip(inject_sources(b)),
    extra_note='<div class="note warn"><h4>None of this happened</h4>'
    '<p>Every other page on this site records what happened. <strong>This one does not.</strong> The first '
    'fortnight is set against the real record and cited; <strong>everything after 1 August 2026 is invented '
    'outright</strong>, and the page marks where that starts. It never says what the inquiry would have '
    '<em>found</em>, because nobody can know that.</p>'
    '<p>Kevin Price, Rondell Roberts and Delon Granderson have been charged with murder and have not been '
    'tried. <strong>Nothing here suggests what they did or did not do, and no part of it says what should '
    'happen to them.</strong></p></div>'))

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
    f'Questions about the MV Barima disaster, answered from the {len(records)} documents in this archive. '
    'Anyone can send a question in.',
    'questions.html',
    '<div class="note warn"><h4>These answers are written by AI, over the whole archive</h4><p>'
    'Everywhere else this site only sets out what published sources said, attributed. Here the '
    f'question is answered directly, by AI reasoning across all {len(records)} documents. Evidence is named; '
    'where the record cannot settle something, that is the answer given. If this page and the '
    'record pages disagree, the record pages are right. Question two also draws on international '
    'instruments held outside the archive, and says so. Nothing here bears on the guilt of the '
    'three men charged on 28 July, who have not been tried. The research and the reasoning are done '
    'with Claude Opus 5, Anthropic&rsquo;s frontier model, over the corpus described on the '
    '<a href="about.html">method page</a>.</p></div>',
    transform=lambda b: collapsible_qa(inject_sources(inject_reasoned(inject_gist(inject_charts(b)))))))

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
