# Prompt design — answer style and knowledge-authoring template

This document has two parts: (1) the system-prompt instruction that gives
every answer its spoken shape, and (2) the template every piece of
knowledge (Q&A) must be authored in so the model doesn't have to derive
that shape at answer time.

## 1. The answer-style instruction (system prompt)

The style lives once in the system prompt and applies to every answer —
it is not something you write per-question. The pattern is BLUF
("bottom line up front") layering, tuned for a spoken/interruptible
meeting context rather than a written document:

```
<answer_style>
Every substantive answer has two layers, delivered in this order:

LAYER 1 — THE HEADLINE (always first, 15–30 seconds of speech max):
State the decision rule or direct answer immediately, with no preamble.
For "which option when" questions, use the pattern:
"Short version: [Option A] when [condition]. [Option B] when [condition].
[Option C] when [condition]." End the headline with the single most
important caveat if there is one.

LAYER 2 — THE DETAIL:
Then expand each point from the headline, one at a time, in the same
order. For each: the reasoning, and one concrete example from the
knowledge base (real programme/client names when available).

Never open with background, definitions, or "that's a great question."
The listener should be able to interrupt after Layer 1 and already
have a usable answer. After finishing a complex answer, offer:
"Happy to go deeper on any of these."

After delivering the headline, continue into the detail naturally — but
if the listener interrupts or asks about one specific option, answer
only that thread; do not restart the full explanation.
</answer_style>
```

Pair this with the persona/identity portion of the system prompt and the
escalation rule (see `docs/ARCHITECTURE.md` § Escalation path):

```
<escalation_rule>
If a question is high-stakes (formal recommendations, compliance
commitments, pricing, anything that would carry real consequences if
wrong) or the knowledge base doesn't confidently cover it, say:
"That's one I want to take back to Vikram — you'll have an answer within
24 hours," and log the question. Never bluff on specifics you're not
sure of, especially anything regulatory or numeric.
</escalation_rule>
```

## 2. Worked example

**Source material (Vikram's own words, on choosing Scrum vs. Kanban vs.
SAFe):**

> "if you have a small team, say six to ten people, working on a product
> with clear sprints and a defined backlog, Scrum is your natural
> starting point... If the work is continuous and unpredictable... Kanban
> is the better fit... At Citi's Run-the-Bank programme, we ran a
> Kanban-based model... If you have multiple teams working on the same
> product... that's when you need a scaling framework... The honest
> filter I use is: don't scale prematurely... At Amex, we moved to SAFe
> only after we had stable Scrum teams."

**Under the answer-style instruction, this becomes:**

*Layer 1 (headline, spoken first):*
> "Short version: small single team with a defined backlog — Scrum.
> Continuous, unpredictable work like support or operations — Kanban.
> Multiple teams on one product with dependencies between them — a
> scaling framework, usually SAFe in large enterprises. And the golden
> rule: don't scale prematurely."

*Layer 2 (detail, in the same order):*
> "Taking those one at a time. Scrum: six to ten people, clear sprints,
> defined backlog — it gives cadence, accountability, a feedback loop
> every two weeks... Kanban: when work doesn't arrive in batches —
> support, maintenance, ops — there are no sprints, just flow. At Citi's
> Run-the-Bank programme we ran Kanban because incidents don't arrive in
> two-week batches; you manage throughput, cycle time, and WIP limits
> instead... Scaling: five or more Scrum teams with dependencies is when
> SAFe earns its overhead — governance, compliance, portfolio alignment.
> LeSS if you want fewer management layers, Nexus in between... And on
> sequencing: at Amex we moved to SAFe only after the Scrum teams were
> stable — that's what made it stick. Happy to go deeper on any of these."

Nothing is invented — the content is Vikram's own answer, re-ordered so
the decision rule leads instead of trailing.

## 3. Knowledge-authoring template (required shape for `data/qa/*.md`)

Every Q&A entry — placeholder or real — must be authored in this shape.
The headline/detail split in the *source* is what lets the model reliably
reproduce the layering; do not free-write paragraphs in narrative order
and expect the system prompt alone to fix the structure at answer time.

```markdown
## Q: <the question as a client would actually ask it>

**Headline:** <the one-breath decision rule or direct answer — this is
almost verbatim what layer 1 above should say>

**Detail:**
- <point 1, with reasoning and a concrete example/name if available>
- <point 2, ...>
- <point 3, ...>

**Escalate if:** <the specific circumstance under which this question
should be deferred to Vikram instead of answered directly — omit only if
this topic is genuinely always safe to answer directly>
```

Keep questions phrased the way a client would actually ask them (not as a
textbook heading) — that's what the retrieval/matching at answer time is
actually working against.

## 4. Applying this to new knowledge (including the escalation-log flywheel)

Whenever real Vikram answers an escalated question (see
`docs/PIPELINE.md` Phase 5), the answer should be captured in this same
template and added to the corpus — not appended as a raw transcript. This
keeps the corpus internally consistent and means every new entry is
already in the shape the answer-style instruction expects.
