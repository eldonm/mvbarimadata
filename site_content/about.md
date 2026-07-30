# Research Notes, Method and Known Gaps

Compiled 26 July 2026, last revised 30 July 2026. Read this before relying on the corpus for anything consequential.

---

## Method

**Social media as a source.** A small number of documents in this corpus are social media posts, and they are labelled as such everywhere they appear: a red badge on the browse card, a red badge on the document page, and a standing warning above the text. They are held under one rule — the account must be an institution or a public figure speaking on the record, and the post must be one a reader could check for themselves. No post by a private individual is collected, and no comment thread is collected at all. That line matters for a disaster: the first days of social media around a mass-casualty event contain the names of people reported dead who were alive, and this archive will not fix that in place.

Social media is used mainly as a lead source rather than as evidence. Where a post points at something real, the archive chases it to published journalism and cites the journalism. The Andrew Donald account is the worked example: it was found as a post by a Member of Parliament, and it is recorded here both as that post and as HGPTV's news report of it, with the report carrying the weight and the post recorded as its origin. Nothing self-published is treated as established because it was posted.

**A new tier: the expert submission.** On 30 July the corpus took in one document that is none of the three things everything else here is. It is not journalism: no outlet commissioned or edited it. It is not a state release. It is not a social media post. It is an unsolicited analysis, written by a named person with stated professional qualifications, sent to this archive by its author and offered as an aid to the Commission of Inquiry. The document is Robert C. Millington's 253-page reading of the Guyanese maritime statute book. It is the only one of its kind here so far, so the tier exists to hold one item, and the rule is written down now rather than after the second one arrives.

**The rule for accepting such a submission.** Four conditions, all of which this one meets. The **author must be named** — an anonymous analysis is not admissible here at any length. He must **state his qualifications**, so a reader can judge what he is qualified to say and what he is not: this author states he is a former merchant marine deck officer and ship pilot and expressly states that he is *not* admitted to practise law in any jurisdiction, which is the more useful half of the disclosure given that the document is about statutes. The **reasoning and the citations must be supplied**, so the work can be checked rather than trusted — here, chapter and section from a named authorised consolidation. And it must be **published in full**, so a reader can audit it against any use this site makes of it, rather than taking the archive's summary on faith. A submission that met three of those four would be recorded as a lead, in the way social media posts are, and not as a source.

**How it is labelled and weighed.** It is marked as a **submitted analysis** everywhere it appears — a badge on its browse card and on its document page, and a standing note above the text. Every proposition drawn from it on the record and analysis pages is attributed to its author by name, marked **[SINGLE SOURCE]** where it rests on him alone, and described as an analysis rather than a record. It is not treated as corroboration of anything, because one person's argument is not a second witness. Its author's own stated limitations are carried with it: the consolidation he read is current only to L.R.O. 1/2012, so any finding of his framed as the absence of a regulation needs checking against later instruments and the Official Gazette. And where it states a fact about the events of 18 July rather than a reading of a statute — it gives the distress signal as 22:43, against the 23:01 this archive carries from the state's own information service — it is treated as any other uncorroborated account would be, and the conflict is recorded rather than resolved. Expertise earns a hearing here. It does not earn the status of record.



**Tooling.** The research, the retrieval, the cross-checking and the reasoning on this site were carried out with **Claude Opus 5**, Anthropic's frontier model, working over the corpus described below. Every claim is nonetheless traceable to a named published document, and the adversarial checks that found and corrected this archive's own errors are logged on the [revisions page](changelog.html). The model is a tool; the sources are the authority.

Five parallel research streams were run against the open web, plus a sixth gap-recovery pass: Guyanese domestic press; official and state sources; international wires and regional press; vessel and institutional history; aftermath, accountability and public debate; and finally the Commission of Inquiry cluster and press-capacity context. Each source was retrieved individually and written to `archive/` as a markdown file with metadata frontmatter recording outlet, author, publication date, URL, retrieval date, tier, stream, genre, casualty figures cited, and extracted key claims.

The corpus was then deduplicated by canonical URL, keeping the fullest capture in each case. Ten superseded duplicates were moved to `_superseded/` rather than deleted, so nothing is lost. Two files had been misfiled as official primary sources when they were in fact press reports of official statements; the correctly attributed versions were kept.

**Standing rule applied throughout:** no file was written containing invented, reconstructed or paraphrased-as-verbatim text. Where retrieval failed, the failure is recorded here rather than papered over. Where the retrieval tool returned condensed prose despite instructions, the file carries a `capture_fidelity` warning — in those files direct quotations are reliable and connective prose is the tool's compression, not the outlet's wording. Do not quote a flagged file as verbatim.

**Corpus:** 266 documents, counted by the date each was retrieved. 152 in the first build of 26 July; 40 Guyana Chronicle articles the same day; 17 on 27 July, being international sources recovered through a browser session and the first Kiskadee Watch reporting; 24 on 29 July, covering 28–29 July, four of them social media posts; and 33 on 30 July — eight in the morning (seven pre-disaster context sources recovered while answering a submitted question about the Fort Island ferry operation, plus one submitted expert analysis) and 25 in an evening sweep covering 29 and 30 July. That sums to 266. **235** are dated 19 July 2026 onward; the remaining **31** are pre-disaster context and undated reference material reaching back to the 1930s builder's record &mdash; 26 carrying a pre-disaster date and five undated. (An earlier version of this line said 235 documents were dated from 19 July and 30 were not. The error was a sorting one: one undated file records its date as the words "Undated (living document)", which a naive string comparison sorts *after* a 2026 date rather than before it, so it was counted on the wrong side. Corrected on 30 July.) Note that this is a split by **date** and the table below is a split by **kind**; they are different partitions of the same 266 documents and their rows do not correspond. One undated reference work, for instance, is counted here among the 31 and below among the three reference works.

---

## Corrections and questions

**Corrections.** If something here is wrong, it should be fixed and the fix logged. Every correction made so far is on the [revisions page](changelog.html), including the ones that withdrew claims this archive had published. [Send a correction](ask.html) — and if you hold the document, send that.

**Questions.** The [questions page](questions.html) is open to anyone. [Send a question](ask.html) and it will be answered there by Claude Opus 5 reading across the whole corpus, on the same terms as everything else here: evidence named, limits stated, and the short answer first. That page is analysis rather than sourced record, and it says so at the top. A question the archive cannot answer will be published as such, because what the record cannot answer is itself a finding.

Both routes go through the same form, which delivers by email. No address is published on this site, which keeps it out of reach of address harvesters; the form is the contact route.

---

## What the count contains

A reader was right to object that "200 sources" overstates what this archive holds. In archival usage a source is a document in the corpus, and each of the 200 is exactly that — a distinct published document with its own publisher, date and link. But a general reader hears the number as 200 independent accounts, and that is not what it is. The count is now given as documents, and the composition is set out here so the number carries its own qualification.

| What it is | Documents |
|---|---|
| Original reporting on the sinking | 170 |
| Pre-disaster context | 30 |
| Syndicated wire copy (AP, Reuters, CMC, AFP carried by other outlets) | 21 |
| Government communication (DPI releases, official statements, instruments) | 19 |
| Opinion, letters and editorials | 18 |
| Social media posts by institutions and public figures | 4 |
| Reference works (encyclopedia, engine and vessel registries, directories) | 3 |
| Expert submission (named author, published in full) | 1 |
| **Total** | **266** |

The 29 July build added 24 documents: seventeen pieces of Guyanese reporting on the charges, the wreck, the former captain's account and the minister's first response to the resignation demands; three regional carriages of the same story; and four social media posts, which are labelled as such wherever they appear and are the first of their kind in this corpus. One of those posts was, at the time, the only record here of a picket at the Office of the President. That is no longer so: the 30 July sweep brought in four press accounts of the same picket, and the note recording its absence has been withdrawn from the chronology and the positions page.

The 30 July morning build added eight. Seven are pre-disaster context, recovered in the course of answering the first question submitted by a member of the public — the 2022 Fort Island stelling contract, the 2022 resumption of ferry calls there, the May 2026 Independence ferry operation and its aftermath, the December 2025 commissioning of the *MV Konawaruk 1899*, and an undated trade review of the *MV Ma Lisha*, the last of which is counted as a reference work rather than as reporting. The eighth is the expert submission, and it is the first document in this corpus that is neither journalism, a state release nor a social media post; the tier and the rule for admitting it are set out under Method above. **None of the eight is original reporting on the sinking by an independent outlet**, which is why that row is unchanged and why the independence figure below has not moved.

Three qualifications matter more than the totals.

**Syndication multiplies one act of reporting.** A single Associated Press dispatch appears here via Afro.com, WRAL twice, and the Citrus County Chronicle. One CMC wire appears via both CBC Barbados and the Jamaica Observer. CBC News's report is Thomson Reuters copy, so CBC and Reuters in this archive are substantially the same reporting counted twice. These variants are kept deliberately — which outlet carried which figure on which day is part of the record, and the archive uses it to show two irreconcilable death tolls running side by side in international copy for about forty-eight hours — but they are not independent corroboration.

**Roughly a quarter of the documents are the state's own voice.** The state-owned *Guyana Chronicle* supplies 40 and the Department of Public Information 25: 65 of 266. That is primary material of real value, being what the government said and when, but it is not independent of the body under scrutiny. The state's share fell slightly on 30 July, because the evening sweep added 24 documents from private outlets and one DPI release.

**Four documents are duplicates or republications**, including the *Guyana Chronicle* publishing the same report at two dates and URLs, and two syndicated pairs carrying identical headlines.

Counting only original reporting on the sinking by outlets that are neither state-owned nor carrying another outlet's wire copy, the figure is **128 rather than 266**. That count is checked at each build rather than carried forward. The morning build of 30 July added eight documents and none of them qualified — six pre-disaster news and government items, one undated trade review of a vessel, and one submitted analysis — so the numerator did not move at all. The evening sweep of the same day added 25, of which 21 do qualify: original Guyanese reporting on the swearing-in of the Commission, the protests of 29 July, the legal reaction to the charges, the Attorney General's remarks, a funeral, a bereaved mother's account, the Ministry's cargo list and two mental-health assessments. The remaining four are one DPI release and three opinion pieces. So on 30 July the independent numerator moved for the first time since 29 July, and it moved by 21.

**Outlet names were deduplicated on 27 July.** The archive had been holding 51 distinct publisher strings for what were in fact 42 publishers: HGPTV had been recorded five different ways, and Demerara Waves, iNews Guyana, Democracy Guyana, the Department of Public Information and Wikipedia twice each. Those twenty records now carry a single canonical name per publisher, which both cleans the outlet filter and stops the archive overstating how many publishers it draws on.

Four apparent duplicates were deliberately left alone because they are different publishers: BBC News, Canada's CBC News and the Caribbean Broadcasting Corporation in Barbados; the Jamaica Gleaner and the Jamaica Observer; the Guyana Chronicle and the Guyana Graphic; and iNews Guyana, News Room Guyana, News Source Guyana and Things Guyana. The Associated Press entries are also kept separate by carrier — *via WRAL*, *via Afro.com*, *via Citrus County Chronicle* — because which outlet carried a wire report is part of what this archive records. CBC News is now labelled *CBC News (Canada)* to distinguish it from the Barbadian broadcaster.

After deduplication three publishers still account for 118 of the 266 documents — Kaieteur News 53, the *Guyana Chronicle* 40 and the Department of Public Information 25. Two of those three are the state. A further dedup was needed on 30 July: HGPTV had drifted back into two publisher strings, "HGPTV" and "HGPTV Nightly News", across sixteen files. They are one publisher and now carry one name.

---

## Retrieval failures — what could not be captured

**Guyana Chronicle: closed on 26 July.** In the first build this was the largest single gap in the corpus. Every fetch attempt, across bare, `www.` and `/amp/` variants, hit a JavaScript redirect wall, and the state-owned Chronicle was absent from the archive entirely. It has since been retrieved through a browser session: 40 articles dated 22–26 July, of which 38 carry full text. Two are flagged `thin-capture` and marked as incomplete on their source pages. The change is logged on the [revisions page](changelog.html).

**Kiskadee Watch: retrieved 27 July.** The BBC credits this independent Guyanese outlet as the origin of Elena Moonsammy's account. Two of its reports are now in the corpus, and they carry survivor testimony on the vessel's machinery that is not present elsewhere. **Ignite News**, credited by CBC as the origin of Leon Murray's account, is now represented by its own 18–21 July chronology. The specific Murray interview was not found on the outlet's site and remains outstanding; CBC's account of it is in the corpus, the original is not.

**Village Voice News: robots-disallowed.** Respected, not circumvented. The outlet is therefore wholly unrepresented, and one known piece is substantively relevant: "Edghill's swift suspensions of MV Barima workers raise more questions than answers."

**Paywalls and 403s.** CBC's `ferry-sinks-guyana` piece was recovered on 27 July through a browser session, along with the Guardian and Deutsche Welle. Still outstanding: CNN (both `cnn.com` and `edition.cnn.com`, where the browser extension has no read permission for the domain), four Washington Post AP-syndications (three recovered via WRAL and Citrus County Chronicle instead), France 24, Telesur in both languages, El Universal (Venezuela), the New York Times, Radio New Zealand, and Stabroek's own 15 March liquidator follow-up.

**BBC and Reuters: resolved on 27 July.** The first build recorded that no BBC byline and no directly-bylined Reuters article had surfaced through any query, and flagged this as a limit of search reach rather than a confirmed absence. Both exist and are now in the corpus: BBC News, "Death toll from Guyana ferry disaster continues to rise," by Vanessa Buschschlüter and Tom Bennett, 19 July, updated 22 July; and Reuters, "Twenty-seven bodies recovered after ferry capsizes off Guyana," by Kemol King, 20 July. Both were found through the reference list of the English Wikipedia article on the vessel, which is itself now in the corpus. The earlier statement was wrong, and the search method that produced it — keyword queries against the open web — is what failed.

**Two Kaieteur pages** served submission stubs rather than article bodies: "MV Barima tragedy exposes Guyana's deep governance failures" (Tevin Skeete) and one other letter. The important Kaieteur piece, "Major discrepancies found on MV Barima manifest," failed two subagent attempts, which returned only condensed output, and was then recovered verbatim by the lead researcher — it is now the single most valuable news document in the archive.

**Ship registries** were largely unreachable: VesselFinder and Clyde-built Ships are robots-disallowed, MarineTraffic returned 403. Vessel provenance therefore rests on the Paxman History Pages engine register, which is fortunately the best available source anyway.

---

## Substantive gaps — documents that do not appear to exist publicly

These are recorded because a reader needs to know which documents were searched for and not found.

**No certificate.** Nothing in the corpus — not one government release, not one ministerial statement — names a class certificate, a passenger safety certificate, or a load-line survey date for the *MV Barima*. Seaworthiness is asserted entirely on a docking chronology. The certified capacity that underwrites MARAD's "not overloaded" finding has never been published, and MARAD's Director-General cannot say when or why it rose from the 1938 rating of 150 passengers to 394.

**No terms of reference.** This gap has narrowed twice and is not closed. A chair and four commissioners were named on 26 July, and on 30 July all five were sworn in at State House before Chief Magistrate Judy Latchman, the chairman virtually. The Department of Public Information's release of that day states the enabling statute for the first time — section 2(1) of the Commissions of Inquiry Act, Cap. 19:03 — which confirms what Kiskadee Watch reported on 27 July and what the AFC had proposed. What is still not in the corpus: any gazetted instrument or Statutory Instrument number, any published terms of reference as a document rather than a paraphrase, a named secretary (Demerara Waves states flatly on 30 July that none has been named), a reporting deadline, a budget figure or appropriation, rules of procedure, or a call for submissions. President Ali is reported as saying the commissioners will determine their own procedures, which means the procedural rules did not exist as at 30 July. The swearing-in itself was closed to the press and streamed on the President's social media accounts instead.

**No official death toll.** The state publishes bodies recovered, never persons missing. The residual has never appeared in a government document.

**No Auditor General finding specific to the T&HD** was located, despite targeted searching, and no trade union statement of any kind — notable given that the suspended and detained are wharf and marine workers.

**No GDF, MARAD, Police Force, Office of the President or Ministry of Public Works web publication** on the disaster. MARAD issued no advisory, no notice to mariners and no certification statement. `parliament.gov.gy` press releases stop at April 2026, its motions index returned empty, and no Hansard exists for the July sitting. The state's published output on the disaster runs almost entirely through DPI — seventeen releases dated 19–25 July, then four days of nothing, then one release on 30 July about the swearing-in of the Commission, with a further seven pre-disaster DPI items in the corpus — and through ministers' Facebook posts. A suspension of officials and a declaration of national mourning were both communicated primarily by social media.

**No IMO statement.** CARICOM and UNDP Guyana issued statements. No statement by the International Maritime Organization appears in the corpus, and TIGI's call of 23 July for an IMO-led investigation is still unanswered — TIGI's president spoke publicly again on 30 July and did not renew it. PAHO is no longer absent: its Country Representative praised the state's response on 30 July, but incidentally, at the signing of an unrelated agreement, and on public-health rather than maritime ground.

**No statutory text.** The corpus now holds a detailed reading of Cap. 49:01, Cap. 49:04, Cap. 49:07 and Cap. 50:01, with chapter and section cited, in the expert submission described under Method. It does not hold the instruments. No authorised text, no subsidiary regulation and nothing from the Official Gazette has been retrieved, and no post-2012 instrument has been checked — which is the specific gap the submission's own stated limitation points at, since most of its findings are findings of absence.

**Four named institutional documents that are not here and may exist.** The submission identifies the IMO Member State Audit report on Guyana, Guyana's corrective action plan arising from it, the progress reports on that plan, and the report and recommendations of Professor Duke Pollard on updating Guyana's maritime legislation. Unlike most of the gaps on this list these are not inferred absences: they are named, dated and attributed to a 2019 public statement by MARAD's then Director General. This archive has not established that any of them exists and has not attempted retrieval.

---

## Structural finding that shaped the corpus

Stabroek News, Guyana's principal independent daily for roughly forty years, ceased print publication on 15 March 2026 in voluntary liquidation — four months before the disaster. The consequence for this research was that repeated searches for Stabroek coverage of the sinking returned nothing. Two of the corpus's pre-disaster sources on vessel condition — Capt. R. E. W. Adams's 2015 letter naming this vessel, and the 2012 piece on the Sprostons-built fleet — come from Stabroek's letters and features pages.

Independent print scrutiny in Guyana narrowed sharply with Stabroek's closure. Kaieteur News, at 53 documents, is the largest single contributor here, and civil-society bodies such as the GHRA, TIGI and the APA are issuing statements directly rather than arguing in a newspaper's letter columns. But the state is close behind it and larger in aggregate: the state-owned *Guyana Chronicle* supplies 40, and with the Department of Public Information's 25 releases the state or a state-owned outlet accounts for 65 of the 266 documents. Kiskadee Watch, added on 27 July, is a further independent Guyanese voice. Readers should weigh that distribution: it reflects which Guyanese outlets were publishing, and which were state-funded, in July 2026.

---

## Priority follow-ups

The Guyana Chronicle hole has now been closed (see above). The remaining highest-value targets are documentary rather than journalistic: the March 2026 tender documents that reportedly show engineers flagging deteriorated hull sections before the sinking; any survey, load-line or capacity certificate for the vessel; the Commission of Inquiry's gazetted instrument, which had not been published when the commissioners were named on 26 July, with attention to whether its terms reach loading *authorisation* and procurement or stop at loading *execution*; the Auditor General's reports on the T&HD; and the 19 September 2015 Kaieteur inspection report cited by Adams, which was searched for and not found.

Four more were added on 30 July, all arising from the expert submission and all of a kind this archive has not previously chased: the authorised texts of Cap. 49:01, Cap. 49:04, Cap. 49:07 and Cap. 50:01 together with their subsidiary regulations and anything gazetted since 2012, without which no statutory proposition on this site can be verified; the IMO Member State Audit report on Guyana and Guyana's corrective action plan and progress reports; the Pollard report on updating Guyana's maritime legislation; and contemporaneous 2019 reporting of Claudette Rogers's statement of 27 March 2019, which currently reaches this archive only through the submission that quotes it. Separately and more urgently than any of them: anything bearing on section 23 of the Transport and Harbours Act and whether a six-month limitation period is in fact running against claims arising from this casualty, which is set out on the [figures page](facts.html) and is a matter for Guyanese lawyers rather than for this archive.

On the live story, the variables worth monitoring are whether the wreck is righted and what that does to the count, whether the residual of roughly thirty missing is ever officially named, whether charges are laid and against whom, whether Parliament sits before the Commission is constituted, and whether any pre-18-July document surfaces bearing a named official's knowledge of the hull's condition.

---

## The verification pass

After the deliverables were drafted, a separate adversarial pass re-checked every name, figure, date, quotation and claim-of-absence against the archive, with instructions to falsify rather than confirm. It found eighteen substantive errors, all now corrected. They are recorded here because the pattern is instructive for anyone extending this work.

The most common failure was **quotation drift** — a paraphrase hardening into quotation marks across drafts. "MV Barima was seaworthy" is DPI's headline, not Edghill's words; his actual formulation was the much narrower "there was no report of any kind that suggested the vessel was unseaworthy." "Frequent mechanical failures" was being quoted from a tool-condensed file whose own note warned that only one unrelated sentence in it was verbatim. "Not compensation" was a truncation of a Prime Ministerial statement about *sequencing* into an apparent legal characterisation the state never made.

The second pattern was **attribution slippage**. Saiku Andrews, an opposition MP voicing a claim, had become a Jamaica Observer byline. Deon La Cruz, an opposition MP, had become a reporter. Toxicology disclosure had migrated from Edghill to Jagdeo. A Bulkan letter's headline had become "Kaieteur's framing." A letter-writer's argument had become a newspaper's editorial position. In each case the substance was right and the source was wrong, which is the more dangerous kind of error because it survives casual checking.

Third, **figures merging**. The vessel's capacity had been rendered as a single "284 tons / 394 passengers" when in fact Thomas said 394/126 tonnes, then 394/120 tonnes, and Edghill said 397/284 tonnes — three inconsistent official statements whose inconsistency is itself the finding. A search area "expanded to 32 square miles" was actually expanded *by* 32, on top of an earlier 400.

Fourth, **inference presented as record**: the *Ma Lisha* dated to 2021 rather than its actual 2023 commissioning; "sole vessel serving Region One" where the archive supports only "sole vessel on the Port Kaituma route"; the 2017 refit's "installation of two engines" hardening into a claim that the 1939 machinery was entirely replaced.

And one **claim of absence that was simply false**: the corpus does contain Reuters copy, indirectly.

Two things the pass surfaced that are now flagged in the analysis rather than fixed. The Prime Minister stated on 25 July that the state has **"no such record"** of a Mayday from the captain — which contradicts the 23:01 timing on which every published chronology, including this one, depends. And **Elena** Moonsammy (Guyanese press, lost seven children she travelled with, sole source for cargo at the stern) and **Helena** Moonsammy (AP and Gleaner, a grandmother who lost four grandchildren and spent nine hours in the water) may be two different people; earlier drafts merged them as one name with variant spellings, which the archive does not support.

## Directory structure

`archive/` holds the 266 full-text sources, one file per source, plus seven `_manifest_*.jsonl` files carrying structured metadata and research annotations for every entry, and `_synthesis_vessel-dossier.md`, a fully cited dossier on the vessel and the T&HD fleet with an explicit unverified-and-contested section.

`deliverables/` holds `00_SOURCE-CATALOGUE.md` (the annotated listing of all sources with summaries, chronological then contextual, plus a distribution table), `01_TIMELINE.md` (reconciled chronology from 1936 to 26 July 2026, with conflicts marked), `02_CONTESTED-FACTS.md` (figure-by-figure reconciliation, single-source claims, reliability guidance), `03_SYSTEMIC-ANALYSIS.md` (the four-pillar systemic brief), and this file.

`_superseded/` holds the ten deduplicated files, retained for audit.
