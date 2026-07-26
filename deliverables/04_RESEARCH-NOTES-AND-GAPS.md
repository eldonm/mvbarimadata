# Research Notes, Method and Known Gaps

Compiled 26 July 2026. Read this before relying on the corpus for anything consequential.

---

## Method

Five parallel research streams were run against the open web, plus a sixth gap-recovery pass: Guyanese domestic press; official and state sources; international wires and regional press; vessel and institutional history; aftermath, accountability and public debate; and finally the Commission of Inquiry cluster and press-capacity context. Each source was retrieved individually and written to `archive/` as a markdown file with metadata frontmatter recording outlet, author, publication date, URL, retrieval date, tier, stream, genre, casualty figures cited, and extracted key claims.

The corpus was then deduplicated by canonical URL, keeping the fullest capture in each case. Ten superseded duplicates were moved to `_superseded/` rather than deleted, so nothing is lost. Two files had been misfiled as official primary sources when they were in fact press reports of official statements; the correctly attributed versions were kept.

**Standing rule applied throughout:** no file was written containing invented, reconstructed or paraphrased-as-verbatim text. Where retrieval failed, the failure is recorded here rather than papered over. Where the retrieval tool returned condensed prose despite instructions, the file carries a `capture_fidelity` warning — in those files direct quotations are reliable and connective prose is the tool's compression, not the outlet's wording. Do not quote a flagged file as verbatim.

**Corpus:** 152 sources, 128 dated 19–26 July 2026, 24 pre-disaster context sources reaching back to the 1930s builder's record.

---

## Retrieval failures — what could not be captured

**Guyana Chronicle: the entire outlet.** Every attempt, across bare, `www.` and `/amp/` variants and multiple researchers, hit a JavaScript redirect wall. This is a significant hole: the Chronicle is state-owned, so the corpus is missing roughly ten known articles from the government's own newspaper, including "Management team responsible for loading, dispatch of MV Barima suspended as probe intensifies," "Gov't orders immediate investigation," "Surviving the unthinkable," the search-area expansion piece, and the Guyana Human Rights Association report. No Chronicle content is present in the archive in any form; the only trace of the outlet is a publisher's disclaimer inside a Democracy Guyana column. **This is the largest single gap and the highest priority for recovery**, most plausibly through a browser session rather than a fetch tool.

**Village Voice News: robots-disallowed.** Respected, not circumvented. The outlet is therefore wholly unrepresented, and one known piece is substantively relevant: "Edghill's swift suspensions of MV Barima workers raise more questions than answers."

**Paywalls and 403s.** CNN (both `cnn.com` and `edition.cnn.com`), CBC's `ferry-sinks-guyana` piece, four Washington Post AP-syndications (three recovered via WRAL and Citrus County Chronicle instead), France 24, Telesur in both languages, El Universal (Venezuela), and Stabroek's own 15 March liquidator follow-up.

**No BBC byline surfaced** through any query formulation, and no Reuters-bylined article was captured directly — though Reuters copy is present in the corpus indirectly, since Al Jazeera's 21 July report is bylined "Al Jazeera Staff, AP and Reuters." Given both wires' usual coverage of a disaster of this scale, treat this as an unresolved question about search reach rather than a confirmed absence of coverage.

**Two Kaieteur pages** served submission stubs rather than article bodies: "MV Barima tragedy exposes Guyana's deep governance failures" (Tevin Skeete) and one other letter. The important Kaieteur piece, "Major discrepancies found on MV Barima manifest," failed two subagent attempts, which returned only condensed output, and was then recovered verbatim by the lead researcher — it is now the single most valuable news document in the archive.

**Ship registries** were largely unreachable: VesselFinder and Clyde-built Ships are robots-disallowed, MarineTraffic returned 403. Vessel provenance therefore rests on the Paxman History Pages engine register, which is fortunately the best available source anyway.

---

## Substantive gaps — documents that do not appear to exist publicly

These matter more than the retrieval failures, because their absence is itself a finding.

**No certificate.** Nothing in the corpus — not one government release, not one ministerial statement — names a class certificate, a passenger safety certificate, or a load-line survey date for the *MV Barima*. Seaworthiness is asserted entirely on a docking chronology. The certified capacity that underwrites MARAD's "not overloaded" finding has never been published, and MARAD's Director-General cannot say when or why it rose from the 1938 rating of 150 passengers to 394.

**No terms of reference.** As of 26 July the Commission of Inquiry exists only as a presidential announcement. No commissioners named, no chair, no secretary, no gazetted instrument, no statutory basis cited by the President, no reporting deadline, no call for submissions. The only statutory citation anywhere in the corpus is the AFC's proposal to use the Commission of Inquiry Act, Cap. 19:03.

**No official death toll.** The state publishes bodies recovered, never persons missing. The residual has never appeared in a government document.

**No Auditor General finding specific to the T&HD** was located, despite targeted searching, and no trade union statement of any kind — notable given that the suspended and detained are wharf and marine workers.

**No GDF, MARAD, Police Force, Office of the President or Ministry of Public Works web publication** on the disaster. MARAD issued no advisory, no notice to mariners and no certification statement. `parliament.gov.gy` press releases stop at April 2026, its motions index returned empty, and no Hansard exists for the July sitting. The state's entire published output on the disaster runs through DPI — seventeen releases dated 19–25 July, with a further five pre-disaster DPI items in the corpus — and through ministers' Facebook posts. **A suspension of officials and a declaration of national mourning were both communicated primarily by social media.**

**No IMO and no PAHO statement.** CARICOM and UNDP Guyana issued statements; the maritime safety body with actual jurisdictional competence has said nothing.

---

## Structural finding that shaped the corpus

Stabroek News, Guyana's principal independent daily for roughly forty years, ceased print publication on 15 March 2026 in voluntary liquidation — four months before the disaster. The consequence for this research was immediate and concrete: repeated searches for Stabroek coverage of the sinking returned nothing, and the archive's two most technically substantial pre-disaster warnings, Capt. R. E. W. Adams's 2015 letter naming this vessel and the 2012 piece on the Sprostons-built fleet, both come from Stabroek's letters and features pages — the forum that no longer exists.

Independent print scrutiny in Guyana is now effectively Kaieteur News alone, which is why the corpus skews heavily to that outlet (32 of 152 sources) and why civil-society bodies such as the GHRA, TIGI and the APA are issuing statements directly rather than arguing in a newspaper's letter columns. Any reader of this archive should hold that distortion in mind: it is a property of the Guyanese media environment in July 2026, not of the research design.

---

## Priority follow-ups

Recovering the Guyana Chronicle's disaster coverage, most likely via a browser session, would close the state-newspaper hole. Beyond that, the highest-value targets are documentary rather than journalistic: the March 2026 tender documents that reportedly show engineers flagging deteriorated hull sections before the sinking; any survey, load-line or capacity certificate for the vessel; the Commission of Inquiry's terms of reference once gazetted, with attention to whether they reach loading *authorisation* and procurement or stop at loading *execution*; the Auditor General's reports on the T&HD; and the 19 September 2015 Kaieteur inspection report cited by Adams, which was searched for and not found.

On the live story, the variables worth monitoring are whether the wreck is righted and what that does to the count, whether the residual of roughly thirty missing is ever officially named, whether charges are laid and against whom, whether Parliament sits before the Commission is constituted, and whether any pre-18-July document surfaces bearing a named official's knowledge of the hull's condition.

---

## The verification pass

After the deliverables were drafted, a separate adversarial pass re-checked every name, figure, date, quotation and claim-of-absence against the archive, with instructions to falsify rather than confirm. It found eighteen substantive errors, all now corrected. They are recorded here because the pattern is instructive for anyone extending this work.

The most common failure was **quotation drift** — a paraphrase hardening into quotation marks across drafts. "MV Barima was seaworthy" is DPI's headline, not Edghill's words; his actual formulation was the much narrower "there was no report of any kind that suggested the vessel was unseaworthy." "Frequent mechanical failures" was being quoted from a tool-condensed file whose own note warned that only one unrelated sentence in it was verbatim. "Not compensation" was a truncation of a Prime Ministerial statement about *sequencing* into an apparent legal characterisation the state never made.

The second pattern was **attribution slippage**. Saiku Andrews, an opposition MP voicing a claim, had become a Jamaica Observer byline. Deon La Cruz, an opposition MP, had become a reporter. Toxicology disclosure had migrated from Edghill to Jagdeo. A Bulkan letter's headline had become "Kaieteur's framing." A letter-writer's argument had become a newspaper's editorial position. In each case the substance was right and the source was wrong, which is the more dangerous kind of error because it survives casual checking.

Third, **figures merging**. The vessel's capacity had been rendered as a single "284 tons / 394 passengers" when in fact Thomas said 394/126 tonnes, then 394/120 tonnes, and Edghill said 397/284 tons — three inconsistent official statements whose inconsistency is itself the finding. A search area "expanded to 32 square miles" was actually expanded *by* 32, on top of an earlier 400.

Fourth, **inference presented as record**: the *Ma Lisha* dated to 2021 rather than its actual 2023 commissioning; "sole vessel serving Region One" where the archive supports only "sole vessel on the Port Kaituma route"; the 2017 refit's "installation of two engines" hardening into a claim that the 1939 machinery was entirely replaced.

And one **claim of absence that was simply false**: the corpus does contain Reuters copy, indirectly.

Two things the pass surfaced that are now flagged in the analysis rather than fixed. The Prime Minister stated on 25 July that the state has **"no such record"** of a Mayday from the captain — which contradicts the 23:01 timing on which every published chronology, including this one, depends. And **Elena** Moonsammy (Guyanese press, lost seven children she travelled with, sole source for cargo at the stern) and **Helena** Moonsammy (AP and Gleaner, a grandmother who lost four grandchildren and spent nine hours in the water) may be two different people; earlier drafts merged them as one name with variant spellings, which the archive does not support.

## Directory structure

`archive/` holds the 152 full-text sources, one file per source, plus six `_manifest_*.jsonl` files carrying structured metadata and research annotations for every entry, and `_synthesis_vessel-dossier.md`, a fully cited dossier on the vessel and the T&HD fleet with an explicit unverified-and-contested section.

`deliverables/` holds `00_SOURCE-CATALOGUE.md` (the annotated listing of all 152 sources with summaries, chronological then contextual, plus a distribution table), `01_TIMELINE.md` (reconciled chronology from 1936 to 26 July 2026, with conflicts marked), `02_CONTESTED-FACTS.md` (figure-by-figure reconciliation, single-source claims, reliability guidance), `03_SYSTEMIC-ANALYSIS.md` (the four-pillar systemic brief), and this file.

`_superseded/` holds the ten deduplicated files, retained for audit.
