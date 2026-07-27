# Research Notes, Method and Known Gaps

Compiled 26 July 2026. Read this before relying on the corpus for anything consequential.

---

## Method

Five parallel research streams were run against the open web, plus a sixth gap-recovery pass: Guyanese domestic press; official and state sources; international wires and regional press; vessel and institutional history; aftermath, accountability and public debate; and finally the Commission of Inquiry cluster and press-capacity context. Each source was retrieved individually and written to `archive/` as a markdown file with metadata frontmatter recording outlet, author, publication date, URL, retrieval date, tier, stream, genre, casualty figures cited, and extracted key claims.

The corpus was then deduplicated by canonical URL, keeping the fullest capture in each case. Ten superseded duplicates were moved to `_superseded/` rather than deleted, so nothing is lost. Two files had been misfiled as official primary sources when they were in fact press reports of official statements; the correctly attributed versions were kept.

**Standing rule applied throughout:** no file was written containing invented, reconstructed or paraphrased-as-verbatim text. Where retrieval failed, the failure is recorded here rather than papered over. Where the retrieval tool returned condensed prose despite instructions, the file carries a `capture_fidelity` warning — in those files direct quotations are reliable and connective prose is the tool's compression, not the outlet's wording. Do not quote a flagged file as verbatim.

**Corpus:** 200 sources — 152 in the first build, plus 40 Guyana Chronicle articles and six international sources added on 26–27 July. 174 are dated 19–26 July 2026; 24 are pre-disaster context sources reaching back to the 1930s builder's record.

---

## Retrieval failures — what could not be captured

**Guyana Chronicle: closed on 26 July.** In the first build this was the largest single gap in the corpus. Every fetch attempt, across bare, `www.` and `/amp/` variants, hit a JavaScript redirect wall, and the state-owned Chronicle was absent from the archive entirely. It has since been retrieved through a browser session: 40 articles dated 22–26 July, of which 38 carry full text. Two are flagged `thin-capture` and marked as incomplete on their source pages. The change is logged on the [revisions page](changelog.html).

**Kiskadee Watch: retrieved 27 July.** The BBC credits this independent Guyanese outlet as the origin of Elena Moonsammy's account. Two of its reports are now in the corpus, and they carry survivor testimony on the vessel's machinery that is not present elsewhere. **Ignite News**, credited by CBC as the origin of Leon Murray's account, has not been retrieved and remains outstanding.

**Village Voice News: robots-disallowed.** Respected, not circumvented. The outlet is therefore wholly unrepresented, and one known piece is substantively relevant: "Edghill's swift suspensions of MV Barima workers raise more questions than answers."

**Paywalls and 403s.** CBC's `ferry-sinks-guyana` piece was recovered on 27 July through a browser session, along with the Guardian and Deutsche Welle. Still outstanding: CNN (both `cnn.com` and `edition.cnn.com`, where the browser extension has no read permission for the domain), four Washington Post AP-syndications (three recovered via WRAL and Citrus County Chronicle instead), France 24, Telesur in both languages, El Universal (Venezuela), the New York Times, Radio New Zealand, and Stabroek's own 15 March liquidator follow-up.

**BBC and Reuters: resolved on 27 July.** The first build recorded that no BBC byline and no directly-bylined Reuters article had surfaced through any query, and flagged this as a limit of search reach rather than a confirmed absence. Both exist and are now in the corpus: BBC News, "Death toll from Guyana ferry disaster continues to rise," by Vanessa Buschschlüter and Tom Bennett, 19 July, updated 22 July; and Reuters, "Twenty-seven bodies recovered after ferry capsizes off Guyana," by Kemol King, 20 July. Both were found through the reference list of the English Wikipedia article on the vessel, which is itself now in the corpus. The earlier statement was wrong, and the search method that produced it — keyword queries against the open web — is what failed.

**Two Kaieteur pages** served submission stubs rather than article bodies: "MV Barima tragedy exposes Guyana's deep governance failures" (Tevin Skeete) and one other letter. The important Kaieteur piece, "Major discrepancies found on MV Barima manifest," failed two subagent attempts, which returned only condensed output, and was then recovered verbatim by the lead researcher — it is now the single most valuable news document in the archive.

**Ship registries** were largely unreachable: VesselFinder and Clyde-built Ships are robots-disallowed, MarineTraffic returned 403. Vessel provenance therefore rests on the Paxman History Pages engine register, which is fortunately the best available source anyway.

---

## Substantive gaps — documents that do not appear to exist publicly

These are recorded because a reader needs to know which documents were searched for and not found.

**No certificate.** Nothing in the corpus — not one government release, not one ministerial statement — names a class certificate, a passenger safety certificate, or a load-line survey date for the *MV Barima*. Seaworthiness is asserted entirely on a docking chronology. The certified capacity that underwrites MARAD's "not overloaded" finding has never been published, and MARAD's Director-General cannot say when or why it rose from the 1938 rating of 150 passengers to 394.

**No terms of reference.** As of 26 July the Commission of Inquiry exists only as a presidential announcement. No commissioners named, no chair, no secretary, no gazetted instrument, no statutory basis cited by the President, no reporting deadline, no call for submissions. The only statutory citation anywhere in the corpus is the AFC's proposal to use the Commission of Inquiry Act, Cap. 19:03.

**No official death toll.** The state publishes bodies recovered, never persons missing. The residual has never appeared in a government document.

**No Auditor General finding specific to the T&HD** was located, despite targeted searching, and no trade union statement of any kind — notable given that the suspended and detained are wharf and marine workers.

**No GDF, MARAD, Police Force, Office of the President or Ministry of Public Works web publication** on the disaster. MARAD issued no advisory, no notice to mariners and no certification statement. `parliament.gov.gy` press releases stop at April 2026, its motions index returned empty, and no Hansard exists for the July sitting. The state's entire published output on the disaster runs through DPI — seventeen releases dated 19–25 July, with a further five pre-disaster DPI items in the corpus — and through ministers' Facebook posts. A suspension of officials and a declaration of national mourning were both communicated primarily by social media.

**No IMO and no PAHO statement.** CARICOM and UNDP Guyana issued statements. No statement by the International Maritime Organization appears in the corpus.

---

## Structural finding that shaped the corpus

Stabroek News, Guyana's principal independent daily for roughly forty years, ceased print publication on 15 March 2026 in voluntary liquidation — four months before the disaster. The consequence for this research was that repeated searches for Stabroek coverage of the sinking returned nothing. Two of the corpus's pre-disaster sources on vessel condition — Capt. R. E. W. Adams's 2015 letter naming this vessel, and the 2012 piece on the Sprostons-built fleet — come from Stabroek's letters and features pages.

Independent print scrutiny in Guyana is now effectively Kaieteur News alone, which is why the corpus skews heavily to that outlet (32 sources) and why civil-society bodies such as the GHRA, TIGI and the APA are issuing statements directly rather than arguing in a newspaper's letter columns. Readers should note this distribution when weighing the corpus: it reflects which Guyanese outlets were publishing in July 2026.

---

## Priority follow-ups

The Guyana Chronicle hole has now been closed (see above). The remaining highest-value targets are documentary rather than journalistic: the March 2026 tender documents that reportedly show engineers flagging deteriorated hull sections before the sinking; any survey, load-line or capacity certificate for the vessel; the Commission of Inquiry's gazetted instrument, which had not been published when the commissioners were named on 26 July, with attention to whether its terms reach loading *authorisation* and procurement or stop at loading *execution*; the Auditor General's reports on the T&HD; and the 19 September 2015 Kaieteur inspection report cited by Adams, which was searched for and not found.

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

`archive/` holds the 192 full-text sources, one file per source, plus six `_manifest_*.jsonl` files carrying structured metadata and research annotations for every entry, and `_synthesis_vessel-dossier.md`, a fully cited dossier on the vessel and the T&HD fleet with an explicit unverified-and-contested section.

`deliverables/` holds `00_SOURCE-CATALOGUE.md` (the annotated listing of all sources with summaries, chronological then contextual, plus a distribution table), `01_TIMELINE.md` (reconciled chronology from 1936 to 26 July 2026, with conflicts marked), `02_CONTESTED-FACTS.md` (figure-by-figure reconciliation, single-source claims, reliability guidance), `03_SYSTEMIC-ANALYSIS.md` (the four-pillar systemic brief), and this file.

`_superseded/` holds the ten deduplicated files, retained for audit.
