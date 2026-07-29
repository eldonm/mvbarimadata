# Mining Facebook for MV Barima discussion — options, constraints, recommendation

Prepared 29 July 2026. Every factual claim below was verified against a primary
source this week; where a source could not be reached or sources conflict, that
is marked. Legal summaries are descriptions of published material, not legal
advice — the Guyana Data Protection Act question in particular should go to a
Guyanese attorney before any collection begins.

---

## 1. The decision that comes before the tooling

This archive's entire credibility rests on one property: every claim traces to a
named, dated, published document that a reader can open and check. That property
is what the adversarial review passes have been protecting all month.

Facebook content is a different class of evidence. It is unverified, often
pseudonymous, frequently deleted, and — in the first days after a mass-casualty
event — substantially wrong. The corpus already records that the survivor count
moved 67, 69, 77, 76 and that ten people were listed as found who were already
at home. Facebook in that window will contain names of "victims" who lived.

So the first question is not which tool. It is **what the data is for**, because
the four plausible answers need different pipelines, carry different risk, and
one of them does not belong in this archive at all.

| Purpose | What it needs | Verdict |
|---|---|---|
| **A. Lead generation** — find eyewitnesses, documents, contradictions worth chasing, then verify by ordinary means and cite the verified source | Search and read. No bulk storage, no republication | **Strongest fit.** Social media as a tip line, not as a source |
| **B. Official-account record** — capture what government and outlet Pages published, as primary documents alongside their websites | A small set of known Page URLs, captured and cited | **Good fit.** These are institutional publications, same class as the 209 |
| **C. Public-reaction measurement** — volume, sentiment, what the public was asking and when | Bulk collection of ordinary citizens' posts and comments | **Poor fit, high risk.** See §5 |
| **D. Republishing citizen posts as content** | All of the above plus consent | **Do not.** See §5 |

Most of the value people expect from "mining Facebook" is actually A and B, and
both are obtainable cheaply and legitimately. C is where the cost, the legal
exposure and the ethical problems all concentrate.

---

## 2. Meta Content Library — the sanctioned route

CrowdTangle shut down 14 August 2024. The Content Library is its successor and
is the only Meta-sanctioned way to search public Facebook content by keyword.

**What it would give you.** Posts from Pages, public Groups and Events, plus
profiles that are verified or have 100+ followers. Comments are available
through a dedicated endpoint with date filtering. Search supports keyword, date
range, producer, language and post surface. Guyana is in scope — the excluded
countries are China, North Korea, South Korea and Togo. The web UI is free; the
API inside Meta's Secure Research Environment is free.

This is exactly the capability the request describes, and it is free.

**The gate.** Access requires an *institution*, not an individual. Either an
accredited degree-granting academic institution, or a **not-for-profit
institution whose primary purpose or core activity is scientific or public
interest research**. An institutional email address is mandatory — Meta's
application guidance states that personal addresses such as @gmail.com are not
accepted. A Restricted Data Use Agreement must be countersigned by an
institutional legal representative.

**A commercial company cannot qualify.** That is the binding constraint here.

**Two routes past it, both real:**

1. **Partner with a university.** The University of Guyana, or any accredited
   institution with a researcher willing to be the named applicant. This is the
   normal path and it also gives the archive academic cover it does not
   currently have.
2. **Constitute the archive as a non-profit** whose stated core activity is
   public-interest research. This is a bigger step with its own consequences,
   but it is the step that would also settle the Guyana DPA registration
   question and strengthen any journalism exemption claim.

**Process and timing (as of 2026).** Applications moved off the ICPSR/SOMAR
portal to Meta's own Research Tools Manager on 8 December 2025. CASD in France
became a vetting partner in January 2026. Meta's stated pipeline is 2–3 weeks
CASD review plus 2–3 weeks Meta processing; SOMAR's real-world guidance is six
weeks typical, up to three months, with agreement redlining adding more.

**One unresolved limit worth knowing before investing.** Bulk *export* is
restricted to "widely-known" accounts. Meta's documentation gives 25,000+
followers for Profiles and Instagram accounts; Bellingcat reports a 15,000
threshold for Facebook Pages, which Meta's page does not state. Whether the
Guyanese outlet Pages clear it is unknown. Even if they do not, **the UI is not
threshold-limited for viewing** — so the Content Library would still let you
find what exists, which you could then pursue by other means. That decoupling of
"find" from "obtain" is genuinely useful and is reason enough to apply.

---

## 3. Graph API — narrow but real

Page Public Content Access still exists and grants read access to public posts
and public comments on Pages you do not administer, plus the Pages Search API.
It requires App Review, Business Verification, and possibly additional contracts.
There is no keyword search across posts — you search for Pages, then read each
Page's feed.

Approval posture for a small independent archive is not published anywhere and
should be treated as unproven rather than impossible.

**The far easier version of the same thing:** a Page's own admin can grant your
app access to that Page, or simply export their own post and comment data from
Meta Business Suite in a few clicks. Which leads to the recommendation below.

---

## 4. Third-party scrapers — and why they do not do what is wanted here

Bright Data and Apify both sell Facebook data. Bright Data's Facebook datasets
run to 1.4bn+ records at roughly $250 per 100,000; Apify's posts scraper is
about $2 per 1,000 posts.

**The decisive technical limitation:** for Facebook posts, both discover content
**by Page, Group or post URL — not by keyword**. Bright Data documents keyword
search only for Marketplace and Events. So "find every Facebook post mentioning
the Barima" is not a thing either vendor sells. What they sell is "pull
everything from these Page URLs," which is useful for purpose B and useless for
purpose A.

**The legal position is materially weaker than the marketing implies.** The
2024 Bright Data win against Meta turned on Meta's terms then covering only
"your use" of the service, which Judge Chen read as directed at logged-in
account holders. **Meta rewrote the terms effective 1 January 2025** to prohibit
automated collection "regardless of whether such automated access or collection
is undertaken while logged-in to a Facebook account." That was written to close
exactly this gap. Whether it succeeds is untested, and the earlier ruling was a
single district-court decision with no appeal.

Note also that hiQ v LinkedIn is widely remembered as a scraper victory and
ended as a defeat: hiQ won on the CFAA, lost on breach of contract, and in
December 2022 stipulated to a permanent injunction, deletion of all data and
$500,000 in damages.

A vendor's risk tolerance does not transfer to you. You would be the downstream
controller of the data.

---

## 5. The exposure that matters most here

**Data protection is a separate question from scraping, and it is the one that
actually bites.**

Publicly posted does not mean outside data-protection law. Apify's own legal
guidance says so plainly: under GDPR, all personal data is protected and it does
not matter where it came from.

For a mass-casualty event the content is worse than ordinary personal data. Posts
from survivors reveal health information. Funeral and prayer posts reveal
religious belief. Both are GDPR Article 9 special categories needing a condition
beyond ordinary lawful basis, and the "manifestly made public by the data
subject" exception is read narrowly by EU regulators — it is not satisfied
merely because a post was visible.

GDPR reaches a Guyana-based archive only where it targets or monitors people in
the EU. Most commenters will be in Guyana. **But Guyana has a large diaspora**,
and systematic collection of posts by Guyanese in the Netherlands, the UK or
elsewhere in the EU is close to the paradigm case for Article 3(2)(b). The same
question arises independently under UK GDPR.

**Guyana's own law is the more immediate item.** The Data Protection Act No. 18
of 2023 was enacted and gazetted 16 August 2023. Whether it has commenced is
genuinely contested: Demerara Waves reported on 31 March 2026 that no
commencement order has issued, while Data Protection Commissioner Aneal Giddings
told Kaieteur News on 15 May 2026 that the Act "is the law of the land" and that
the Data Protection Office is being formally established. A Commissioner exists.
The reported scheme includes mandatory registration of data controllers, and an
exemption for journalistic, literary or artistic purposes conditional on
publication being in the public interest. The archive would likely rely on that
exemption — defensible, but not automatic, and the registration duty is cheap to
comply with and an offence to ignore.

**Confirm commencement and registration requirements directly with the Data
Protection Office before collecting anything.** That is a phone call.

**And the non-legal harm is the real constraint.** Bulk-collecting the first
72 hours of Facebook around this disaster means permanently fixing a body of
material that names the wrong dead, identifies survivors who have not chosen to
be public, and captures minors. An archive whose stated purpose is accuracy
would be creating a durable record of inaccuracy about identifiable, grieving
people. There is no technical control that fixes that; only scope discipline
does.

---

## 6. Recommendation, in order

**Step 1 — Email the six outlets. This week. Cost: an afternoon.**
Kaieteur News, Stabroek News, News Room, Guyana Chronicle, iNews Guyana,
Demerara Waves. They own their Pages, and a Page admin can export their own
posts and comments from Meta Business Suite without any special access. Ask for
their MV Barima coverage post and comment export, and for permission to cite it.
This is the only route that legitimately reaches comments at volume, it is free,
it requires no tooling, and it builds relationships worth having anyway. Several
of these outlets are already the archive's largest sources.

**Step 2 — Capture the official Pages properly. Cost: a day of work.**
Government and agency Pages — DPI, the Ministry of Public Works, MARAD, the
Office of the President — publish statements on Facebook that sometimes never
reach a website. Those are institutional publications, exactly the class the
archive already holds. Capture specific public post URLs as fixed, citable
records using WARC-based archiving (Webrecorder or ArchiveBox), review each one,
and file them like any other document. Low volume, human-reviewed, no personal
data of private citizens, and it plugs a genuine gap.

**Step 3 — Apply to the Meta Content Library, via a partner.** Approach the
University of Guyana or another accredited institution for a named academic
applicant. Six weeks to three months. Free. This gives keyword search across
Pages, Groups and Events, which is the capability actually being asked for, and
it arrives through the front door. Start the conversation now because the clock
is long.

**Step 4 — Decide deliberately whether to go further.** If after steps 1–3 there
is still a specific question only bulk citizen posts can answer, that is the
point to weigh a commercial scraper against the ToS position, the data-protection
exposure and the harm profile — with the specific question in hand rather than
in general. My view is that step 4 will not be needed, and that if it is, the
right instrument is a narrowly scoped academic collaboration rather than a
vendor contract.

**What I would not do:** buy a scraping subscription first and work out the
purpose afterwards. It costs money, cannot do keyword search on posts anyway,
puts the archive on the wrong side of Meta's current terms, and creates a
dataset of grieving people's words that the archive would then have to govern.

---

## 7. If the answer is "sentiment and volume"

If the actual goal is measuring public reaction rather than finding facts, say
so and the design changes. That is legitimate research and there is an honest
way to do it: aggregate counts and themes, never republished individual posts,
no names, no screenshots, minimum retention, and a stated deletion policy. It
would need to live somewhere clearly separated from the documented record —
a different page, a different voice, with its method and its limits stated as
plainly as the questions page states its own.

It should not be mixed into the record pages. The archive's strength is that a
reader always knows exactly what kind of thing they are looking at.
