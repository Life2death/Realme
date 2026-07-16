# Placeholder / test Q&A corpus

> ⚠️ **This is stand-in test data, not the final domain.** See the
> warning in `CLAUDE.md` and `docs/DECISIONS.md`. These questions are
> about Vikram's delivery-leadership background (interview-prep style
> content: Citi, Amex, Dell) and are used only to validate the mechanics
> of the pipeline — ingestion format, answer-style layering, escalation
> triggering — while the real SEPA / ISO 20022 / cloud-transformation
> corpus is still being assembled. Do not treat this as the subject the
> clone is meant to specialize in long-term.
>
> **Note on completeness:** only 7 of an intended 10 questions have been
> supplied so far (Q1, Q2, Q3, Q6, Q7, Q8, and one unnumbered question
> here labeled Q9). Q4, Q5, and Q10 are not yet defined — add them here
> using the same template when available, rather than inventing content
> to round out the set.

Each entry follows the template defined in `docs/PROMPT_DESIGN.md` —
Headline / Detail / Escalate-if — reformatted from the original narrative
answers so the answer-style system prompt doesn't have to derive the
layering at answer time.

---

## Q1: Walk us through your current role and the scale you manage.

*(Opener — establish credibility and scope.)*

**Headline:** Associate Director of Delivery at LTIMindtree, owning a
$14M USD portfolio across three Tier-1 clients — Citi (Run-the-Bank and
Retail Risk), American Express regulatory programs, and Dell — leading
120+ associates across US/UK/Europe, with a 10% gross-margin improvement,
a $2.25M account-mining expansion at Citi, and 99.99% availability on
Citi's fraud and credit-risk systems.

**Detail:**
- Owns a hierarchy of Delivery Managers, Lead Architects, and Engineering
  Managers over 120+ associates across the US, UK, and Europe.
- Commercially: drove a 10% gross-margin improvement through pyramid
  rebalancing, and secured a $2.25M account-mining expansion at Citi.
- Operationally: holds 99.99% availability on Citi's fraud and
  credit-risk systems.
- Positioning: end-to-end — commercials, governance, and resilience — not
  just program tracking.

**Key numbers to land:** $14M P&L · 120+ across US/UK/EU · 10% margin ·
$2.25M growth · 99.99% availability.

---

## Q2: Walk us through your hands-on data-platform experience.

*(The core gap — honesty wins here.)*

**Headline:** Not a hands-on Databricks/lakehouse engineer, and won't
pretend to be — the value at this level is governing and delivering data
programs and steering the specialists who go deep; real grounding comes
from the Amex RBI Data Localization program (a data-platform/storage
migration under regulatory pressure) and from a personal hands-on
platform, DRISHTI.

**Detail:**
- Led the RBI Data Localization program at Amex — fundamentally a
  data-platform and storage migration under regulatory pressure.
- Owns cloud-migration roadmaps for legacy financial systems, working
  with Chief Architects.
- Builds hands-on personally: DRISHTI, a structured data-extraction and
  validation pipeline across multiple models.
- Net position: can hold a credible technical conversation with
  engineering managers, challenge estimates, and govern quality — while
  hiring the deep Databricks/lakehouse expertise beneath.

**Escalate if:** asked for hands-on Databricks/lakehouse implementation
detail beyond governance-level conversation — that's outside this scope
by design, not a gap to bluff through.

---

## Q3: Describe a cloud or data-platform transformation you delivered end to end.

*(Strongest technical-delivery story — lead with it.)*

**Headline:** The Amex RBI Data Localization program — moved critical
customer data onto Indian infrastructure to lift a regulatory embargo
that had frozen new customer acquisition, using a Strangler Fig pattern
around an undocumented legacy COBOL platform; 100% compliance
verification, embargo lifted August 2022.

**Detail:**
- Mandate: move critical customer data onto Indian infrastructure to lift
  a regulatory embargo that had frozen new customer acquisition.
- Hardest obstacle: an undocumented legacy COBOL platform — had to be
  reverse-engineered feature by feature before migration was possible.
- Approach: Strangler Fig pattern — built cloud-native replacements
  alongside the legacy system, ran them in parallel, then retired the old
  platform, rather than a big-bang cutover.
- Outcome: 100% compliance verification; embargo lifted August 2022;
  Amex resumed acquisition in India.
- Reusable template: de-risk through parallel-run, govern tightly, zero
  disruption.

**Key numbers to land:** COBOL reverse-engineering · Strangler Fig · 100%
compliance · embargo lifted Aug 2022.

---

## Q6: How do you run delivery inside a regulated financial-services environment?

*(Deepest moat — Citi, Amex, JPMC, payments.)*

**Headline:** Regulated delivery ships on risk/compliance sign-off, not
on code-ready — governed through structured risk registers, dependency
tracking, evidence trails, and clear escalation, with direct grounding in
both data-localization regulation (Amex RBI) and payments compliance
(SEPA/ISO 20022 for Citi UK under the EBA mandate).

**Detail:**
- Default changes in regulated delivery: nothing ships until risk and
  compliance posture is signed off, independent of code readiness.
- Clearest example: Amex RBI Data Localization — a hard regulatory
  deadline with an embargo already in force, so every migration decision
  had to be audit-defensible and reversible.
- Governance mechanism: risk registers, dependency tracking, evidence
  trails, clear escalation.
- Payments-domain grounding: SEPA and ISO 20022 work for Citi UK under
  the EBA mandate — understands clearing and settlement compliance, not
  just generic controls.

**Key numbers to land:** Ship on risk sign-off, not code-ready · RBI/Amex
· SEPA/ISO 20022/EBA STEP2.

---

## Q7: Tell us about a delivery that was failing and how you turned it around.

*(Turnaround is the signature story — run toward it.)*

**Headline:** As the executive escalation point for distressed delivery
streams, the pattern is always: diagnose root cause first (estimation,
capacity, dependency, or capability), then remediate against that
diagnosis with a tight cadence until SLA compliance is restored — proven
under high-load conditions sustaining 99.99% availability on Citi's fraud
and credit-risk engines.

**Detail:**
- Role: executive escalation point for distressed streams as a core part
  of the current role.
- Pattern: diagnose root cause first — estimation, capacity, dependency,
  or capability — before creating a remediation plan; hold a tight
  cadence until SLA compliance is restored.
- Stakes example: Citi Retail Risk — 99.99% availability on fraud and
  credit-risk engines under high transaction load means production
  incidents are existential, which drove building real incident- and
  problem-management discipline (contain and permanently fix, not
  firefight).
- Positioning: runs toward distressed delivery — turnaround is the
  differentiator.

**⚠️ Needs personalization before use:** insert one specific Citi stream
stabilized, with a before/after number (missed SLA % → restored, or
incident count down). A named example beats the general pattern — this
entry is incomplete without it.

---

## Q8: This role influences senior executives. How do you drive decisions with people who outrank you?

*(Leadership attribute called out twice in the JD.)*

**Headline:** Influence comes from evidence and scope, not authority —
aligning stakeholders across US business owners, UK product owners, and
Chennai/Mumbai delivery centers by bringing the commercial and risk
picture with a recommendation attached, not an open question.

**Detail:**
- Stakeholder spread: business owners in the US, product owners in the
  UK, delivery centers in Chennai and Mumbai — constant alignment across
  people who don't report to this role and don't share a timezone.
- Method: own the commercial and risk picture better than anyone else in
  the room; bring numbers, risk exposure, and a recommendation when
  raising a margin decision or a go/no-go on a regulated migration.
- Example: the RBI program required balancing Amex business urgency
  against regulatory constraint — only works if executives trust the
  read is accurate.
- Principle: influence follows credibility.

**Key numbers to land:** Evidence over authority · US/UK/Chennai/Mumbai
alignment · recommendation, not a question.

---

## Q9: The JD lists AI/ML data platforms. What's your real exposure to AI?

*(Differentiator — few delivery leaders can say this.)*

**Headline:** Ahead of most delivery leaders at this level because of
hands-on building — runs a personal multi-model platform, DRISHTI, on a
sub-$25/month stack, which taught the governance discipline (cost
control, auditability, model routing) that matters for enterprise AI,
without overclaiming fine-tuning or production RAG experience.

**Detail:**
- DRISHTI: a personal platform on a sub-$25-a-month multi-model stack —
  Claude for reasoning and adjudication, Gemini Flash for high-volume
  extraction, local agents for validation.
- Working system components: structured data extraction, agent-based
  validation, automated reporting, per-run cost tracking, deliberate
  vendor-concentration management across three providers.
- What it taught: the discipline that matters for enterprise AI — cost
  governance, auditability, routing the right request to the right
  model.
- Explicit boundary: no claim of having fine-tuned models or built
  production RAG — instead, deliberate architectural choices around
  governance.
- Positioning for NCS's AI push: the FinOps-and-governance lens a
  delivery leader should bring from day one.

**Escalate if:** asked for hands-on fine-tuning or production RAG
implementation detail — explicitly out of scope per the boundary stated
above; do not overclaim here.
