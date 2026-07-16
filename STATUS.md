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
- **System prompt drafted** (`prompts/system-prompt.md`): identity/
  disclosure, the BLUF answer-style instruction, and the escalation rule.
- **Gate 1 test harness written** (`scripts/test_brain.py`): loads the
  system prompt + full `data/qa/*.md` corpus into one prompt-cached
  context; supports interactive chat (default) and a batch eval
  (`--eval`) that runs paraphrased in-scope questions plus out-of-scope
  "trap" questions and flags whether escalation fired. Setup in
  `scripts/requirements.txt` and `scripts/.env.example`.

### What's next (in order — do not skip ahead)

1. **Run Gate 1.** `pip install -r scripts/requirements.txt`, set
   `ANTHROPIC_API_KEY`, then `python scripts/test_brain.py --eval`.
   Score the in-scope answers by hand (does each lead with a headline?
   is the detail grounded in the KB?) and confirm the trap questions
   escalate instead of bluffing.
2. **Gate 1 criteria** (see `docs/PIPELINE.md`): ≥80% of in-scope answers
   acceptable AND ≥80% of traps correctly escalate → move to Phase 2
   (voice, no meetings). Below ~60% → fix the prompt/data (usually more
   `examples/`-style reasoning content) before building any voice or
   meeting layer on top.
3. Iterate on `prompts/system-prompt.md` and the corpus until Gate 1
   passes; note the result and any prompt changes back in this file.
4. Once real SEPA/ISO 20022 documents are ready, replace/extend the
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
