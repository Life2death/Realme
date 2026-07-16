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

**Phase 2 — Voice, no meetings yet.** Gate 1 (Phase 1, text-only brain)
passed against placeholder data. The Phase 2 proxy is built and locally
smoke-tested; ElevenLabs voice clone + agent configuration (dashboard
steps) have not been done yet. See `docs/PIPELINE.md` for the full phase
breakdown and `docs/VOICE_INTEGRATION.md` for the Phase 2 execution guide.

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

- **Phase 2 voice proxy built and locally verified**
  (`server/llm_proxy.py`): an OpenAI-compatible `/v1/chat/completions`
  endpoint backed by the exact same brain module (`scripts/brain.py`,
  refactored out of `test_brain.py` so Phase 1 and Phase 2 can never
  silently drift apart). Verified locally: health check responds, a real
  streamed answer round-tripped correctly and came back in the expected
  BLUF shape, and the shared-secret auth guard correctly rejects requests
  with a missing or wrong `Authorization` header (important since this
  will eventually sit behind a public tunnel URL). Not yet tested through
  an actual ElevenLabs agent.
- Architecture decision recorded in `docs/DECISIONS.md`: use ElevenLabs'
  **custom LLM** integration rather than its built-in Claude picker, so
  Phase 2 runs on the identical Gate-1-validated prompt/KB instead of a
  second hand-pasted copy, and isn't limited to whichever older Claude
  versions ElevenLabs has added to their picker.
- **ElevenLabs dashboard field reference written**
  (`docs/ELEVENLABS_DASHBOARD_REFERENCE.md`): exact tab names and field
  labels for the agent editor (Agent / Voice / Knowledge Base / Analysis /
  Call history), the Custom LLM setup flow (Server URL, Model ID, the
  secret-based API key field), and explicit "leave this empty" notes for
  the system-prompt and knowledge-base fields, cross-referenced from
  `docs/VOICE_INTEGRATION.md` Step 4. Built from ElevenLabs' own
  documentation, not a live login — flagged as something to correct in
  the repo if the actual dashboard differs, rather than a one-off answer
  in chat.

### What's next (in order — do not skip ahead)

1. **Finish Phase 2 per `docs/VOICE_INTEGRATION.md`** (field-level detail
   in `docs/ELEVENLABS_DASHBOARD_REFERENCE.md`):
   - Clone the voice in the ElevenLabs dashboard (Step 1).
   - Run the proxy + expose it via a tunnel (ngrok or similar) (Steps 2–3
     — code is ready, this is just running it and confirming the public
     URL responds).
   - Create the ElevenLabs agent and point its Custom LLM at the tunnel
     URL, with the system prompt field left as a stub (not a real copy)
     and the knowledge-base tab left empty (Step 4).
   - Test by voice — re-run a subset of `scripts/test_brain.py`'s
     questions, listening for mispronunciations, answers that run too
     long spoken, and whether escalation still fires correctly (Step 5).
2. **Phase 2 soft gate** (`docs/PIPELINE.md`): would a friendly former
   colleague find this a reasonable conversation partner? If yes → Phase
   3 (real meetings via Recall.ai). If content is right but the voice
   *experience* is clunky, iterate here — not a reason to abandon.
3. Once real SEPA/ISO 20022 documents are ready, replace/extend the
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
- The proxy currently runs on a laptop behind a tunnel — fine for
  validation, not for a real client pilot. A stable always-on deployment
  is a Phase 3+ item, not needed yet (see `docs/VOICE_INTEGRATION.md` §
  Known limitations).
- No meeting-bot or avatar integration exists yet — Phase 3/4 have not
  started.
