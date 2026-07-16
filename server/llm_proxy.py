#!/usr/bin/env python3
"""
Phase 2 voice proxy: an OpenAI-compatible chat-completions endpoint backed
by the exact Gate-1-validated brain (scripts/brain.py).

Why this exists (see docs/VOICE_INTEGRATION.md for the full rationale):
ElevenLabs' Conversational AI agent can either use one of its own built-in
LLM choices, or call a "custom LLM" you host yourself, as long as it speaks
the standard OpenAI chat-completions wire format (this is what ElevenLabs'
agent "api_type: chat_completions" custom-LLM option expects). We use the
custom-LLM path so that:

  1. The voice agent runs on the SAME system prompt + knowledge base that
     already passed Gate 1 — not a second copy hand-pasted into ElevenLabs'
     own system-prompt field, which would silently drift out of sync.
  2. We can use whatever current Claude model we want (e.g. claude-sonnet-5),
     not just whichever older Claude versions ElevenLabs has added to their
     own model picker.

This server IGNORES any system-role message ElevenLabs forwards and always
substitutes the real system prompt + knowledge base from brain.py. Only the
user/assistant turns from the incoming conversation are kept.

Run it:
    pip install -r server/requirements.txt
    python server/llm_proxy.py
    # then expose it publicly for ElevenLabs to reach, e.g.:
    #   ngrok http 8000
    # and point the ElevenLabs agent's Custom LLM URL at the ngrok URL + /v1

See docs/VOICE_INTEGRATION.md for the full setup (voice clone, agent config,
tunnel, testing).
"""

from __future__ import annotations

import json
import sys
import time
import uuid
from pathlib import Path
from typing import AsyncIterator

# scripts/brain.py is the single source of truth for the brain (system
# prompt + knowledge base + .env loading) — reuse it rather than duplicating
# any of that logic here. See scripts/brain.py's own docstring.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import brain  # noqa: E402

import anthropic  # noqa: E402
from fastapi import FastAPI, Request  # noqa: E402
from fastapi.responses import StreamingResponse, JSONResponse  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# claude-sonnet-5 over claude-opus-4-8 here: this endpoint sits on the
# critical path of a live voice conversation, where response latency is
# directly felt by whoever's talking. Sonnet is materially faster and
# cheaper; re-run scripts/test_brain.py --eval with MODEL swapped to
# claude-opus-4-8 if you want to compare answer quality before committing.
MODEL = "claude-sonnet-5"
MAX_TOKENS = 2048

anthropic_key = brain.require_env(
    "ANTHROPIC_API_KEY",
    "Set it in the repo-root .env (see scripts/.env.example) before "
    "starting the proxy.",
)
anthropic_client = anthropic.Anthropic(api_key=anthropic_key)

# Shared secret the proxy checks on every request, so a stumbled-upon public
# ngrok URL can't be used to run up your Anthropic bill. Set the SAME value
# as the ElevenLabs agent's Custom LLM "API key" field (ElevenLabs sends it
# back to you as a Bearer token — see docs/VOICE_INTEGRATION.md).
PROXY_SHARED_SECRET = brain.require_env(
    "PROXY_SHARED_SECRET",
    "Set it in the repo-root .env to any random string, then paste the "
    "same value into the ElevenLabs agent's Custom LLM API key field.",
)

PORT = 8000

app = FastAPI(title="Realme voice-proxy (Claude brain, OpenAI-compatible)")

# Loaded once at startup, not per-request: this is the whole point of prompt
# caching (see docs/DECISIONS.md) — every conversation turn reuses the same
# cached system-prompt + knowledge-base prefix.
SYSTEM_BLOCKS = brain.load_system_blocks()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_auth(request: Request) -> bool:
    auth_header = request.headers.get("authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()
    return token == PROXY_SHARED_SECRET


def _incoming_to_anthropic_messages(openai_messages: list[dict]) -> list[dict]:
    """Convert an OpenAI-style messages array to Anthropic's shape.

    Drops any system-role entries — ElevenLabs may forward its own agent
    system prompt here, but we deliberately always use brain.py's tested
    prompt instead (see module docstring). Only user/assistant turns pass
    through.
    """
    converted = []
    for msg in openai_messages:
        role = msg.get("role")
        if role not in ("user", "assistant"):
            continue
        converted.append({"role": role, "content": msg.get("content", "")})
    if not converted or converted[0]["role"] != "user":
        # Anthropic requires the first message to be from the user. If the
        # incoming history is empty or opens with an assistant turn (e.g.
        # ElevenLabs' configured first_message), prepend a harmless opener
        # so the request is valid rather than erroring.
        converted.insert(0, {"role": "user", "content": "(conversation start)"})
    return converted


def _sse_chunk(request_id: str, created: int, delta_text: str | None, finish_reason: str | None) -> str:
    """Format one OpenAI-compatible streaming chunk."""
    payload = {
        "id": request_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": MODEL,
        "choices": [
            {
                "index": 0,
                "delta": ({"content": delta_text} if delta_text is not None else {}),
                "finish_reason": finish_reason,
            }
        ],
    }
    return f"data: {json.dumps(payload)}\n\n"


async def _stream_answer(messages: list[dict]) -> AsyncIterator[str]:
    request_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())

    with anthropic_client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_BLOCKS,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield _sse_chunk(request_id, created, text, None)

    yield _sse_chunk(request_id, created, None, "stop")
    yield "data: [DONE]\n\n"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/healthz")
def healthz():
    """Plain liveness check — hit this first when wiring up the tunnel."""
    return {"status": "ok", "model": MODEL}


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    if not _check_auth(request):
        return JSONResponse(status_code=401, content={"error": "invalid or missing API key"})

    body = await request.json()
    openai_messages = body.get("messages", [])
    stream_requested = body.get("stream", False)
    anthropic_messages = _incoming_to_anthropic_messages(openai_messages)

    if stream_requested:
        return StreamingResponse(
            _stream_answer(anthropic_messages),
            media_type="text/event-stream",
        )

    # Non-streaming fallback (mainly useful for manual curl testing — the
    # real ElevenLabs integration should always request stream=true for
    # acceptable voice latency).
    text_parts: list[str] = []
    with anthropic_client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_BLOCKS,
        messages=anthropic_messages,
    ) as stream:
        for chunk in stream.text_stream:
            text_parts.append(chunk)
    answer = "".join(text_parts)

    return JSONResponse(
        content={
            "id": f"chatcmpl-{uuid.uuid4().hex}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": MODEL,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": answer},
                    "finish_reason": "stop",
                }
            ],
        }
    )


if __name__ == "__main__":
    import uvicorn

    print(f"Starting voice proxy on http://0.0.0.0:{PORT}  (model={MODEL})", file=sys.stderr)
    print("Health check: GET /healthz", file=sys.stderr)
    print("ElevenLabs custom-LLM endpoint: POST /v1/chat/completions", file=sys.stderr)
    uvicorn.run(app, host="0.0.0.0", port=PORT)
