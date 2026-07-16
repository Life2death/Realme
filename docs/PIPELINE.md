# Pipeline — phased build plan

Principle: **validate cheaply, in order, with an explicit kill/continue
gate at every phase.** The single biggest risk to this project is not the
plumbing (voice, meeting bots, avatars) — it's whether the LLM, loaded
with Vikram's documented knowledge, actually answers like him. That is
tested first, in plain text, for a few dollars, before anything else is
built.

Time budget assumed: 12–16 hrs/day available, so phases move in days, not
weeks, once unblocked.

---

## Phase 0 — Setup

- Accounts: Anthropic, ElevenLabs, Recall.ai, HeyGen (HeyGen not paid/wired
  until Phase 4).
- Organize source documents into:
  - `core/` — best material: frameworks, migration runbooks, mapping
    guides, lessons learned.
  - `reference/` — specs, rulebooks (e.g. ISO 20022, EPC docs).
  - `examples/` — past real Q&A, emails, meeting notes where Vikram
    answered hard questions. **This folder is the highest-value one** —
    it captures *reasoning*, not just facts.
- Write an **eval set**: ~50 real questions across three tiers —
  factual, judgment, and "trap" questions (ones where a confident wrong
  answer would be worse than "let me check"). For each, note 2–3 bullets
  of what the real Vikram would say. This is what makes every later gate
  trustworthy — build it once, reuse it at every gate.

Status: superseded for the current iteration by the placeholder-data
approach in `STATUS.md` (real docs not ready yet; a placeholder question
set is used instead to test mechanics — see
`data/qa/generic-test-questions.md`).

---

## Phase 1 — The brain, text only

**No voice, no meetings, no avatar.** Just: does the LLM, loaded with the
knowledge base, answer like Vikram?

1. Prefer loading the full corpus directly into context (with prompt
   caching) over building a RAG/vector-search pipeline first — Claude's
   context window is large enough for most personal knowledge bases, and
   this skips a week of retrieval engineering. Only build real RAG later
   if the corpus doesn't fit or cost demands it.
2. Write the system prompt: persona, the answer-style pattern (headline
   first, then detail — see `docs/PROMPT_DESIGN.md`), and the escalation
   rule ("if high-stakes or not confident, defer to Vikram, log the
   question").
3. Test interface: the simplest thing that works — a console, a basic
   chat script. No UI investment yet.
4. Run the full eval set. Score each answer: acceptable as-is / right
   direction but needs polish / wrong or dangerously overconfident. Check
   separately that trap questions trigger escalation instead of a bluff.

### Gate 1

- ≥80% of answers acceptable, **and**
- ≥80% of trap/out-of-scope questions correctly escalate instead of
  guessing.
- **Below ~60%: stop and diagnose before continuing.** The fix is almost
  always more `examples/` material (real recorded reasoning), not more
  reference specs.

This gate should be reachable in a few days for a few dollars of API
spend. If the idea doesn't work, this is where that gets discovered —
cheaply.

---

## Phase 2 — Voice, no meetings yet

1. Clone the voice (ElevenLabs): 30+ minutes of clean recordings —
   reading source documents aloud works well (clean audio + natural
   domain vocabulary in the same pass).
2. Use ElevenLabs Conversational AI (Agents) as the voice shell — hosted
   STT + turn-taking + TTS, with the Phase 1 brain plugged in as the
   backing LLM/logic. Avoids hand-wiring STT→LLM→TTS latency at this
   stage.
3. Re-run a subset of the eval set **by voice**. New failure modes show
   up here: mispronounced domain acronyms, answers that read fine in text
   but run too long spoken, awkward interruption handling.
4. Tune: explicit spoken-length guidance in the prompt, pronunciation
   fixes via the TTS lexicon.

Soft gate: would a friendly former colleague find this a reasonable
conversation partner? If yes, continue.

---

## Phase 3 — Real meetings, audio-only

1. Wire Recall.ai: bot joins a meeting URL (Zoom **or** Teams — one API,
   this is why Recall.ai is the meeting-bot choice over HeyGen's native
   join, which is Zoom-only), streams audio/transcript out, streams the
   agent's voice back in via Output Media.
2. Always disclose: the bot identifies itself as "Vikram's AI Advisor" —
   never presents as the live human.
3. Add meeting-specific logic:
   - **Address detection** — respond when addressed by name or when a
     question is clearly in-scope, not to every utterance in a multi-party
     call.
   - **Escalation logging** — every deferred question goes to a reviewable
     list; Vikram's real answers get folded back into `examples/` (this is
     the improvement flywheel — treat it as a permanent process, not a
     one-time setup step).
   - **Full transcript capture** for review.
4. Test ladder, one rung at a time: solo test call → a friend
   role-playing a difficult client → a real friendly client, disclosed and
   free, explicitly asked to find where it breaks.

### Gate 2

- After 3+ real conversations: did participants get useful answers
  without Vikram in the room? Would a friendly pilot client actually pay
  for access?
- If yes → Phase 4 (video). If answers are good but the *meeting
  experience* is clunky (turn-taking, latency) — iterate here, that's a
  fixable engineering problem, not a reason to abandon.
- At this point there is already a sellable product: a 24/7 voice
  advisory line / meeting-attendance-by-voice offering.

---

## Phase 4 — Video (HeyGen)

1. Create the custom HeyGen avatar (a few minutes of on-camera video,
   good lighting, neutral background).
2. Two integration paths, build in this order:
   - **Path A — quick win, Zoom only:** HeyGen's native Interactive
     Avatar-in-Zoom integration, calendar-linked, supports simultaneous
     meetings, connects to a custom LLM backend (the Phase 1 brain).
   - **Path B — Teams + full control:** keep the Recall.ai pipeline from
     Phase 3; swap the output stage to brain → ElevenLabs voice → HeyGen
     LiveAvatar streaming (renders the talking face) → Recall.ai Output
     Media (streams video+audio into the call). Works on both Zoom and
     Teams, and is the architecture actually owned end-to-end.
3. Re-run the friendly-client test on video. Watch specifically for
   lip-sync latency and the "uncanny valley" reaction — some clients will
   genuinely prefer voice-only; keep both as offerings rather than
   assuming video is strictly better.

---

## Phase 5 — Commercial pilot

- 2–3 paying pilot clients on a discounted retainer (AI-advisor access +
  N hours of live Vikram per month).
- Daily loop: review every transcript → answer escalated questions →
  fold answers back into `examples/` → the clone measurably improves
  week over week. This loop does not stop — it is the ongoing operating
  model, not a phase that completes.
- Track: questions asked, % escalated, client follow-up/satisfaction.
  These numbers are the evidence for scaling further or stopping.

---

## Gate summary

| Gate | Phase | What's being tested | Kill criterion |
|---|---|---|---|
| Gate 1 | 1 → 2 | Brain answers acceptably; escalates correctly | <60% acceptable even after adding more `examples/` material |
| (soft) | 2 → 3 | Voice conversation is natural | Unfixably robotic/wrong in-domain (unlikely if Gate 1 passed) |
| Gate 2 | 3 → 4 | Survives real meetings; clients find it useful | Friendly pilot clients say they'd never use it (not just "it's rough") |
| (pilot) | 4 → 5 | Video adds value over audio-only | Purely cosmetic gap — audio product already stands alone commercially |

## Rough cost model (see chat history / `docs/DECISIONS.md` for detail)

- Text-only brain testing (Phase 1): a few dollars total.
- Voice-only, per meeting-hour: roughly $3–4 in usage costs (STT + LLM +
  TTS), once subscriptions are in place.
- Voice + video (HeyGen), per meeting-hour: roughly $9–15, dominated by
  avatar-rendering minutes.
- Fixed monthly subscriptions across the four tools: roughly $300–500/mo
  once past the free/trial tiers, covered by the first one or two paying
  pilot clients.
