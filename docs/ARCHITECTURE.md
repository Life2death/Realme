# Architecture

This describes the target end-state architecture (Phase 4). Earlier
phases are subsets of this — see `docs/PIPELINE.md` for what's actually
wired up at each stage. Check `STATUS.md` before assuming any component
below exists yet.

## Components

| Component | Tool | Responsibility |
|---|---|---|
| Meeting bot | Recall.ai | Joins Zoom/Teams meetings; streams participant audio/transcript out; streams the agent's audio+video back in (Output Media) |
| Speech-to-text | Deepgram (via Recall.ai or direct) | Real-time transcription of meeting audio |
| Brain | Anthropic Claude API | Reasoning over the knowledge base; produces the answer text; owns the escalation decision |
| Knowledge base | Markdown Q&A corpus (`data/qa/`), loaded via prompt-cached context (Phase 1); may move to a retrieval/RAG layer later if the corpus outgrows context | Source of truth for what the clone knows and how it should reason |
| Voice | ElevenLabs (voice clone + Conversational AI) | Text-to-speech in Vikram's cloned voice; handles turn-taking/interruptions when used as the Phase 2/3 conversational shell |
| Video avatar (Phase 4+) | HeyGen LiveAvatar | Renders a real-time talking-head video of Vikram synced to the voice output |

## Data flow (target end-state, Phase 4 "Path B" — Teams + full control)

```
Meeting (Zoom/Teams)
    │  audio in
    ▼
Recall.ai bot ──► Speech-to-text (Deepgram) ──► transcript
                                                     │
                                                     ▼
                                        Claude (brain) + knowledge base
                                                     │
                                        answer text OR escalation event
                                                     │
                                                     ▼
                                          ElevenLabs (voice synthesis)
                                                     │
                                                     ▼
                                        HeyGen LiveAvatar (video render)
                                                     │
                                                     ▼
                                      Recall.ai Output Media ──► back into meeting
```

Earlier phases drop components from the bottom up:

- **Phase 1**: brain + knowledge base only, plain text in/out, no other
  component exists.
- **Phase 2**: brain + ElevenLabs Conversational AI (which subsumes its
  own STT/TTS/turn-taking) — no meeting bot, tested via a direct
  call/widget.
- **Phase 3**: adds Recall.ai as the meeting-bot layer, audio only — no
  HeyGen in the loop.
- **Phase 4**: adds HeyGen as described above; Path A (HeyGen's native
  Zoom integration) is a simpler variant that bypasses Recall.ai and the
  manual voice-to-avatar wiring entirely, at the cost of being Zoom-only.

## Escalation path

The brain does not attempt to answer everything. The system prompt
(`docs/PROMPT_DESIGN.md`) defines an explicit escalation rule: high-stakes
or low-confidence questions produce a spoken deferral ("I'll take that
back to Vikram...") plus a logged event. That log is the input to the
Phase 3+ daily review loop described in `docs/PIPELINE.md` Phase 5 — this
is how the knowledge base improves over time, not a one-off step.

## Disclosure requirement (non-negotiable, applies at every phase with a
real meeting participant)

The agent identifies itself as "Vikram's AI Advisor" in every meeting. It
never presents itself as, or allows itself to be mistaken for, the live
human. This applies from the first real (non-solo) test call onward.
