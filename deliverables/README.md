# MV Barima Tragedy — Research Archive

**Event:** The Transport & Harbours Department ferry *MV Barima* sailed from the T&HD wharf at Kingston, Georgetown at approximately 15:15 on Saturday 18 July 2026, bound for Port Kaituma in Guyana's North West District (Region One). She lost an engine roughly four hours out, took on water, and capsized off Iron Punt near the mouth of the Pomeroon River, some seven to ten nautical miles off the Essequibo Coast, after transmitting a Mayday at 23:01. Her manifest recorded 116 passengers and 17 crew. The complement was later reconstructed from boarding-area CCTV at 179. As of 26 July 2026, 73 bodies had been recovered, 69 identified, 76–77 people rescued, and roughly thirty remain unaccounted for. The state has never published a death toll.

**Archive compiled:** 26 July 2026 · **Corpus:** 152 full-text sources · **Status:** live event, unconstituted inquiry

---

## Where to start

If you want the **listing of sources and summaries**, open `deliverables/00_SOURCE-CATALOGUE.md`. Every one of the 152 archived sources is there with a summary, key facts, notable quotes and its local filename — Part 1 chronological through the disaster, Part 2 the historical and structural record, Part 3 a distribution table by outlet.

If you want the **story straight**, open `deliverables/01_TIMELINE.md`. It runs from the 1939 build through 26 July 2026, marks every conflict `[CONTESTED]`, and closes on the arithmetic the state has not stated.

If you are about to cite a number, read `deliverables/02_CONTESTED-FACTS.md` first. The passenger count, the death toll and the vessel's certified capacity are all unstable, and several consequential claims rest on a single source.

If you want the **analysis**, `deliverables/03_SYSTEMIC-ANALYSIS.md` is the four-pillar brief: the Substratum, the Narrative Landscape, the Agency Matrix, and a cone of plausibility with a resolution vector.

Before relying on any of it for anything consequential, read `deliverables/04_RESEARCH-NOTES-AND-GAPS.md`. It documents what could not be retrieved, what appears not to exist publicly, and the media-environment distortion baked into the corpus.

---

## The three things most worth knowing

**The manifest was not a flawed document; for about a day it was a fiction.** Only 35 of the first 67 survivors appeared on it. The state spent 19 July telling bereaved families it was working from the vessel's manifest. The eventual complement of 179 came from a security camera.

**Seaworthiness is asserted, never documented.** No certificate of survey, load line or passenger capacity appears anywhere in 152 sources. MARAD's Director-General cannot say when the vessel's rating rose from 150 passengers in 1938 to 394. The claim that she was overloaded and the claim that she was not are equally unfalsifiable for the same reason.

**Guyana lost its main independent newspaper four months before this happened.** Stabroek News ceased print on 15 March 2026 — the same forum that in 2015 published a master mariner naming this exact vessel as fit for scrapping.

---

## How the archive is organised

`archive/` — 152 full-text source files, one per source, named `YYYY-MM-DD_outlet-slug_headline-slug.md`, each with metadata frontmatter (outlet, author, publication date, URL, retrieval date, tier, stream, genre, figures cited, extracted key claims). Also six `_manifest_*.jsonl` files with structured annotations for every source, and `_synthesis_vessel-dossier.md`, a fully cited dossier on the vessel and fleet.

`deliverables/` — the five documents described above.

`_superseded/` — ten deduplicated files, retained for audit rather than deleted.

**One handling rule.** Files whose frontmatter carries a `capture_fidelity`, `fidelity` or `verbatim: false` warning were returned by the retrieval tool in condensed form. Their direct quotations are reliable; their connective prose is the tool's compression and is not the outlet's wording. Do not quote those files as verbatim. Everything else is full source text as published.
