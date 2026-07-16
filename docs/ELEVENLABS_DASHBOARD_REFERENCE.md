# ElevenLabs dashboard — exact fields to fill in

A scannable field-by-field reference for Step 4 of `docs/VOICE_INTEGRATION.md`
(configuring the agent). Dashboard UIs change over time — if a label here
doesn't match what you see, look for the nearest equivalent (noted inline
where the docs were ambiguous) and tell me what you actually see so this
file can be corrected rather than left stale.

Confirmed against ElevenLabs' own documentation at the time this was
written; **not** confirmed against a live login (I don't have access to
your account). Treat this as "what to expect," verify as you go.

---

## Agent editor tabs

The agent editor has (at least) these tabs — confirmed names:

| Tab | What you'll touch |
|---|---|
| **Agent** | First message, system prompt, LLM selection |
| **Voice** | Which cloned voice the agent speaks with |
| **Knowledge Base** | **Skip this tab entirely** — see note below |
| **Analysis** | Evaluation criteria / data collection (not needed yet) |
| **Call history** | Where you'll review test-call transcripts afterward |

---

## 1. Create the agent

- Dashboard → **Agents** (or similar) → **Create new agent** / **+ New**.
- Choose **Blank template** if offered (not a pre-built persona template).
- Name it something identifiable, e.g. `Vikram AI Advisor — Phase 2 test`.

## 2. Voice tab

- Select the voice you cloned in Step 1 of `docs/VOICE_INTEGRATION.md`.
- Leave stability / similarity / speed at defaults for the first test —
  tune these *after* you've heard a baseline, not before.

## 3. Agent tab — First message

Field label: **First message**.

Enter something short and disclosed up front, e.g.:

```
Hi, this is Vikram's AI advisor — happy to help while Vikram's away from the keyboard.
```

This is spoken *before* your custom LLM is ever called, so the disclosure
here matters independently of the disclosure logic already in
`prompts/system-prompt.md`.

## 4. Agent tab — System prompt

Field label: **System prompt**.

**Do not paste the real system prompt here.** Enter a short stub instead:

```
See server/llm_proxy.py in the Realme repo — the real prompt and knowledge base are injected server-side by the custom LLM.
```

Why: `server/llm_proxy.py` ignores whatever system message ElevenLabs sends
and always substitutes `prompts/system-prompt.md` + `data/qa/*.md` (see
`docs/DECISIONS.md`). If you paste the real prompt here too, you now have
two copies that can silently drift apart — the whole problem this
architecture was built to avoid.

## 5. Agent tab — LLM selection → Custom LLM

Look for an **LLM** dropdown or section (documentation places it on the
right side of the Agent tab). Steps:

1. Open the **LLM** dropdown → select **Custom LLM**.
2. A configuration panel/modal opens with these fields:

| Field (as documented) | What to enter |
|---|---|
| **Server URL** | Your tunnel URL + the endpoint path: `https://<your-ngrok-subdomain>.ngrok-free.app/v1/chat/completions` |
| **Model ID** | `claude-sonnet-5` (or whatever `MODEL` is currently set to in `server/llm_proxy.py` — the proxy ignores this field's actual value and uses its own `MODEL` constant, but fill it in for clarity/logging on ElevenLabs' side) |
| **API key** | See below — this is a *secret*, not a plain text field |

3. **API key setup** (documented flow):
   - Click the dropdown under **API key**.
   - Select **Create new secret**.
   - Give it a recognizable name, e.g. `REALME_PROXY_SECRET` (the name is
     just a label in ElevenLabs' secret store — it does not need to match
     anything in your `.env`).
   - In the **value** field, paste the exact value of `PROXY_SHARED_SECRET`
     from your repo-root `.env`.
   - Click **Add secret**.
   - Select that secret from the dropdown so it's attached to this agent.

4. **If you see an additional "API type" / "response format" field**
   (some ElevenLabs surfaces expose this, others infer it from the URL
   path): choose **Chat Completions** — this is what `server/llm_proxy.py`
   implements (`POST /v1/chat/completions`), not the newer "Responses API"
   shape.

5. **If you see a "Request headers" field**: leave it empty. Auth is
   handled entirely via the API key/secret above, which ElevenLabs sends
   as a `Bearer` token in the `Authorization` header — exactly what
   `server/llm_proxy.py`'s auth check expects.

6. Close the LLM modal (often an **×** button), then **Publish** (or
   **Save**) the agent. Changes to LLM configuration typically don't take
   effect until published.

## 6. Knowledge Base tab

**Leave this empty. Do not upload anything here.**

The knowledge base already lives in `data/qa/*.md` and is injected by
`server/llm_proxy.py` on every request. Uploading a copy here would create
a second, different knowledge source ElevenLabs' own RAG might draw from
alongside (or instead of) what the proxy sends — exactly the
two-sources-of-truth problem this architecture avoids. See
`docs/DECISIONS.md`.

## 7. Testing

Look for a **Test AI agent** / **Test call** button (usually near the top
of the agent editor, or under a "Test" / preview panel). This opens an
in-browser voice call with the agent — use your microphone, ask questions
from `scripts/test_brain.py`'s `IN_SCOPE_QUESTIONS` / `TRAP_QUESTIONS`, and
follow the checklist in `docs/VOICE_INTEGRATION.md` Step 5.

Afterward, check the **Call history** tab for the transcript — useful for
catching things you missed live (mispronunciations, timing) and for the
same "review transcripts → improve the corpus" loop described in
`docs/PIPELINE.md` Phase 5, once you're further along.

---

## If something doesn't match

The dashboard is a moving target and this reference was built from
documentation, not a live account. If a field name, tab, or flow doesn't
match what you see:

1. Look for the nearest equivalent by *function* (e.g. any field that
   clearly means "point this agent at a server I host" is the Custom LLM
   URL field, regardless of its exact current label).
2. Tell me what you're actually seeing (a screenshot description or the
   exact label) and I'll correct this file so it stays accurate for next
   time — that's the point of keeping it in the repo instead of just
   telling you once in chat.
