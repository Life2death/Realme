# Realme — Vikram's AI Advisor Clone

An AI clone / digital twin that can join real meetings (Zoom/Teams) on
Vikram's behalf, answer questions in his voice and reasoning style using
his own documented expertise, and escalate anything high-stakes back to
him.

> **If you're an AI agent opening this repo, read [`CLAUDE.md`](CLAUDE.md)
> first** — it has the intent, current phase, and rules of engagement in
> agent-consumable form.

## Why this exists

Vikram has deep expertise in cloud transformation, SEPA payments / ISO
20022, and large-scale IT delivery — and is getting invited onto calls
across every time zone (US, UK, Europe, Australia). One person cannot be
on every call, every hour. The goal is not a generic chatbot — it's a
**meeting-capable advisor**: it joins the call, listens, answers what it
confidently knows in Vikram's own words, and defers ("I'll take that back
to Vikram, you'll have an answer within 24 hours") on anything it
shouldn't guess at.

## Approach, in one paragraph

Validate cheaply and in order: prove the **brain** (LLM + knowledge base)
answers well in plain text before spending a dollar on voice; prove the
**voice** agent holds a conversation before wiring it into a real meeting;
prove it survives **real meetings** in audio before adding a video avatar.
Each stage has an explicit pass/fail gate — see
[`docs/PIPELINE.md`](docs/PIPELINE.md). This order exists specifically to
avoid months of engineering on a foundation ("does the knowledge base even
produce good answers?") that hasn't been checked yet.

## Repo map

- [`CLAUDE.md`](CLAUDE.md) — orientation for any AI agent working in this repo
- [`STATUS.md`](STATUS.md) — current phase, what's done, what's next
- [`docs/PIPELINE.md`](docs/PIPELINE.md) — the full phased plan, tools, gates, cost model
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — component/data-flow architecture
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — key decisions and what was ruled out, with reasons
- [`docs/PROMPT_DESIGN.md`](docs/PROMPT_DESIGN.md) — system prompt design, answer-style pattern, Q&A authoring template
- [`data/qa/generic-test-questions.md`](data/qa/generic-test-questions.md) — placeholder test corpus (see the warning in `CLAUDE.md` — this is not the final domain data)

## Tech stack

| Layer | Tool | Role |
|---|---|---|
| Brain | Anthropic Claude API | Reasoning + answers over the knowledge base |
| Voice | ElevenLabs (voice clone + Conversational AI agents) | Speech-to-text, TTS, turn-taking |
| Meeting bot | Recall.ai | Joins Zoom/Teams, streams audio/video in and out |
| Video avatar (later phase) | HeyGen (LiveAvatar) | Real-time talking-head video of Vikram |

## Status

In progress. See [`STATUS.md`](STATUS.md) for the current phase and gate.
