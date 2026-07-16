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

**Phase 1 — Brain validation, text-only.** No voice, no meeting bot, no
avatar yet. Goal: prove the LLM + knowledge base gives client-acceptable
answers before building anything on top of it. See `docs/PIPELINE.md` for
the full phase breakdown and gate criteria.

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

### What's next (in order — do not skip ahead)

1. Write the system prompt combining: identity/persona, the BLUF
   answer-style instruction (`docs/PROMPT_DESIGN.md`), and the
   escalation rule.
2. Load the placeholder Q&A into context (full-context approach, not
   RAG yet — see `docs/DECISIONS.md` for why) and run them through
   Claude in a plain chat/console — no voice, no meeting bot.
3. Score every answer: does it lead with the headline? Does the detail
   match the source Q&A? Does anything outside the given questions
   correctly trigger the escalation line instead of a confident guess?
4. **Gate 1** (see `docs/PIPELINE.md`): ≥80% of answers acceptable and
   escalation firing correctly on out-of-scope questions → move to
   Phase 2 (voice, no meetings). Below that, fix the prompt/data first —
   do not add voice or meeting infrastructure on a brain that hasn't
   passed this gate.
5. Once real SEPA/ISO 20022 documents are ready, replace/extend the
   placeholder corpus using the same Q&A template, and re-run Gate 1
   against the real domain before trusting any later-phase work
   (voice/meeting/video) that was built against placeholder data.

## Known open items

- Real subject-matter documents (SEPA/ISO 20022, cloud transformation
  case material) are not ready yet — timeline unknown. Placeholder data
  is being used so the pipeline itself isn't blocked on that.
- Only 7 of the intended 10 placeholder questions have been supplied
  (Q1, Q2, Q3, Q6, Q7, Q8, Q9). Q4, Q5, and Q10 are not yet defined.
- No voice, meeting-bot, or avatar integration exists yet — do not assume
  any of `docs/PIPELINE.md` Phase 2 onward has started.
