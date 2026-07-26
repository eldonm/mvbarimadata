# MV Barima — data dashboard

A static, dependency-free research site and infographic presenting what 152
published sources establish about the sinking of the Guyanese ferry *MV
Barima* on the night of Saturday 18 July 2026, compiled 26 July 2026.

**Browse the site:** open [`site/index.html`](site/index.html) directly in a
browser (no server, no build step), or serve the `site/` folder with any
static host.

## Contents

```
site/            The public website — 158 pages, source code and generated
                 output together. Start at site/index.html. See
                 site/README.md for structure, deployment, and
                 accessibility notes.
site_content/    The neutral, attributed markdown this site is built from
                 (chronology, figures, positions and proposals, method).
infographic/     One-page PDF/HTML infographic summarizing the record.
deliverables/    The underlying research documents: timeline, contested
                 facts, systemic analysis, research notes and gaps, and the
                 source catalogue.
archive/         Bibliographic metadata and neutral summaries for all 152
                 sources (_manifest_*.jsonl, _summaries_neutral.jsonl).
```

## What is and is not published here

This repository does **not** contain the full text of the 152 news articles
and press releases the research draws on. That corpus is kept privately;
only bibliographic detail, a research summary, and a link to each original
are published, on each source's page within the site — fair quotation for
comment and review, with the traffic sent to the publisher. Copyright in the
underlying journalism belongs to the outlets that did the work.

Also deliberately absent: any compiled list of the dead. Survivor and family
testimony appears only as already published and attributed.

## Editorial rule

Nothing here is asserted in this project's own voice. Every statement is
either a figure with its source, or a position attributed to the party that
stated it. The site advances no explanation of the cause and makes no
recommendation; where parties have proposed remedies, those are recorded as
their proposals, in [`site/positions.html`](site/positions.html). Light mode
is the site's default and does not follow OS preference, so every visitor
sees the same thing on a first visit.

## Health warning

This was compiled eight days after the sinking, while Guyana's Commission of
Inquiry was still unconstituted and the figures were still moving. Every
number here should be treated as provisional — see
[`site/about.html`](site/about.html) before citing anything.
