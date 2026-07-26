# MV Barima — public research site

A static, dependency-free website presenting what 152 published sources establish about the sinking of the
Guyanese ferry *MV Barima* on the night of Saturday 18 July 2026, with drill-down to every source.

Built 26 July 2026. **158 pages, no build step, no framework, no tracking, no cookies, no external requests.**

## Deploying

The site is plain HTML/CSS/JS with relative links. It works three ways with no changes:

- **Open it locally** — double-click `index.html`. Everything works offline, including search and the charts.
- **Any static host** — drag the folder to Netlify, or push to a `gh-pages` branch, or `aws s3 sync . s3://bucket`.
  No configuration, no redirects, no server-side anything.
- **A subdirectory** — all links are relative, so it can live at `example.com/barima/` without edits.

There is nothing to install and nothing to keep patched. That is deliberate: an archive that depends on a
build toolchain stops working the moment the toolchain does.

## Structure

```
index.html          Overview: headline figures, three interactive charts, the voyage hour by hour,
                    the vessel and institutional record, conditions recorded against proposals on the
                    record, and where each party stands on the inquiry
timeline.html       Full chronology 1936–2026, conflicts marked
facts.html          Every figure that changed: who stated it, when, on what stated basis
positions.html      Positions and proposals: what each named party has said, attributed
sources.html        Searchable, filterable index of all 152 sources
sources/*.html      152 individual source pages
about.html          Method, retrieval failures, substantive gaps, and the 18 corrections
assets/style.css    One stylesheet. Light is the default for every visitor; dark is opt-in only
assets/site.js      Theme toggle, chart hover layer, source filtering. ~250 lines, no dependencies
data/sources.json   The full research dataset as machine-readable JSON, for onward use
build_site.py       Regenerates every page from the private archive (see below)
```

## What is and is not published here

The private research corpus holds the **full verbatim text** of all 152 sources. This site deliberately does
**not** republish it. Each source page carries bibliographic detail, a research summary, extracted claims,
short attributed quotations, and a prominent link to the original — fair quotation for comment and review,
with the traffic sent to the publisher. Copyright in the underlying journalism belongs to the outlets that
did the work.

Also deliberately absent: any compiled list of the dead. Survivor and family testimony appears only as
already published and attributed. A roll of victims assembled from press reports is not this archive's to
publish.

## Editorial rule

Nothing on the site is asserted in the archive's own voice. Every statement is either a figure with its source, or
a position attributed to the party that stated it. The site advances no explanation of the cause and makes no
recommendation; where parties have proposed remedies, those are recorded as their proposals. Analytical framing
that was present in earlier drafts has been removed, including from the 152 per-source summaries.

Light mode is the published default and the operating-system preference is deliberately not followed, so every
visitor sees the same thing on a first visit. A reader can opt into dark mode with the toggle, and that choice
persists locally.

## Accessibility and rendering notes

Every chart has a table-view twin, so no value is reachable only by hovering. Charts carry `<title>`/`<desc>`
and per-mark `aria-label`s, and every hit target is keyboard-focusable with the same readout as hover. Colour
never carries meaning alone — legends are always present and marks are directly labelled. The palette was
validated for colour-vision deficiency separation in both light and dark modes; the one slot that falls below
3:1 contrast on the light surface is only ever used with a visible adjacent label. Layout reflows to a single
column below 900px. The site prints legibly.

## Regenerating

`build_site.py` reads the private archive (`archive/*.md` plus the `_manifest_*.jsonl` annotation files) and
the five markdown deliverables, and writes every page. To update after adding sources:

```bash
python3 build_site.py     # needs pyyaml and markdown
```

Paths are set at the top of the script. It asserts on slug collisions rather than silently overwriting, and
prints a summary — record count, outlet count, and how many sources are flagged as condensed captures — so a
bad run is visible immediately.

## Health warning

This was compiled eight days after the sinking, while the Commission of Inquiry was still unconstituted and
the figures were still moving. Every number here should be treated as provisional. Read `about.html` before
citing anything, and note that the arithmetic residual of roughly thirty missing people is *arithmetic* — it
is not an official figure, because no official figure exists.
