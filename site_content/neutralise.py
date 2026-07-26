# -*- coding: utf-8 -*-
"""Strip evaluative and advocacy language from the site copy, preserving every
factual claim and attribution. Fails loudly if a target string is not found."""
import io, sys

R = {}

R['timeline.md'] = [
# --- framing / headings ---
("Compiled 26 July 2026 from the 152-source archive, then adversarially verified against it. Every claim is attributed. Where sources conflict, both versions appear and the conflict is marked **[CONTESTED]**; where a consequential claim rests on one source, it is marked **[SINGLE SOURCE]**. See `02_CONTESTED-FACTS.md` for the full reconciliation. Times are local (UTC−4).",
 "Compiled 26 July 2026 from 152 published sources and checked against them. Every entry is attributed to the source that reports it. Where sources conflict, both versions are given and marked **[CONTESTED]**; where a claim appears in only one source it is marked **[SINGLE SOURCE]**. Times are local (UTC−4)."),
("## Part I — The long fuse, 1936–2026", "## Part I — Vessel and institutional record, 1936–2026"),
("## Part IV — The reckoning, 19–26 July 2026", "## Part IV — Response, investigation and public reaction, 19–26 July 2026"),
("## Part II — The voyage, Saturday 18 July 2026", "## Part II — The voyage, Saturday 18 July 2026"),
("## The arithmetic that has never been stated", "## Figures reported, and the arithmetic they imply"),
# --- evaluative removals ---
("This is the firmest provenance in the corpus, and it is corroborated from an unexpected direction: Kaieteur News, while arguing *against* the age thesis, independently dates the sister ship to 1937.",
 "This is the earliest independent record of the vessel in the corpus. Kaieteur News, in a piece disputing the relevance of the vessel's age, separately dates the sister ship to 1937."),
("**[CONTESTED] Certified capacity — the single most consequential unresolved figure.**",
 "**[CONTESTED] Certified capacity.**"),
("She is the Caribbean's defining ferry disaster and the precedent Guyanese commentators now invoke. The archive also indicates she came off the Sprostons slipway in Georgetown in 1958–59, the same yard and years as the T&HD's own *Torani* and *Malali* — a connection the commentary has missed.",
 "Guyanese commentators have cited it as precedent in July 2026 coverage. One source in the corpus also places her construction at the Sprostons slipway in Georgetown in 1958–59, the same yard and period as the T&HD's *Torani* and *Malali*."),
("This is the most specific pre-disaster warning in the corpus, published eleven years before the sinking.",
 "It is the earliest source in the corpus to name this vessel and describe its condition directly, published eleven years before the sinking."),
("The state's own diagnosis, sixteen months out.", "Published sixteen months before the sinking."),
("**[CONTESTED]** cause; **[CONTESTED]** date — Stabroek says print ceased 15 March, Kaieteur says 14 March. The structural consequence is not contested: four months before the disaster, Guyana lost its main independent print scrutiny.",
 "**[CONTESTED]** cause; **[CONTESTED]** date — Stabroek reports print ceased 15 March, Kaieteur reports 14 March. Print publication ceased four months before the sinking."),
("Edghill's press conference detonates the paper record: only **35 of the 67 rescued appear on the manifest**",
 "At an evening press conference Edghill stated that only **35 of the 67 rescued appeared on the manifest**"),
("and argues age is irrelevant because modern thin steel is stronger — an argument that implicitly concedes the 1939 hull was not modern.",
 "and states that age is not determinative because modern thin steel is stronger."),
("The state has never published a death toll. It publishes bodies recovered. Against a working complement of **179** and **76–77 survivors**, the residual is **102–103 people**. Seventy-three have been recovered. The gap — roughly thirty people — is the number no official document in this archive names.",
 "No official death toll appears in the corpus. Government releases report bodies recovered. Against a stated complement of **179** and **76–77 survivors**, subtraction leaves **102–103 people**. Seventy-three bodies had been recovered as of 26 July. The difference — approximately thirty people — does not appear as a figure in any government release in this corpus."),
]

R['facts.md'] = [
("Compiled 26 July 2026, then adversarially verified against the archive. Purpose: to keep the corpus usable when figures are later revised, retracted or litigated. Nothing here is settled; everything is attributed.",
 "Compiled 26 July 2026 and checked against the 152 sources. Purpose: to record what each figure was, who stated it, when, and on what stated basis, so the record remains usable as figures are revised. Nothing here is settled; everything is attributed."),
("## 1. How many people were aboard\n\nThis is the load-bearing dispute, because every other number depends on it.",
 "## 1. How many people were aboard\n\nOther figures in this record depend on this one."),
("**Certified capacity — the figure nobody can produce.** Three mutually inconsistent versions circulate, all from officials, none backed by a published certificate:",
 "**Certified capacity.** Three inconsistent versions appear in the corpus, all attributed to officials. No published certificate appears in the corpus:"),
("**The critical finding.** The manifest was not a flawed document; for roughly twenty-four hours it was a fiction the state read aloud to bereaved families. Only **35 of the first 67 survivors** appeared on it — meaning thirty-two people who demonstrably survived were never recorded as having boarded. The eventual figure of 179 was reconstructed from **CCTV footage**, not paperwork. Demerara Waves' columnist caught the arithmetic before the state conceded it: rescued plus recovered plus missing had already exceeded 170 while the official complement stood at 133.",
 "**What the sources record.** Only **35 of the first 67 survivors** appeared on the manifest, per Edghill on 19 July — so thirty-two people recorded as rescued were not recorded as having boarded. DPI releases of 19 July state that families were being updated using the vessel's manifest. The figure of 179 is attributed to a review of **CCTV footage** rather than to any paper record. A Demerara Waves column of 22 July noted that rescued plus recovered plus missing already exceeded 170 while the official complement stood at 133."),
("## 2. Survivors — a count that moved backwards", "## 2. Survivor figures and their revision"),
("Two outlets explained the reversal. News Room attributed it to de-duplication across uncoordinated reporting channels; Kaieteur described the same verification and reconciliation process taking 77 down to 76. Demerara Waves gave the concrete case — ten people \"found\" overnight Monday were already at home. This matters beyond bookkeeping: it is direct evidence that no single authority controlled the count during the first seventy-two hours.",
 "Two outlets reported a reason for the reduction. News Room attributed it to de-duplication across uncoordinated reporting channels; Kaieteur described the same verification and reconciliation process taking 77 down to 76. Demerara Waves reported that ten people recorded as found overnight Monday were already at home."),
("**The number never published.**", "**Figures not published.**"),
("**The structural weakness in the claim.** Seaworthiness is asserted on a *docking chronology* — last docked 2024, next due latter half of 2026 — never on a document. No source in the archive names a class certificate, a passenger safety certificate, or a load-line survey date. And \"not overloaded\" rests on a capacity figure that MARAD's own Director-General cannot trace back from the 1938 rating, and which he and Edghill state differently. **The claim of compliance and the claim of overloading are equally unfalsifiable, because the certified capacity has never been published.**",
 "**What the corpus does and does not contain.** The seaworthiness statements in the corpus rest on a *docking chronology* — last docked 2024, next due latter half of 2026. No source in the corpus names a class certificate, a passenger safety certificate, or a load-line survey date. The \"not overloaded\" statement rests on a capacity figure that MARAD's Director-General said he could not trace back from the 1938 rating, and which he and Edghill stated differently. **Neither the claim that she was overloaded nor the claim that she was not can be checked against a published document, because no certified capacity has been published.**"),
("Note also that Thomas's argument concedes more than it defends: if modern thin steel is stronger, the 1939 hull was by his own reasoning not modern. On the machinery, the 2017 rehabilitation is described as including \"installation of two engines\"; whether that means the original Paxmans were entirely replaced is not established in the corpus, so \"87 years old\" is safely said of the hull and not of the plant.",
 "On the machinery, the 2017 rehabilitation is described as including \"installation of two engines\"; whether the original Paxman engines were entirely replaced is not established in the corpus. The figure of 87 years is therefore supported for the hull and not for the machinery."),
("Note that Thomas's own stability reasoning, applied to these facts, points at loading and free-surface effect rather than at the helm.",
 "Thomas's stability explanation and the survivor accounts of loading were not reconciled in any source in the corpus."),
("## 8. Compensation versus funeral costs — a distinction being blurred",
 "## 8. Compensation and funeral costs as reported"),
("Reporting that compresses this into the state calling payments \"not compensation\" misstates it.",
 "The corpus does not contain a statement by any official characterising payments as \"not compensation\"; that wording is a compression of the quotation above."),
("**Strongest evidentiary weight:**", "**Earliest or most directly sourced:**"),
]

R['about.md'] = [
("**This is the largest single gap and the highest priority for recovery**, most plausibly through a browser session rather than a fetch tool.",
 "This is the largest single gap in the corpus. Recovery would most plausibly require a browser session rather than a fetch tool."),
("## Substantive gaps — documents that do not appear to exist publicly\n\nThese matter more than the retrieval failures, because their absence is itself a finding.",
 "## Substantive gaps — documents that do not appear to exist publicly\n\nThese are recorded because a reader needs to know which documents were searched for and not found."),
("**A suspension of officials and a declaration of national mourning were both communicated primarily by social media.**",
 "A suspension of officials and a declaration of national mourning were both communicated primarily by social media."),
("**No IMO and no PAHO statement.** CARICOM and UNDP Guyana issued statements; the maritime safety body with actual jurisdictional competence has said nothing.",
 "**No IMO and no PAHO statement.** CARICOM and UNDP Guyana issued statements. No statement by the International Maritime Organization appears in the corpus."),
("The consequence for this research was immediate and concrete: repeated searches for Stabroek coverage of the sinking returned nothing, and the archive's two most technically substantial pre-disaster warnings, Capt. R. E. W. Adams's 2015 letter naming this vessel and the 2012 piece on the Sprostons-built fleet, both come from Stabroek's letters and features pages — the forum that no longer exists.",
 "The consequence for this research was that repeated searches for Stabroek coverage of the sinking returned nothing. Two of the corpus's pre-disaster sources on vessel condition — Capt. R. E. W. Adams's 2015 letter naming this vessel, and the 2012 piece on the Sprostons-built fleet — come from Stabroek's letters and features pages."),
("Any reader of this archive should hold that distortion in mind: it is a property of the Guyanese media environment in July 2026, not of the research design.",
 "Readers should note this distribution when weighing the corpus: it reflects which Guyanese outlets were publishing in July 2026."),
]

fails = []
for fn, pairs in R.items():
    src = io.open(fn, encoding='utf-8').read()
    for old, new in pairs:
        if old not in src:
            fails.append((fn, old[:70]))
            continue
        src = src.replace(old, new, 1)
    io.open(fn, 'w', encoding='utf-8').write(src)

if fails:
    print('UNMATCHED (nothing replaced for these):')
    for fn, s in fails:
        print(' ', fn, '::', s)
    sys.exit(1)
print('all replacements applied cleanly')
