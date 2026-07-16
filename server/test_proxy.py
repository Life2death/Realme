#!/usr/bin/env python3
"""
Smoke test for server/llm_proxy.py — hits the proxy directly (no ElevenLabs
involved) to confirm the OpenAI-compatible streaming contract works before
spending any time wiring it into a real ElevenLabs agent.

Run the proxy first in one terminal:
    python server/llm_proxy.py

Then in another terminal:
    python server/test_proxy.py "Give me the quick version of your role."
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import brain  # noqa: E402

PROXY_URL = "http://localhost:8000/v1/chat/completions"


def main() -> None:
    question = " ".join(sys.argv[1:]) or "Give me the quick version of your role."
    shared_secret = brain.require_env(
        "PROXY_SHARED_SECRET",
        "Set it in the repo-root .env — same value the proxy itself reads.",
    )

    print(f"POST {PROXY_URL}")
    print(f"Q: {question}\n")

    response = requests.post(
        PROXY_URL,
        headers={"Authorization": f"Bearer {shared_secret}"},
        json={
            "model": "custom",
            "messages": [{"role": "user", "content": question}],
            "stream": True,
        },
        stream=True,
        timeout=60,
    )
    response.raise_for_status()

    print("advisor > ", end="", flush=True)
    for line in response.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue
        payload = line[len("data: "):]
        if payload == "[DONE]":
            break
        chunk = json.loads(payload)
        delta = chunk["choices"][0]["delta"].get("content")
        if delta:
            print(delta, end="", flush=True)
    print("\n")


if __name__ == "__main__":
    main()
