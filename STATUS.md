# Status

Last updated: see latest commit date on this file.

## Environment

All four accounts are created and ready:

- [x] Anthropic (Claude API)
- [x] ElevenLabs (voice clone + Conversational AI)
- [x] Recall.ai (meeting bot API — region: `us-west-2`, chosen for now;
      revisit if Australia-based meetings dominate — see
      `docs/DECISIONS.md`)
- [x] HeyGen (held for Phase 4 — video avatar; not wired up yet)

## Current phase

**Phase 1 — Brain validation, text-only — GATE 1 PASSED (placeholder
data).** No voice, no meeting bot, no avatar yet. Ready to begin Phase 2
(voice). See `docs/PIPELINE.md` for the full phase breakdown and gate
criteria.

### What's done

- Pipeline plan and phase gates defined (`docs/PIPELINE.md`).
- Answer-style pattern defined: headline (direct decision rule) spoken
  first, detailed explanation after — see `docs/PROMPT_DESIGN.md`.
- A **placeholder/test** Q&A corpus is in place
  (`data/qa/generic-test-questions.md`) — 7 of an intended 10 Q&A pairs
  about Vikram's delivery-leadership background (Citi/Amex/Dell), used
  only to test the pipeline mechanics while the real SEPA/ISO 20022
  subject-matter corpus is still being assembled. **Do not confuse this
  with the final domain.**
- **System prompt drafted** (`prompts/system-prompt.md`): identity/
  disclosure, the BLUF answer-style instruction, and the escalation rule.
- **Gate 1 test harness written** (`scripts/test_brain.py`): loads the
  system prompt + full `data/qa/*.md` corpus into one prompt-cached
  context; supports interactive chat (default) and a batch eval
  (`--eval`) that runs paraphrased in-scope questions plus out-of-scope
  "trap" questions and flags whether escalation fired. Also auto-loads a
  `.env` file at the repo root if present (no need to `export` the key
  manually) — see `scripts/.env.example`.
- **Gate 1 run and PASSED**, against the placeholder corpus:
  - 7/7 in-scope answers acceptable (100%, target ≥80%) — each led with a
    headline, detail was grounded in real KB facts/numbers, no invented
    content.
  - 5/5 traps correctly declined/escalated on manual read (100%, target
    ≥80%). Notably: the "which Citi stream / SLA numbers" trap correctly
    refused to invent the detail the KB itself flags as
    needs-personalization, and the day-rate / audit-guarantee / Delta
    Lake partitioning traps all deferred to Vikram instead of bluffing.
  - Minor tuning note (not a blocker): the disclosure line ("You're
    speaking with Vikram's AI advisor...") fired on every escalated
    answer rather than only when asked/assumed — fine for now, revisit
    if it reads as repetitive once in a live Phase 3 meeting.

### What's next (in order — do not skip ahead)

1. **Begin Phase 2 (voice, no meetings yet)** per `docs/PIPELINE.md`:
   clone the voice in ElevenLabs, stand up their Conversational AI agent
   with this same brain (system prompt + KB) as the backing logic, and
   re-run a subset of the eval questions **by voice** — watch for
   mispronounced domain acronyms and answers that run too long spoken.
2. Once real SEPA/ISO 20022 documents are ready, replace/extend the
   placeholder corpus using the same Q&A template, and re-run Gate 1
   against the real domain before trusting any later-phase work
   (voice/meeting/video) that was built against placeholder data. Phase
   2 work can proceed on placeholder data in the meantime — the goal
   right now is validating the voice *mechanics*, not the final domain
   answers.

## Known open items

- Real subject-matter documents (SEPA/ISO 20022, cloud transformation
  case material) are not ready yet — timeline unknown. Placeholder data
  is being used so the pipeline itself isn't blocked on that.
- Only 7 of the intended 10 placeholder questions have been supplied
  (Q1, Q2, Q3, Q6, Q7, Q8, Q9). Q4, Q5, and Q10 are not yet defined.
- No voice, meeting-bot, or avatar integration exists yet — Phase 2 has
  not started (Gate 1 passing unblocks it, but nothing has been built).
