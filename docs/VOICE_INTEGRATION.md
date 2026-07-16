# Voice integration (Phase 2) — ElevenLabs

This is the Phase 2 execution guide (see `docs/PIPELINE.md` Phase 2). No
meeting bot, no video — just: does the brain hold up as a real-time spoken
conversation?

## Architecture decision: custom LLM proxy, not ElevenLabs' built-in LLM picker

ElevenLabs' Conversational AI agents can run on one of their built-in LLM
choices (as of writing: Claude Opus 4.7, Sonnet 4.6/4.5/4, Haiku 4.5, plus
GPT/Gemini options — check their dashboard for the current list, since this
changes over time), **or** call a custom LLM endpoint you host yourself, as
long as it speaks the standard OpenAI chat-completions wire format.

**We use the custom LLM path.** Reasons (see `docs/DECISIONS.md` for the
full entry):

1. It reuses the **exact** system prompt + knowledge base that already
   passed Gate 1 (`scripts/brain.py`), rather than a second copy hand-pasted
   into ElevenLabs' own system-prompt field — which would silently drift
   out of sync the moment either copy is edited.
2. It lets us use whichever current Claude model we want, independent of
   which older Claude versions happen to be in ElevenLabs' picker at any
   given time.
3. ElevenLabs' own knowledge-base feature does its own RAG/chunking, which
   is a different retrieval design than the full-context-loading decision
   already made and validated (`docs/DECISIONS.md`). The custom LLM path
   keeps one retrieval design, not two.

The cost: we run and expose a small server (`server/llm_proxy.py`). That
server is already written, and already smoke-tested — see below.

## Components

| Component | What it is |
|---|---|
| `scripts/brain.py` | Shared brain logic (system prompt + KB + .env loading) — same code Gate 1 validated, used by both `scripts/test_brain.py` and `server/llm_proxy.py` |
| `server/llm_proxy.py` | FastAPI server exposing `POST /v1/chat/completions` (OpenAI-compatible) backed by `brain.py` + the Anthropic API |
| `server/test_proxy.py` | Standalone smoke test — hits the proxy directly, no ElevenLabs involved |
| ElevenLabs voice clone | Your cloned voice, created once in the ElevenLabs dashboard |
| ElevenLabs agent | The Conversational AI agent — handles STT, turn-taking, TTS; its "brain" is pointed at `server/llm_proxy.py` |
| Tunnel (ngrok or similar) | Exposes the local proxy at a public HTTPS URL ElevenLabs' cloud service can reach |

## Step 1 — Clone the voice

Dashboard: **Voices → Add voice → Instant Voice Clone** (or Professional
Voice Clone for higher fidelity if available on your plan).

- Upload 1–3+ minutes of clean audio at minimum; ElevenLabs' own guidance
  and our Phase 2 plan (`docs/PIPELINE.md`) both suggest ~30 minutes of
  clean recordings for a stronger clone if you have the time.
- Reading your own source documents aloud kills two birds: clean audio,
  and the model picks up your natural pronunciation of domain vocabulary
  (SEPA, ISO 20022, EBA, etc.) — useful once the real corpus replaces the
  placeholder.
- Note the resulting **voice ID** — you'll need it for the agent config.

## Step 2 — Run the proxy locally

```bash
pip install -r server/requirements.txt
```

Add a shared secret to your repo-root `.env` (a random string — this is
NOT your Anthropic key, it's a second secret that gates the proxy so a
stumbled-upon public URL can't run up your API bill):

```
PROXY_SHARED_SECRET=<a long random string>
```

Then start it:

```bash
python server/llm_proxy.py
```

You should see it log that it loaded the system prompt + knowledge base,
then confirm it's alive:

```bash
curl http://localhost:8000/healthz
```

**Before wiring anything to ElevenLabs**, smoke-test the proxy directly:

```bash
python server/test_proxy.py "Give me the quick version of your role."
```

This should stream back a properly BLUF-formatted answer, identical in
substance to what `scripts/test_brain.py` produces — because it's the same
brain. If this step doesn't work, nothing downstream will either; fix it
here first.

## Step 3 — Expose the proxy publicly

ElevenLabs' cloud service needs to reach your proxy over the public
internet. For this validation phase, a tunnel is the fastest path (no
deployment, no hosting cost) — e.g. [ngrok](https://ngrok.com):

```bash
ngrok http 8000
```

Ngrok will print a public HTTPS URL (e.g. `https://abcd1234.ngrok-free.app`).
Confirm it works before going further:

```bash
curl https://abcd1234.ngrok-free.app/healthz
```

Once this direction is confirmed (Phase 2 gate, below) and you're moving
toward Phase 3/real client pilots, replace the tunnel with a small always-on
deployment (Render, Fly.io, a cheap VPS — anything that can run a FastAPI
app) so the proxy doesn't depend on your laptop staying on and the tunnel
staying open. Not needed yet for validation.

## Step 4 — Configure the ElevenLabs agent

Dashboard: **create a new agent** (blank template), then:

- **Voice tab**: select the voice ID from Step 1.
- **Agent tab → LLM settings**: choose **Custom LLM**, and set:
  - **URL**: `https://<your-tunnel-url>/v1/chat/completions`
  - **API key**: the same value as `PROXY_SHARED_SECRET` in your `.env`
    (ElevenLabs stores this as a secret and sends it back as a Bearer
    token on every request — this is exactly what `server/llm_proxy.py`
    checks).
  - **API type**: `chat_completions` (OpenAI-compatible — what the proxy
    implements).
- **Agent tab → System prompt**: leave this minimal or put a one-line
  placeholder like `"See server/llm_proxy.py — the real prompt is
  injected server-side."` **Do not** paste the real system prompt here —
  the proxy ignores whatever ElevenLabs sends as a system message and
  always substitutes `prompts/system-prompt.md` + `data/qa/*.md`
  (see the module docstring in `server/llm_proxy.py`). Keeping this field
  empty/stubbed avoids the two-copies-drifting-apart problem entirely.
- **Agent tab → First message**: something like *"Hi, this is Vikram's AI
  advisor — happy to help while Vikram's away from the keyboard."* This
  is spoken before your custom LLM is even called, so keep it short and
  make the disclosure explicit here too, not just in the system prompt.
- **Knowledge base tab**: leave empty. The knowledge base already lives
  in `data/qa/*.md` and is injected by the proxy — a second copy here
  would duplicate (and eventually diverge from) the real one.

## Step 5 — Test

Dashboard: **Test AI agent** (or the embedded widget). Ask a subset of the
same questions from `scripts/test_brain.py`'s `IN_SCOPE_QUESTIONS` and
`TRAP_QUESTIONS` — but **by voice this time**. Listen specifically for:

- **Mispronunciations** of domain acronyms/names (SEPA, ISO 20022, EBA,
  DRISHTI, LTIMindtree, etc.) — fixable via ElevenLabs' pronunciation
  dictionary / phoneme tagging once you find them.
- **Answers that read fine in text but run too long spoken** — the
  headline should land in ~15–30 seconds; if it's dragging, tighten
  `prompts/system-prompt.md`'s answer-style instruction further.
- **Turn-taking / interruption handling** — ElevenLabs' agent handles this
  natively, but confirm it feels natural when you interrupt mid-answer,
  per the system prompt's instruction to answer only the interrupted
  thread rather than restarting.
- **Escalation still firing correctly** — ask a couple of the trap
  questions by voice; confirm the spoken answer still declines instead of
  bluffing.

## Phase 2 gate (soft gate, per `docs/PIPELINE.md`)

Would a friendly former colleague find this a reasonable conversation
partner? If yes — move to Phase 3 (real meetings, via Recall.ai). If the
*content* is right but the *voice experience* is clunky (latency,
interruption handling), that's an iteration item here, not a reason to
abandon — see `docs/PIPELINE.md` Phase 2 for the full framing.

## Known limitations of this setup (intentional, for now)

- The proxy runs on your laptop behind a tunnel — fine for validation,
  not for a real client pilot (Phase 3+ needs a stable always-on
  deployment; see Step 3).
- `server/llm_proxy.py` ignores conversation-level nuances an ElevenLabs
  system message might otherwise carry (e.g. dynamic variables ElevenLabs
  supports for personalization) — out of scope until Phase 2 validation
  shows a real need for it.
- No streaming-token-level latency optimization has been done yet (e.g.
  sentence-chunked TTS handoff) — first get it working, then tune it if
  the felt latency is a problem in testing.
