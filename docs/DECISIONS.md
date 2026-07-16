# Decisions — what we chose, what we ruled out, and why

A running log. Add to this rather than rewriting history when a decision
changes — note the date/context of the change instead.

## Why not just use HeyGen end-to-end (avatar-only)?

HeyGen's straightforward avatar product caps at 30-minute pre-rendered
videos — the wrong tool category for this use case entirely (this isn't a
video-generation problem, it's a live-conversation problem). The relevant
HeyGen product is **LiveAvatar** (real-time interactive streaming), which
has no such cap and is billed per streaming minute instead. HeyGen is used
for the video layer only, in Phase 4, after audio is validated — not as
the whole pipeline.

## Why validate brain → voice → meetings → video, in that order?

The knowledge-base/reasoning quality is the part most likely to fail and
the cheapest to test. Testing it last (after building voice, meeting, and
avatar plumbing) would mean discovering a fundamental problem only after
weeks of engineering investment. Testing it first means a "this doesn't
work" verdict costs a few days and a few dollars, and every later phase
only starts once the phase before it has passed an explicit gate. See
`docs/PIPELINE.md` for the gates.

## Why full-context loading instead of RAG (retrieval-augmented generation),
at least initially?

Claude's context window (1M tokens on current models) covers most
personal/expert knowledge corpora whole. Loading the entire `core/` +
`examples/` corpus directly into a prompt-cached system prompt gets full
knowledge-base grounding on every answer with none of the retrieval
engineering (chunking, embeddings, vector store, retrieval tuning) that
RAG requires. RAG is deferred until/unless the real corpus genuinely
doesn't fit in context, or cost analysis says otherwise — it is not
assumed to be necessary by default.

## Why Recall.ai for the meeting bot, not HeyGen's native meeting join?

HeyGen's native "join a Zoom meeting" integration is Zoom-only. Recall.ai
exposes one bot API across Zoom, Microsoft Teams, Google Meet, and others
— and the target client base includes Teams-heavy calls (US/UK/Europe/
Australia enterprise clients). Recall.ai is the meeting-bot layer;
HeyGen's native Zoom path is kept as a fast/simple option (Phase 4, Path
A) specifically for Zoom-only scenarios, alongside — not instead of — the
Recall.ai-based path that also covers Teams.

## Why ElevenLabs Conversational AI for the voice shell in Phase 2/3,
rather than hand-wiring STT → LLM → TTS?

At the validation stage, the goal is to test whether the *conversation*
holds up, not to build production-grade real-time audio infrastructure.
ElevenLabs Agents bundles STT, turn-taking/interruption handling, and TTS
behind one API and accepts a custom backing LLM, which lets the Phase 1
brain (unchanged) drive it. Custom low-level audio pipeline engineering
is deferred unless a concrete limitation of the hosted product shows up
in testing.

## Why disclose the AI advisor rather than have it pass as the live human?

Two reasons, both treated as non-negotiable rather than a style
preference: (1) most enterprise clients' policies and several
jurisdictions require consent/disclosure for recording or AI participants
in meetings; discovery of an undisclosed clone would damage the exact
trust the offering depends on. (2) Disclosed, it's a stronger commercial
pitch on its own terms — "my AI handles triage and off-hours coverage,
I handle the hard calls" — rather than a deception that has to hold up
indefinitely.

## Why an explicit escalation rule instead of trying to make the brain
never wrong?

No knowledge base is complete, and regulated/technical domains (SEPA
payments compliance, ISO 20022, formal recommendations) have real cost to
a confident wrong answer. The system prompt treats "defer to Vikram" as a
correct, expected output for a defined class of questions (compliance
commitments, pricing, anything not confidently covered), not a fallback
failure mode. The escalation log is also the mechanism that improves the
knowledge base over time (see `docs/PIPELINE.md` Phase 5) — every
escalated question, once answered by the real Vikram, becomes new
`examples/` material.

## Why headline-first ("BLUF") answer structure?

Meetings are spoken, synchronous, and interruptible — a listener needs a
usable answer within the first ~20–30 seconds, and needs to be able to
interrupt after the headline and already have something actionable. A
document-style answer (context → reasoning → conclusion) reads fine as
text but performs badly spoken aloud in a live meeting. See
`docs/PROMPT_DESIGN.md` for the exact pattern and worked examples.

## Why store knowledge as structured Q&A (Headline / Detail / Escalate-if)
rather than free-form documents?

Models reproduce structure more reliably from examples than from
instructions alone. Storing the source knowledge already split into
headline and detail means the model doesn't have to *derive* the
BLUF layering at answer time — it's already shaped that way in the
source. This also gives a single consistent authoring template so new
knowledge (from the escalation-log flywheel, or from the eventual real
SEPA/ISO 20022 corpus) slots in the same way every time. See
`docs/PROMPT_DESIGN.md`.

## Why is the current `data/qa/` corpus a placeholder, and is that a
problem?

The real subject-matter documents (SEPA/ISO 20022 specs, cloud
transformation case material) were not ready at the time Phase 1 testing
started, and assembling them was expected to take longer than the rest of
the pipeline validation. Rather than block the entire project on document
collection, a placeholder corpus (delivery-leadership / interview-prep
content) is used to validate the *mechanics* — ingestion format,
answer-style layering, escalation triggering — independent of
subject-matter domain. This is a deliberate, temporary substitution, not a
scope change: see `STATUS.md` for what happens when the real corpus
arrives (same template, same Gate 1 re-run, against the real domain,
before trusting any phase built against placeholder data).

## Why a custom LLM proxy for ElevenLabs, instead of ElevenLabs' built-in Claude selection?

ElevenLabs' Conversational AI agents can run on a built-in Claude model
(their picker includes several Claude versions, though not always the
newest ones — check current availability) or call a self-hosted "custom
LLM" that speaks the standard OpenAI chat-completions format. We chose the
custom LLM route (`server/llm_proxy.py`) for three reasons: (1) it reuses
the exact system prompt + knowledge base that already passed Gate 1
(`scripts/brain.py`) instead of a second copy hand-pasted into ElevenLabs'
own system-prompt field, which would silently drift out of sync the moment
either copy is edited; (2) it lets us use whichever current Claude model we
want, independent of ElevenLabs' picker; (3) ElevenLabs' own knowledge-base
feature does its own RAG/chunking, which is a different retrieval design
than the full-context-loading decision already made above — the custom LLM
path keeps one retrieval design instead of two. The cost is running and
exposing a small proxy server, which is a few hours of work, not a
structural risk. See `docs/VOICE_INTEGRATION.md` for the full setup.

## Why the proxy ignores whatever system message ElevenLabs forwards

`server/llm_proxy.py` always substitutes `prompts/system-prompt.md` +
`data/qa/*.md` and drops any system-role message in the incoming request,
even though ElevenLabs' agent config has its own system-prompt field. This
is deliberate: if both the ElevenLabs dashboard field and the repo's real
prompt could each independently affect behavior, they will eventually say
different things and nobody will know which one actually ran. Keeping
exactly one source of truth (`scripts/brain.py`) means every phase — text
eval, voice, and eventually meetings — is provably running the same brain.

## Meeting-region choice for Recall.ai

Recall.ai signup is region-scoped (`us-west-2`, `eu-central-1`,
`ap-northeast-1`). `us-west-2` was chosen as a starting point. Revisit if
the actual client meeting mix skews heavily toward Australia/APAC, since
that affects latency for the bot's audio/video streaming, not just
signup convenience.
