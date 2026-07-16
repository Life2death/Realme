# CLAUDE.md — Read this first

This file exists so that any AI agent (Claude, or otherwise) that opens this
repository can understand what it is, why it exists, and what to do next
without needing the human's full chat history repeated to it.

## What this project is

**Realme** is a project to build Vikram's **AI clone / digital twin** — a
voice (and eventually video) agent that can:

1. Join real Zoom/Teams meetings on Vikram's behalf,
2. Answer client questions in his voice, in his style, using his own
   documented knowledge and experience,
3. Escalate to the real Vikram when a question is high-stakes or outside
   what the knowledge base covers.

The motivation: Vikram has deep expertise (cloud transformation, SEPA
payments / ISO 20022, IT service delivery, large-program leadership at
Citi/Amex/Dell-scale accounts) and is being invited to calls across every
time zone (US, UK, Europe, Australia). He cannot be on every call at once.
The goal is not a chatbot FAQ — it's a **meeting-capable advisor** that
sounds like him, reasons like him, and knows when to say "let me take that
back to Vikram."

**This is explicitly not** a generic customer-support bot, not a marketing
gimmick, and it must never impersonate Vikram without disclosure — every
deployment discloses "this is Vikram's AI advisor," never pretends to be
the live human.

## Current phase

See [`STATUS.md`](STATUS.md) for the live status. As of the last update:
Gate 1 has passed (against placeholder data) and the project is moving
into **Phase 2 (voice, no meetings yet)** — wiring the Gate-1-validated
brain into an ElevenLabs Conversational AI agent. Read `STATUS.md` before
assuming any later phase (meetings, video) has started.

## How the repo is organized

| Path | What's in it |
|---|---|
| `README.md` | Human-facing project overview |
| `STATUS.md` | Current phase, what's done, what's next (**check this first**) |
| `docs/PIPELINE.md` | The full phased build plan, gates, and kill criteria |
| `docs/ARCHITECTURE.md` | Technical architecture — components and data flow |
| `docs/DECISIONS.md` | Why we chose this approach; what we ruled out and why |
| `docs/PROMPT_DESIGN.md` | How to write the system prompt and answer style (BLUF pattern) |
| `docs/VOICE_INTEGRATION.md` | Phase 2 setup guide: ElevenLabs voice clone + agent + proxy |
| `docs/ELEVENLABS_DASHBOARD_REFERENCE.md` | Field-by-field ElevenLabs dashboard reference (exact tabs/labels/values) |
| `prompts/system-prompt.md` | The brain's system prompt (identity, answer style, escalation rule) |
| `scripts/brain.py` | **Single source of truth** for the brain — loads the system prompt + `data/qa/*.md`. Used by both `scripts/test_brain.py` (Phase 1) and `server/llm_proxy.py` (Phase 2). Never duplicate this logic elsewhere. |
| `scripts/test_brain.py` | Phase 1 Gate 1 test harness (interactive + `--eval` batch mode) |
| `server/llm_proxy.py` | Phase 2 voice proxy — OpenAI-compatible endpoint backed by `brain.py`, for ElevenLabs' Custom LLM integration |
| `server/test_proxy.py` | Standalone smoke test for the proxy (no ElevenLabs involved) |
| `data/qa/generic-test-questions.md` | **Placeholder/test** Q&A corpus — see warning below |

## ⚠️ Important: the current data is NOT the real knowledge base

`data/qa/generic-test-questions.md` contains 10 Q&A pairs about Vikram's
**delivery-leadership / interview-prep persona** (Citi, Amex, Dell delivery
management). This is **stand-in test data**, used only to validate the
*mechanics* of the pipeline (ingestion format, answer-style layering,
escalation logic) while the real subject-matter corpus (SEPA / ISO 20022 /
cloud transformation documents) is still being assembled.

**Do not treat this data as the final domain the clone should specialize
in.** When the real corpus arrives, it replaces/extends this file under
the same `data/` structure and the same Q&A template — see
`docs/PROMPT_DESIGN.md` for the exact format.

## What an agent picking this up should do

1. Read `STATUS.md` to find the current phase and the next unchecked task.
2. Read `docs/PIPELINE.md` to see the gate that phase must pass before
   moving to the next one — **do not skip ahead to voice/meeting/video
   work if the text-only brain hasn't passed Gate 1.**
3. Read `docs/PROMPT_DESIGN.md` before writing or editing any system
   prompt — it documents the required answer shape (headline-first, then
   detail) and the escalation rule that must always be present.
4. If asked to add new knowledge-base content, follow the Q&A template in
   `docs/PROMPT_DESIGN.md` exactly (Headline / Detail / Escalate-if) — do
   not free-write documents in a different shape; the layering only works
   if the source data is already structured that way.
5. Update `STATUS.md` when a phase gate is passed or a decision changes.
